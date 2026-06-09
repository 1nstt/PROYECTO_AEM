import numpy as np

class BlackHole:
    def __init__(self, vector_binario, fitness):
        self.vector_binario = vector_binario.copy()
        self.fitness = fitness
        self.trial = 0  # contador de estancamiento para la radiación de hawking

class BBH_MMKP_UDP_Optimizer:
    def __init__(self, datos_instancia, num_estrellas=25, max_iter=2000, pr=0.1, prob_slingshot=0.15, 
                 radio_horizonte=10, delta_incremento=0.005, distancia_max_fusion=2,
                 limite_evaporacion=35, delta_enfriamiento=0.005):
        
        self.datos = datos_instancia
        self.num_estrellas = num_estrellas
        self.max_iter = max_iter
        self.pr = pr
        self.prob_slingshot = prob_slingshot
        
        # dimensiones del hipercubo binario
        self.total_items = datos_instancia['r_ij_k'].shape[0]
        self.n_grupos = datos_instancia['n']
        self.m_restricciones = datos_instancia['m']
        self.mapeo_grupos = datos_instancia['mapeo_grupos']
        
        # parámetros gravitatorios y térmicos unificados
        self.radio_horizonte_inicial = radio_horizonte # Guardamos el radio base
        self.radio_horizonte = radio_horizonte         # Este cambiará dinámicamente
        self.delta_incremento = delta_incremento
        self.distancia_max_fusion = distancia_max_fusion
        self.limite_evaporacion = limite_evaporacion
        self.delta_enfriamiento = delta_enfriamiento
        
        self.f_crit = self.calcular_fcrit_inicial()
        self.lista_bh = []
        self.poblacion = self.inicializar_poblacion_estrellas()
        
        # Guardián del Óptimo histórico absoluto del universo
        self.master_bh = None

    def calcular_fcrit_inicial(self):
        """ calcula el umbral inicial basado en el beneficio promedio de los grupos """
        beneficios = self.datos['V_ij']
        return float((np.sum(beneficios) / beneficios.size) * self.n_grupos)

    class Estrella:
        def __init__(self, vector, fitness):
            self.vector_binario = vector.copy()
            self.fitness = fitness

    def generar_solucion_estructurada_paper(self):
        """
        Genera un único vector binario viable siguiendo estrictamente la 
        estrategia initializeSolution del paper MABC.
        """
        N_subproblemas = 4
        dh_intercambios = 10
        todos_los_grupos = list(self.mapeo_grupos.keys())
        grupos_por_subproblema = self.n_grupos // N_subproblemas
        b_p_k = self.datos['b_k'] / N_subproblemas

        vec = np.zeros(self.total_items, dtype=int)
        grupos_mezclados = todos_los_grupos.copy()
        np.random.shuffle(grupos_mezclados)
        
        for s_idx in range(N_subproblemas):
            inicio = s_idx * grupos_por_subproblema
            fin = inicio + grupos_por_subproblema
            sub_grupos = grupos_mezclados[inicio:fin]
            
            # --- CONSTRUCCIÓN CODICIOSA ---
            for grupo in sub_grupos:
                indices_items = self.mapeo_grupos[grupo]
                recursos_items = self.datos['r_ij_k'][indices_items]
                consumos_relativos = np.sum(recursos_items / self.datos['b_k'], axis=1)
                mejor_item_local = indices_items[np.argmin(consumos_relativos)]
                vec[mejor_item_local] = 1

            # --- FASE DE INTERCAMBIOS CONTROLADOS ---
            d = 0
            intentos_max = 50
            intentos = 0
            while d < dh_intercambios and intentos < intentos_max:
                intentos += 1
                grupo_azar = np.random.choice(sub_grupos)
                indices_items = self.mapeo_grupos[grupo_azar]
                item_activo = indices_items[np.where(vec[indices_items] == 1)[0][0]]
                opciones_disponibles = [idx for idx in indices_items if idx != item_activo]
                item_candidato = np.random.choice(opciones_disponibles)
                
                vec[item_activo] = 0
                vec[item_candidato] = 1
                
                items_seleccionados_subproblema = []
                for g in sub_grupos:
                    idx_sel = self.mapeo_grupos[g][np.where(vec[self.mapeo_grupos[g]] == 1)[0][0]]
                    items_seleccionados_subproblema.append(idx_sel)
                
                consumo_subproblema = np.sum(self.datos['r_ij_k'][items_seleccionados_subproblema], axis=0)
                
                if np.all(consumo_subproblema <= b_p_k):
                    d += 1
                else:
                    vec[item_activo] = 1
                    vec[item_candidato] = 0
        return vec

    def inicializar_poblacion_estrellas(self):
        """ Inicializa la población llamando al constructor del paper """
        poblacion_inicial = []
        for _ in range(self.num_estrellas):
            vec = self.generar_solucion_estructurada_paper()
            fit = self.evaluar_fitness_mochila(vec)
            poblacion_inicial.append(self.Estrella(vec, fit))
        return poblacion_inicial

    def reparar_estructura_mmkp(self, vec):
        nuevo_vec = vec.copy()
        for grupo, indices in self.mapeo_grupos.items():
            if np.sum(nuevo_vec[indices]) != 1:
                nuevo_vec[indices] = 0
                elegido = np.random.choice(indices)
                nuevo_vec[elegido] = 1
        return nuevo_vec

    def evaluar_fitness_mochila(self, vec):
        consumos = np.dot(vec, self.datos['r_ij_k'])
        if np.any(consumos > self.datos['b_k']):
            return 0.0
        return float(np.dot(vec, self.datos['V_ij']))

    def calcular_distancia_hamming(self, vec1, vec2):
        return int(np.sum(vec1 != vec2))

    def optimizar(self):
        print(f"\n[bucle] comenzando simulación espacial con {self.num_estrellas} estrellas...")
        print(f"[bucle] umbral crítico inicial (f_crit): {self.f_crit:.2f}")
        
        for iteracion in range(self.max_iter):
            # --- HORIZONTE DE EVENTOS ADAPTATIVO ---
            progreso = iteracion / self.max_iter
            self.radio_horizonte = max(2, int(self.radio_horizonte_inicial * (1.0 - progreso)))

            conteo_evaporaciones = 0
            conteo_slingshot = 0
            conteo_colisiones = 0
            
            # --- FASE 1: REGISTRO DE AGUJEROS NEGROS CON UMBRAL ESCALABLE ---
            for s in self.poblacion:
                ya_es_bh = any(self.calcular_distancia_hamming(s.vector_binario, bh.vector_binario) == 0 for bh in self.lista_bh)
                
                if s.fitness >= self.f_crit and not ya_es_bh:
                    nuevo_bh = BlackHole(vector_binario=s.vector_binario.copy(), fitness=s.fitness)
                    self.lista_bh.append(nuevo_bh)
                    self.f_crit *= (1 + self.delta_incremento)
            
            if len(self.lista_bh) > 0:
                lider_actual = max(self.lista_bh, key=lambda x: x.fitness)
                if self.master_bh is None or lider_actual.fitness > self.master_bh.fitness:
                    self.master_bh = BlackHole(vector_binario=lider_actual.vector_binario.copy(), fitness=lider_actual.fitness)

            # --- FASE 2: MOVIMIENTO DE ESTRELLAS Y EVENTOS GRAVITATORIOS ---
            if len(self.lista_bh) == 0 and self.master_bh is not None:
                self.lista_bh.append(BlackHole(vector_binario=self.master_bh.vector_binario.copy(), fitness=self.master_bh.fitness))

            vectores_bh_activos = [bh.vector_binario for bh in self.lista_bh]
            
            for s in self.poblacion:
                es_bh_activo = any(self.calcular_distancia_hamming(s.vector_binario, v) == 0 for v in vectores_bh_activos)
                if es_bh_activo:
                    continue
                
                if len(self.lista_bh) > 0:
                    distancias = [self.calcular_distancia_hamming(s.vector_binario, bh.vector_binario) for bh in self.lista_bh]
                    bh_asignado = self.lista_bh[np.argmin(distancias)]
                    
                    # --- SOLUCIÓN INTEGRADA: ATRACCIÓN POR BLOQUES DE GRUPO ---
                    for grupo, indices in self.mapeo_grupos.items():
                        if np.random.rand() < self.pr:
                            # Apagamos los ítems de la estrella en este grupo
                            s.vector_binario[indices] = 0
                            # Encontramos la posición exacta del ítem activo en el Agujero Negro y lo copiamos
                            idx_activo_bh = indices[np.where(bh_asignado.vector_binario[indices] == 1)[0][0]]
                            s.vector_binario[idx_activo_bh] = 1
                    
                    # Estructura garantizada al 100%: Evaluamos directamente el peso de la mochila
                    s.fitness = self.evaluar_fitness_mochila(s.vector_binario)
                    
                    # Horizonte de Eventos y Slingshot
                    if self.calcular_distancia_hamming(s.vector_binario, bh_asignado.vector_binario) < self.radio_horizonte:
                        if np.random.rand() < self.prob_slingshot:
                            for d in range(self.total_items):
                                if s.vector_binario[d] != bh_asignado.vector_binario[d]:
                                    s.vector_binario[d] = 1 - s.vector_binario[d]
                            
                            # El slingshot invierte bits sueltos, por lo que aquí SÍ es mandatorio reparar
                            s.vector_binario = self.reparar_estructura_mmkp(s.vector_binario)
                            s.fitness = self.evaluar_fitness_mochila(s.vector_binario)
                            conteo_slingshot += 1
                            
                            if s.fitness == 0:
                                s.vector_binario = self.generar_solucion_estructurada_paper()
                                s.fitness = self.evaluar_fitness_mochila(s.vector_binario)
                        else:
                            s.vector_binario = self.generar_solucion_estructurada_paper()
                            s.fitness = self.evaluar_fitness_mochila(s.vector_binario)
                else:
                    mascara_mutacion_alta = np.random.rand(self.total_items) < 0.5
                    s.vector_binario[mascara_mutacion_alta] = 1 - s.vector_binario[mascara_mutacion_alta]
                    s.vector_binario = self.reparar_estructura_mmkp(s.vector_binario)
                    s.fitness = self.evaluar_fitness_mochila(s.vector_binario)

            # --- FASE 3: MOVIMIENTO DE AUTO-REFINAMIENTO DE LOS AGUJEROS NEGROS ---
            for bh in self.lista_bh:
                bh_intento_vec = bh.vector_binario.copy()
                grupo_azar = np.random.choice(list(self.mapeo_grupos.keys()))
                indices_del_grupo = self.mapeo_grupos[grupo_azar]
                
                bh_intento_vec[indices_del_grupo] = 0
                objeto_elegido = np.random.choice(indices_del_grupo)
                bh_intento_vec[objeto_elegido] = 1
                
                bh_intento_vec = self.reparar_estructura_mmkp(bh_intento_vec)
                fit_intento = self.evaluar_fitness_mochila(bh_intento_vec)
                
                if fit_intento > bh.fitness:
                    bh.vector_binario = bh_intento_vec.copy()
                    bh.fitness = fit_intento
                    bh.trial = 0
                else:
                    bh.trial += 1
            
            if len(self.lista_bh) > 0:
                lider_actual = max(self.lista_bh, key=lambda x: x.fitness)
                if self.master_bh is None or lider_actual.fitness > self.master_bh.fitness:
                    self.master_bh = BlackHole(vector_binario=lider_actual.vector_binario.copy(), fitness=lider_actual.fitness)

            # --- FASE 4: EVAPORACIÓN POR RADIACIÓN DE HAWKING ---
            indices_para_evaporar = []
            if len(self.lista_bh) > 0:
                mejor_bh_actual = max(self.lista_bh, key=lambda x: x.fitness)
                
                for idx, bh in enumerate(self.lista_bh):
                    if bh == mejor_bh_actual or (self.master_bh is not None and bh.fitness == self.master_bh.fitness):
                        continue
                        
                    if bh.trial >= self.limite_evaporacion:
                        indices_para_evaporar.append(idx)
                        self.f_crit *= (1 - self.delta_enfriamiento)
                        conteo_evaporaciones += 1
            
            if indices_para_evaporar:
                self.lista_bh = [bh for idx, bh in enumerate(self.lista_bh) if idx not in indices_para_evaporar]

            # --- FASE 5: FUSIÓN POR PROXIMIDAD EXTREMA ---
            if len(self.lista_bh) > 1:
                mejor_bh_actual = max(self.lista_bh, key=lambda x: x.fitness)
                marcados_para_eliminar = set()
                
                for i in range(len(self.lista_bh)):
                    for j in range(i + 1, len(self.lista_bh)):
                        if i in marcados_para_eliminar or j in marcados_para_eliminar:
                            continue
                        
                        dist = self.calcular_distancia_hamming(self.lista_bh[i].vector_binario, self.lista_bh[j].vector_binario)
                        if dist <= self.distancia_max_fusion:
                            conteo_colisiones += 1
                            
                            if self.lista_bh[i] == mejor_bh_actual:
                                marcados_para_eliminar.add(j)
                            elif self.lista_bh[j] == mejor_bh_actual:
                                marcados_para_eliminar.add(i)
                            else:
                                if self.lista_bh[i].fitness >= self.lista_bh[j].fitness:
                                    marcados_para_eliminar.add(j)
                                else:
                                    marcados_para_eliminar.add(i)
                
                self.lista_bh = [bh for idx, bh in enumerate(self.lista_bh) if idx not in marcados_para_eliminar]

            if len(self.lista_bh) == 0 and self.master_bh is not None:
                self.lista_bh.append(BlackHole(vector_binario=self.master_bh.vector_binario.copy(), fitness=self.master_bh.fitness))

            # --- reporte por consola ---
            if iteracion % 50 == 0 or iteracion == self.max_iter - 1:
                mejor_f_actual = max([bh.fitness for bh in self.lista_bh]) if len(self.lista_bh) > 0 else 0.0
                print(f"[iter {iteracion:04d}] "
                      f"mej_Z: {mejor_f_actual:<7.1f} | "
                      f"act_BHs: {len(self.lista_bh):<2d} | "
                      f"rad_horizonte: {self.radio_horizonte:<2d} | " 
                      f"evap_hawking: {conteo_evaporaciones:<2d} | "
                      f"slingshot: {conteo_slingshot:<2d} | "
                      f"colisiones: {conteo_colisiones:<2d} | "
                      f"f_crit: {self.f_crit:.1f}")

        return max(self.lista_bh, key=lambda x: x.fitness) if len(self.lista_bh) > 0 else self.master_bh
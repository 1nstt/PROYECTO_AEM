import numpy as np
import os
import time
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt

class BlackHole:
    def __init__(self, vector_binario, fitness):
        self.vector_binario = vector_binario.copy()
        self.fitness = fitness
        self.trial = 0  # contador de estancamiento para la radiación de hawking

class BBH_MMKP_UDP_Optimizer:
    def __init__(self, datos_instancia, num_estrellas=25, max_iter=2000, pr=0.1, prob_slingshot=0.15, 
                 radio_horizonte=10, delta_incremento=0.005, distancia_max_fusion=2,
                 limite_evaporacion=35, delta_enfriamiento=0.005, extra_fcrit_inicial=0.0):
        
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
        self.radio_horizonte_inicial = radio_horizonte 
        self.radio_horizonte = radio_horizonte         
        self.delta_incremento = delta_incremento
        self.distancia_max_fusion = distancia_max_fusion
        self.limite_evaporacion = limite_evaporacion
        self.delta_enfriamiento = delta_enfriamiento
        
        self.extra_fcrit_inicial = extra_fcrit_inicial
        self.f_crit = self.calcular_fcrit_inicial()
        
        self.lista_bh = []
        self.poblacion = self.inicializar_poblacion_estrellas()
        self.master_bh = None

        # =================================================================
        # NUEVOS CONTADORES Y TRAZADORES DE TELEMETRÍA AVANZADA
        # =================================================================
        self.max_bhs_simultaneos = 0
        self.total_bhs_creados_historico = 0  # Acumulador absoluto de colapsos estelares
        self.total_slingshots_gatillados = 0
        self.slingshots_exitosos_fitness = 0
        self.slingshots_factibles = 0
        self.slingshots_infactibles_respawn = 0

        # Arrays históricos para curvas de convergencia (Métricas por generación/tiempo)
        self.historial_iteraciones = []
        self.historial_mejor_Z = []
        self.historial_tiempo_cpu = []
        self.historial_bhs_activos = []
        self.historial_f_crit = []
        # =================================================================

    def calcular_fcrit_inicial(self):
        """ calcula el umbral inicial basado en el beneficio promedio de los grupos y el delta manual """
        beneficios = self.datos['V_ij']
        base_fcrit = float((np.sum(beneficios) / beneficios.size) * self.n_grupos)
        return base_fcrit + self.extra_fcrit_inicial

    class Estrella:
        def __init__(self, vector, fitness):
            self.vector_binario = vector.copy()
            self.fitness = fitness

    def generar_solucion_estructurada_paper(self):
        """ Genera un único vector binario viable siguiendo initializeSolution de MABC """
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
            
            for grupo in sub_grupos:
                indices_items = self.mapeo_grupos[grupo]
                recursos_items = self.datos['r_ij_k'][indices_items]
                consumos_relativos = np.sum(recursos_items / self.datos['b_k'], axis=1)
                mejor_item_local = indices_items[np.argmin(consumos_relativos)]
                vec[mejor_item_local] = 1

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

    def initialize_poblacion_estrellas(self):
        return self.inicializar_poblacion_estrellas()

    def inicializar_poblacion_estrellas(self):
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
        return np.count_nonzero(vec1 != vec2)

    def optimizar(self):
        print(f"\n[bucle] comenzando simulación espacial con {self.num_estrellas} estrellas...")
        print(f"[bucle] umbral crítico inicial (f_crit): {self.f_crit:.2f}")
        
        cronometro_inicio = time.time()

        for iteracion in range(self.max_iter):
            # =================================================================
            # --- HORIZONTE DE EVENTOS ADAPTATIVO (SELECCIONAR PERFIL) ---
            # =================================================================
            progreso = iteracion / self.max_iter
            
            # OPCIÓN A: PERFIL LINEAL
            # self.radio_horizonte = max(2, int(self.radio_horizonte_inicial * (1.0 - progreso)))
            
            # OPCIÓN B: PERFIL EXPONENCIAL
            self.radio_horizonte = max(2, int(self.radio_horizonte_inicial * np.exp(-3.0 * progreso)))
            
            # OPCIÓN C: PERFIL SIGMOIDAL 
            # factor_sigmoide = 1.0 / (1.0 + np.exp(10.0 * (progreso - 0.5)))
            # self.radio_horizonte = max(2, int(2 + (self.radio_horizonte_inicial - 2) * factor_sigmoide))
            # =================================================================
            
            conteo_evaporaciones = 0
            conteo_slingshot = 0
            conteo_colisiones = 0
            
            num_bhs_actuales = len(self.lista_bh)
            if num_bhs_actuales > 0:
                matriz_bh = np.array([bh.vector_binario for bh in self.lista_bh])
            else:
                matriz_bh = None

            # --- FASE 1: REGISTRO DE AGUJEROS NEGROS CON UMBRAL ESCALABLE ---
            for s in self.poblacion:
                if s.fitness >= self.f_crit:
                    if matriz_bh is not None:
                        ya_es_bh = np.any(np.all(matriz_bh == s.vector_binario, axis=1))
                    else:
                        ya_es_bh = False
                    
                    if not ya_es_bh:
                        nuevo_bh = BlackHole(vector_binario=s.vector_binario.copy(), fitness=s.fitness)
                        self.lista_bh.append(nuevo_bh)
                        self.total_bhs_creados_historico += 1 # Contador absoluto incremental
                        self.f_crit *= (1 + self.delta_incremento)
                        if matriz_bh is not None:
                            matriz_bh = np.vstack([matriz_bh, s.vector_binario])
                        else:
                            matriz_bh = np.array([s.vector_binario])
            
            if len(self.lista_bh) > self.max_bhs_simultaneos:
                self.max_bhs_simultaneos = len(self.lista_bh)
            
            if len(self.lista_bh) > 0:
                lider_actual = max(self.lista_bh, key=lambda x: x.fitness)
                if self.master_bh is None or lider_actual.fitness > self.master_bh.fitness:
                    self.master_bh = BlackHole(vector_binario=lider_actual.vector_binario.copy(), fitness=lider_actual.fitness)
            
            if self.master_bh is not None:
                self.f_crit = min(self.f_crit, self.master_bh.fitness)

            # --- FASE 2: MOVIMIENTO DE ESTRELLAS Y EVENTOS GRAVITATORIOS ---
            if len(self.lista_bh) == 0 and self.master_bh is not None:
                self.lista_bh.append(BlackHole(vector_binario=self.master_bh.vector_binario.copy(), fitness=self.master_bh.fitness))
                matriz_bh = np.array([self.master_bh.vector_binario])

            if len(self.lista_bh) > 0:
                matriz_bh = np.array([bh.vector_binario for bh in self.lista_bh])
                
                for s in self.poblacion:
                    if np.any(np.all(matriz_bh == s.vector_binario, axis=1)):
                        continue
                    
                    distancias = np.count_nonzero(matriz_bh != s.vector_binario, axis=1)
                    idx_asignado = np.argmin(distancias)
                    bh_asignado = self.lista_bh[idx_asignado]
                    dist_al_asignado = distancias[idx_asignado]
                    
                    # Atracción limpia por bloques de grupo (PROTEGIDA)
                    for grupo, indices in self.mapeo_grupos.items():
                        if np.random.rand() < self.pr:
                            s.vector_binario[indices] = 0
                            
                            # Encontrar qué ítem tiene activo el BH en este grupo
                            items_activos_bh = np.where(bh_asignado.vector_binario[indices] == 1)[0]
                            
                            if items_activos_bh.size > 0:
                                # Comportamiento Normal: Copia al Agujero Negro
                                idx_activo_bh = indices[items_activos_bh[0]]
                                s.vector_binario[idx_activo_bh] = 1
                            else:
                                # Red de Seguridad: Si el BH está desestructurado, elige al azar
                                idx_azar = np.random.choice(indices)
                                s.vector_binario[idx_azar] = 1
                    
                    s.fitness = self.evaluar_fitness_mochila(s.vector_binario)
                    
                    # --- SLINGSHOT GUIADO POR ELITISMO INTEGRAL ---
                    if dist_al_asignado < self.radio_horizonte:
                        if np.random.rand() < self.prob_slingshot:
                            fitness_previo_estrella = s.fitness
                            todos_los_grupos = list(self.mapeo_grupos.keys())
                            np.random.shuffle(todos_los_grupos)
                            
                            limite_conservacion = max(1, int(self.n_grupos * 0.30))
                            grupos_a_conservar = set(todos_los_grupos[:limite_conservacion])
                            
                            for grupo, indices in self.mapeo_grupos.items():
                                s.vector_binario[indices] = 0 
                                
                                if grupo in grupos_a_conservar:
                                    items_activos_bh = np.where(bh_asignado.vector_binario[indices] == 1)[0]
                                    if items_activos_bh.size > 0:
                                        idx_activo_bh = indices[items_activos_bh[0]]
                                        s.vector_binario[idx_activo_bh] = 1
                                    else:
                                        idx_azar = np.random.choice(indices)
                                        s.vector_binario[idx_azar] = 1
                                else:
                                    nueva_opcion_azar = np.random.choice(indices)
                                    s.vector_binario[nueva_opcion_azar] = 1
                            
                            s.fitness = self.evaluar_fitness_mochila(s.vector_binario)
                            conteo_slingshot += 1
                            self.total_slingshots_gatillados += 1
                            
                            if s.fitness > fitness_previo_estrella:
                                self.slingshots_exitosos_fitness += 1
                            
                            if s.fitness > 0:
                                self.slingshots_factibles += 1
                            else:
                                self.slingshots_infactibles_respawn += 1
                                s.vector_binario = self.generar_solucion_estructurada_paper()
                                s.fitness = self.evaluar_fitness_mochila(s.vector_binario)
                        else:
                            s.vector_binario = self.generar_solucion_estructurada_paper()
                            s.fitness = self.evaluar_fitness_mochila(s.vector_binario)
            else:
                for s in self.poblacion:
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
                master_fitness = self.master_bh.fitness if self.master_bh is not None else -1
                
                for idx, bh in enumerate(self.lista_bh):
                    if bh.trial < self.limite_evaporacion:
                        continue
                    if bh == mejor_bh_actual or bh.fitness == master_fitness:
                        continue
                        
                    indices_para_evaporar.append(idx)
                    self.f_crit *= (1 - self.delta_enfriamiento)
                    conteo_evaporaciones += 1
            
            if indices_para_evaporar:
                self.lista_bh = [bh for idx, bh in enumerate(self.lista_bh) if idx not in indices_para_evaporar]

            # --- FASE 5: FUSIÓN POR PROXIMIDAD EXTREMA ---
            num_bhs_final = len(self.lista_bh)
            if num_bhs_final > 1:
                mejor_bh_actual = max(self.lista_bh, key=lambda x: x.fitness)
                marcados_para_eliminar = set()
                matriz_bh_final = np.array([bh.vector_binario for bh in self.lista_bh])
                
                for i in range(num_bhs_final):
                    if i in marcados_para_eliminar:
                        continue
                    
                    distancias_colision = np.count_nonzero(matriz_bh_final[i] != matriz_bh_final[i+1:], axis=1)
                    
                    for local_idx, dist in enumerate(distancias_colision):
                        j = i + 1 + local_idx
                        if j in marcados_para_eliminar:
                            continue
                            
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
                
                if marcados_para_eliminar:
                    self.lista_bh = [bh for idx, bh in enumerate(self.lista_bh) if idx not in marcados_para_eliminar]

            if len(self.lista_bh) == 0 and self.master_bh is not None:
                self.lista_bh.append(BlackHole(vector_binario=self.master_bh.vector_binario.copy(), fitness=self.master_bh.fitness))

            # =================================================================
            # REGISTRO HISTÓRICO DE TELEMETRÍA (PASO A PASO)
            # =================================================================
            tiempo_actual_cpu = time.time() - cronometro_inicio
            mejor_f_actual = max([bh.fitness for bh in self.lista_bh]) if len(self.lista_bh) > 0 else 0.0
            if self.master_bh is not None and self.master_bh.fitness > mejor_f_actual:
                mejor_f_actual = self.master_bh.fitness

            self.historial_iteraciones.append(iteracion)
            self.historial_mejor_Z.append(mejor_f_actual)
            self.historial_tiempo_cpu.append(tiempo_actual_cpu)
            self.historial_bhs_activos.append(len(self.lista_bh))
            self.historial_f_crit.append(self.f_crit)
            # =================================================================

            # --- reporte por consola ---
            if iteracion % 50 == 0 or iteracion == self.max_iter - 1:
                print(f"[iter {iteracion:04d}] "
                      f"mej_Z: {mejor_f_actual:<7.1f} | "
                      f"act_BHs: {len(self.lista_bh):<2d} | "
                      f"rad_horizonte: {self.radio_horizonte:<2d} | " 
                      f"evap_hawking: {conteo_evaporaciones:<2d} | "
                      f"slingshot: {conteo_slingshot:<2d} | "
                      f"colisiones: {conteo_colisiones:<2d} | "
                      f"f_crit: {self.f_crit:.1f}")

        return max(self.lista_bh, key=lambda x: x.fitness) if len(self.lista_bh) > 0 else self.master_bh

    # =================================================================
    # MÉTODO: GENERACIÓN DE REPORTES Y GRÁFICOS ESTRUCTURADOS (CON VECTOR COMPLETO)
    # =================================================================
    def generar_reportes_y_graficos(self, nombre_instancia, texto_consola):
        """
        Crea de forma automatizada la jerarquía de almacenamiento bajo la raíz:
        proyecto meta / ejecuciones / {nombre_instancia} / EJECUCION_{fecha_hora} /
        Guarda el log de consola, los gráficos y el vector binario completo de ceros y unos.
        """
        # 1. Encontrar la raíz real subiendo un nivel desde donde está clasebase.py
        ruta_clasebase = Path(__file__).resolve()  
        ruta_raiz_proyecto = ruta_clasebase.parent.parent  
        
        fecha_hora_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Configurar la ruta de la carpeta de destino
        carpeta_raiz = ruta_raiz_proyecto / "ejecuciones" / nombre_instancia / f"EJECUCION_{fecha_hora_str}"
        carpeta_raiz.mkdir(parents=True, exist_ok=True)
        
        # 2. Extraer el vector binario de la mejor solución absoluta encontrada
        mejor_bh = max(self.lista_bh, key=lambda x: x.fitness) if len(self.lista_bh) > 0 else self.master_bh
        vector_completo_str = "\n▶ CONFIGURACIÓN DEL VECTOR BINARIO ÓPTIMO COMPLETO (X_ij):\n"
        if mejor_bh is not None:
            vector_completo_str += f"{mejor_bh.vector_binario.tolist()}\n"
        else:
            vector_completo_str += "[] (No se encontraron soluciones factibles)\n"
        
        # Unificar el texto que venía de afuera con el volcado del vector binario
        reporte_final_con_vector = texto_consola + vector_completo_str + "=========================================================\n"
        
        # 3. Persistir archivo log_ejecucion.txt en el disco
        archivo_txt = carpeta_raiz / "log_ejecucion.txt"
        with open(archivo_txt, "w", encoding="utf-8") as f:
            f.write(reporte_final_con_vector)
        
        # 4. Gráfico 1: Solución vs Generación (Iteraciones)
        plt.figure(figsize=(10, 5))
        plt.plot(self.historial_iteraciones, self.historial_mejor_Z, color="blue", linewidth=2, label="Mejor Z")
        plt.plot(self.historial_iteraciones, self.historial_f_crit, color="red", linestyle="--", alpha=0.7, label="Umbral f_crit")
        plt.title(f"Curva de Convergencia por Generación - Instancia {nombre_instancia}")
        plt.xlabel("Iteración / Generación")
        plt.ylabel("Función Objetivo (Z)")
        plt.grid(True, linestyle=":")
        plt.legend()
        plt.savefig(carpeta_raiz / "convergencia_por_generacion.png", dpi=300, bbox_inches="tight")
        plt.close()
        
        # 5. Gráfico 2: Solución vs Tiempo de Ejecución (CPU)
        plt.figure(figsize=(10, 5))
        plt.plot(self.historial_tiempo_cpu, self.historial_mejor_Z, color="green", linewidth=2, label="Mejor Z")
        plt.title(f"Evolución del Rendimiento por Tiempo de CPU - Instancia {nombre_instancia}")
        plt.xlabel("Tiempo total consumido por la CPU (Segundos)")
        plt.ylabel("Función Objetivo (Z)")
        plt.grid(True, linestyle=":")
        plt.legend()
        plt.savefig(carpeta_raiz / "convergencia_por_tiempo.png", dpi=300, bbox_inches="tight")
        plt.close()

        # 6. Gráfico 3: Dinámica Poblacional Estelar (BHs Activos)
        plt.figure(figsize=(10, 4))
        plt.plot(self.historial_iteraciones, self.historial_bhs_activos, color="purple", linewidth=1.5, label="BHs Activos simultáneos")
        plt.title(f"Evolución Dinámica Poblacional de Atractores - Instancia {nombre_instancia}")
        plt.xlabel("Iteración")
        plt.ylabel("Cantidad de Agujeros Negros")
        plt.grid(True, linestyle=":")
        plt.legend()
        plt.savefig(carpeta_raiz / "dinamica_poblacional.png", dpi=300, bbox_inches="tight")
        plt.close()
        
        # 7. Desplegar el reporte unificado con el vector por la pantalla de la terminal
        print(vector_completo_str)
        print("=========================================================")
        print(f"[sistema] Reportes, gráficos y vector guardados exitosamente en:\n ➔ {carpeta_raiz.resolve()}")
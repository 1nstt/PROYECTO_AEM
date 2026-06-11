1.  INICIO
2.  Definir Parámetros: Num_Estrellas, Max_Iter, Pr, Prob_Slingshot, Delta_Incremento, Distancia_Max_Fusion, Limite_Evaporacion, Delta_Enfriamiento, N_Subproblemas, Dh_Intercambios
3.  Calcular F_crit inicial: F_crit = (Suma_Total_Beneficios / Total_Objetos) * Total_Grupos
4.  Inicializar Lista_BH como una lista vacía, Master_BH = NULO

5.  // --- SUBPROCESO: GENERAR_SOLUCION_ESTRUCTURADA_MABC ---
6.  SUBPROCESO Generar_Solucion_Estructurada_MABC():
7.      Inicializar Vector_Solucion con ceros
8.      Dividir aleatoriamente los n grupos del problema en N_Subproblemas
9.      Fraccionar la capacidad de recursos totales: b_p^k = b^k / N_Subproblemas
10.     PARA cada subproblema asignado:
11.         // Paso 1: Construcción Codiciosa Inicial
12.         PARA cada grupo en el subproblema:
13.             Seleccionar el objeto con el menor consumo de recursos relativos
14.             Activar objeto en Vector_Solucion
15.         FIN PARA
16.         // Paso 2: Diversificación por Intercambios de Hamming Controlados
17.         d = 0
18.         MIENTRAS (d < Dh_Intercambios) Y (Intentos < Max_Intentos) HACER:
19.             Seleccionar un grupo al azar del subproblema
20.             Intercambiar el objeto activo por un objeto inactivo al azar
21.             SI (Consumo_Acumulado_Subproblema <= b_p^k) ENTONCES:
22.                 d = d + 1 // Intercambio exitoso y factible
23.             SINO:
24.                 Deshacer el intercambio inmediatamente // Mantener viabilidad
25.             FIN SI
26.         FIN MIENTRAS
27.     FIN PARA
28.     DEVOLVER Vector_Solucion
29. FIN SUBPROCESO

30. // --- INICIALIZACIÓN DE LA POBLACIÓN DE ESTRELLA ---
31. PARA cada estrella S desde 1 hasta Num_Estrellas:
32.     S(Vector) = Generar_Solucion_Estructurada_MABC() 
33.     Evaluar_Fitness_Mochila(S) 
34. FIN PARA

35. // Bucle Principal de Simulación Cósmica
36. MIENTRAS (Iteración < Max_Iter) HACER:
36.5     // --- HORIZONTE DE EVENTOS ADAPTATIVO ---
36.6     Progreso = Iteración / Max_Iter
36.7     Radio_Horizonte = MAX(2, PARTE_ENTERA(Radio_Horizonte_Inicial * (1.0 - Progreso)))

37.     // --- FASE 1: REGISTRO DE AGUJEROS NEGROS CON UMBRAL ESCALABLE ---
38.     PARA cada estrella S de la población:
39.         ya_es_bh = Comprobar_Si_Existe_Clon_En_Lista(S, Lista_BH)
40.         SI (Fitness(S) >= F_crit) Y (ya_es_bh == FALSO) ENTONCES:
41.             Registrar S en Lista_BH 
42.             Contador_Estancamiento(S) = 0
43.             F_crit = F_crit * (1 + Delta_Incremento)
44.         FIN SI
45.     FIN PARA

45.1    // --- GUARDAR MASTER_BH Y CONFIGURAR TOPE MÁXIMO DE F_CRIT ---
45.2    SI (Longitud(Lista_BH) > 0) ENTONCES:
45.3        Lider_Actual = Encontrar_BH_Con_Maximo_Fitness(Lista_BH)
45.4        SI (Master_BH == NULO) Ó (Lider_Actual.Fitness > Master_BH.Fitness) ENTONCES:
45.5            Master_BH = Clonar_Copia_Profunda(Lider_Actual)
45.6        FIN SI
45.7        F_crit = MIN(F_crit, Master_BH.Fitness) // Truncamiento dinámico anti-bloqueo
45.8    FIN SI

46.     // --- FASE 2: MOVIMIENTO DE ESTRELLAS Y EVENTOS GRAVITATORIOS ---
46.5    SI (Longitud(Lista_BH) == 0) Y (Master_BH != NULO) ENTONCES:
46.6        Registrar Master_BH en Lista_BH
46.7    FIN SI
47.     PARA cada estrella S de la población:
48.         es_bh_act = Comprobar_Si_Existe_Clon_En_Lista(S, Lista_BH)
49.         SI (es_bh_act == FALSO) ENTONCES:
50.             SI (Lista_BH NO está vacía) ENTONCES:
51.                 BH_Asignado = Encontrar_BH_Mas_Cercano_Hamming(S, Lista_BH)
52.                 
53.                 // --- GRAVEDAD LIMPIA POR BLOQUES DE GRUPO (TU MEJORA) ---
54.                 PARA cada Grupo 'g' del problema:
55.                     SI (Generar_Aleatorio(0, 1) < Pr) ENTONCES:
56.                         Apagar_Todos_Los_Objetos_Del_Grupo(S, g)
57.                         Idx_BH = Encontrar_Objeto_Activo_Del_BH_En_Grupo(BH_Asignado, g)
58.                         Activar_Objeto_En_Estrella(S, g, Idx_BH) // Estructura sana nativa
59.                     FIN SI
60.                 FIN PARA
61.                 Evaluar_Fitness_Mochila(S)
62.                 
63.                 // Horizonte de Eventos
64.                 SI (Calcular_Distancia_Hamming(S, BH_Asignado) < Radio_Horizonte) ENTONCES:
65.                     SI (Generar_Aleatorio(0, 1) < Prob_Slingshot) ENTONCES:
66.                         // --- EFECTO SLINGSHOT REVISADO: ELITISMO INTEGRAL (30/70) ---
67.                         Todos_Los_Grupos = Obtener_Lista_De_Grupos()
68.                         Barajar_Aleatoriamente(Todos_Los_Grupos)
69.                         
70.                         Limite_Conservacion = MAX(1, PARTE_ENTERA(Total_Grupos * 0.30))
71.                         Grupos_A_Conservar = Seleccionar_Primeros_N_Elementos(Todos_Los_Grupos, Limite_Conservacion)
72.                         
73.                         PARA cada Grupo 'g' del problema:
74.                             Apagar_Todos_Los_Objetos_Del_Grupo(S, g)
75.                             SI ('g' pertenece a Grupos_A_Conservar) ENTONCES:
76.                                 // Conservación elitista guiada por el atractor
77.                                 Idx_BH = Encontrar_Objeto_Activo_Del_BH_En_Grupo(BH_Asignado, g)
78.                                 Activar_Objeto_En_Estrella(S, g, Idx_BH)
79.                             SINO:
80.                                 // Prueba violenta y exploratoria al azar
81.                                 Idx_Azar = Generar_Entero_Aleatorio_Del_Grupo(g)
82.                                 Activar_Objeto_En_Estrella(S, g, Idx_Azar)
83.                             FIN SI
84.                         FIN PARA
85.                         Evaluar_Fitness_Mochila(S)
86.                         conteo_slingshot = conteo_slingshot + 1
87.                         
88.                         SI (Fitness(S) == 0) ENTONCES: 
89.                             S(Vector) = Generar_Solucion_Estructurada_MABC() 
90.                             Evaluar_Fitness_Mochila(S)
91.                         FIN SI
92.                     SINO:
93.                         S(Vector) = Generar_Solucion_Estructurada_MABC() 
94.                         Evaluar_Fitness_Mochila(S)
95.                     FIN SI
96.                 FIN SI
97.             SINO:
98.                 // Mutación Libre Segura con Ajuste de Dimensiones Correcto
99.                 Mascara_Booleana = Generar_Mascara_Aleatoria(Tasa_Alta = 0.5)
100.                Invertir_Bits_Donde_Mascara_Es_True(S, Mascara_Booleana)
101.                Reparar_Estructura_MMKP(S)
102.                Evaluar_Fitness_Mochila(S)
103.             FIN SI
104.         FIN SI
105.     FIN PARA

106.     // --- FASE 3: MOVIMIENTO DE AUTO-REFINAMIENTO DE LOS AGUJEROS NEGROS ---
107.     PARA cada BH en Lista_BH:
108.         BH_Intento = Clonar_Copia_Profunda(BH)
109.         Grupo_Azar = Generar_Entero_Aleatorio(0, Total_Grupos - 1)
110.         
111.         Apagar_Todos_Los_Objetos_Del_Grupo(BH_Intento, Grupo_Azar)
112.         Objeto_Elegido = Generar_Entero_Aleatorio_Del_Grupo(Grupo_Azar)
113.         Activar_Objeto_En_BH(BH_Intento, Grupo_Azar, Objeto_Elegido)
114.         
115.         Reparar_Estructura_MMKP(BH_Intento)
116.         Fit_Intento = Evaluar_Fitness_Mochila(BH_Intento)
117.         
118.         SI (Fit_Intento > BH.Fitness) ENTONCES:
119.             BH.Vector_Binario = BH_Intento.Vector_Binario
120.             BH.Fitness = Fit_Intento
121.             Contador_Estancamiento(BH) = 0
122.         SINO:
123.             Contador_Estancamiento(BH) = Contador_Estancamiento(BH) + 1
124.         FIN SI
125.     FIN PARA

126.     // --- FASE 4: EVAPORACIÓN POR RADIACIÓN DE HAWKING ---
127.     SI (Longitud(Lista_BH) > 0) ENTONCES:
128.         Mejor_BH_Actual = Encontrar_BH_Con_Maximo_Fitness(Lista_BH)
129.         
130.         PARA cada BH en Lista_BH:
131.             // Protección de élite para el campeón actual y el Máster mundial
132.             SI (BH != Mejor_BH_Actual) Y (BH.Fitness != Master_BH.Fitness) ENTONCES:
133.                 SI (Contador_Estancamiento(BH) >= Limite_Evaporacion) ENTONCES:
134.                     Marcar_Para_Evaporar(BH)
135.                     F_crit = F_crit * (1 - Delta_Enfriamiento)
136.                     conteo_evaporaciones = conteo_evaporaciones + 1
137.                 FIN SI
138.             FIN SI
139.         FIN PARA
140.         Ejecutar_Evaporacion_De_Marcados(Lista_BH)
141.     FIN SI

142.     // --- FASE 5: COLISIÓN Y FUSIÓN POR PROXIMIDAD EXTREMA ---
143.     SI (Longitud(Lista_BH) > 1) ENTONCES:
144.         PARA i desde 0 hasta Longitud(Lista_BH) - 1 HACER:
145.             PARA j desde i + 1 hasta Longitud(Lista_BH) - 1 HACER:
146.                 BH1 = Lista_BH[i]
147.                 BH2 = Lista_BH[j]
148.                 
149.                 SI (Calcular_Distancia_Hamming(BH1, BH2) <= Distancia_Max_Fusion) ENTONCES:
150.                     SI (BH1.Fitness >= BH2.Fitness) ENTONCES:
151.                         Marcar_Para_Eliminar(BH2)
152.                     SINO:
153.                         Marcar_Para_Eliminar(BH1)
154.                     FIN SI
155.                 FIN SI
156.             FIN PARA
157.         FIN PARA
158.         Ejecutar_Eliminacion_De_Marcados(Lista_BH)
159.     FIN SI

160.     SI (Longitud(Lista_BH) == 0) Y (Master_BH != NULO) ENTONCES:
161.         Registrar Master_BH en Lista_BH
162.     FIN SI

163.     Incrementar Iteración
164. FIN MIENTRAS

165. DEVOLVER el miembro con el mejor fitness absoluto dentro de Lista_BH (o Master_BH)
166. FIN
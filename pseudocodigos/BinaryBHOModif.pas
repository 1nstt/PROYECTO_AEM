1.  INICIO
2.  Definir Parámetros: Num_Estrellas, Max_Iter, Pr, Prob_Slingshot, Delta_Incremento, Distancia_Max_Fusion, Limite_Evaporacion, Delta_Enfriamiento, N_Subproblemas, Dh_Intercambios
3.  Calcular F_crit inicial: F_crit = (Suma_Total_Beneficios / Total_Objetos) * Total_Grupos
4.  Inicializar Lista_BH como una lista vacía

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

37.     // --- FASE 1: REGISTRO DE AGUJEROS NEGROS CON UMBRAL ESCALABLE ---
38.     PARA cada estrella S de la población:
39.         ya_es_bh = Comprobar_Si_Existe_Clon_En_Lista(S, Lista_BH)
40.         SI (Fitness(S) >= F_crit) Y (ya_es_bh == FALSO) ENTONCES:
41.             Registrar S en Lista_BH 
42.             Contador_Estancamiento(S) = 0
43.             F_crit = F_crit * (1 + Delta_Incremento)
44.         FIN SI
45.     FIN PARA

46.     // --- FASE 2: MOVIMIENTO DE ESTRELLAS Y EVENTOS GRAVITATORIOS ---
47.     PARA cada estrella S de la población:
48.         es_bh_act = Comprobar_Si_Existe_Clon_En_Lista(S, Lista_BH)
49.         SI (es_bh_act == FALSO) ENTONCES:
50.             SI (Lista_BH NO está vacía) ENTONCES:
51.                 BH_Asignado = Encontrar_BH_Mas_Cercano_Hamming(S, Lista_BH)
52.                 
53.                 PARA cada dimensión 'd' en la estrella S:
54.                     SI (Generar_Aleatorio(0, 1) < Pr) ENTONCES: S(d) = BH_Asignado(d) FIN SI
55.                 FIN PARA
56.                 Reparar_Estructura_MMKP(S)
57.                 Evaluar_Fitness_Mochila(S)
58.                 
59.                 // Horizonte de Eventos
60.                 SI (Calcular_Distancia_Hamming(S, BH_Asignado) < Radio_Horizonte) ENTONCES:
61.                     SI (Generar_Aleatorio(0, 1) < Prob_Slingshot) ENTONCES:
62.                         // EFECTO SLINGSHOT
63.                         PARA cada dimensión 'd' en la estrella S:
64.                             SI (S(d) != BH_Asignado(d)) ENTONCES: S(d) = NOT(S(d)) FIN SI
65.                         FIN PARA
66.                         Reparar_Estructura_MMKP(S)
67.                         
68.                         SI (Evaluar_Fitness_Mochila(S) == 0) ENTONCES: 
69.                             S(Vector) = Generar_Solucion_Estructurada_MABC() 
70.                             Evaluar_Fitness_Mochila(S)
71.                         FIN SI
72.                     SINO:
73.                         S(Vector) = Generar_Solucion_Estructurada_MABC() 
74.                         Evaluar_Fitness_Mochila(S)
75.                     FIN SI
76.                 FIN SI
77.             SINO:
78.                 Mutar_Estrella_Aleatoriamente(S, Tasa_Alta)
79.                 Reparar_Estructura_MMKP(S)
80.             FIN SI
81.         FIN SI
82.     FIN PARA

83.     // --- FASE 3: MOVIMIENTO DE AUTO-REFINAMIENTO POR TORNEO ESTOCÁSTICO ---
84.     PARA cada BH en Lista_BH:
85.         BH_Intento = Clonar_Copia_Profunda(BH)
86.         Grupo_Azar = Generar_Entero_Aleatorio(0, Total_Grupos - 1)
87.         
88.         // Desactivar el objeto actualmente seleccionado en ese grupo azar
89.         Apagar_Objeto_Activo_Del_Grupo(BH_Intento, Grupo_Azar)
90.         
91.         // Convocar un mini-torneo de 3 candidatos del grupo al azar (Mantiene la exploración)
92.         Candidatos_Torneo = Seleccionar_N_Objetos_Al_Azar_Del_Grupo(Grupo_Azar, Tamaño_Torneo=3)
93.         
94.         // El combate: Elegir al gladiador que maximice la utilidad del paper MABC
95.         Objeto_Ganador = Calcular_Ganador_Utilidad_Surrogada(Candidatos_Torneo, Capacidad_Mochila_b^k)
96.         Activar_Objeto_Del_Grupo(BH_Intento, Grupo_Azar, Objeto_Ganador)
97.         
98.         Reparar_Estructura_MMKP(BH_Intento)
99.         
100.        SI (Evaluar_Fitness_Mochila(BH_Intento) > Evaluar_Fitness_Mochila(BH)) ENTONCES:
101.            BH = BH_Intento
102.            Contador_Estancamiento(BH) = 0 // Progreso real detectado
103.        SINO:
104.            Contador_Estancamiento(BH) = Contador_Estancamiento(BH) + 1 // No se supera a sí mismo
105.        FIN SI
106.    FIN PARA

107.    // --- FASE 4: EVAPORACIÓN POR RADIACIÓN DE HAWKING CON PROTECCIÓN DE ÉLITE ---
108.    SI (Longitud(Lista_BH) > 0) ENTONCES:
109.        Mejor_BH_Global = Encontrar_BH_Con_Maximo_Fitness(Lista_BH)
110.        
111.        PARA cada BH en Lista_BH:
112.            SI (BH != Mejor_BH_Global) ENTONCES:
113.                SI (Contador_Estancamiento(BH) >= Limite_Evaporacion) ENTONCES:
114.                    Imprimir("¡RADIACIÓN DE HAWKING! Un agujero negro secundario perdió su masa.")
115.                    Marcar_Para_Evaporar(BH)
116.                    F_crit = F_crit * (1 - Delta_Enfriamiento)
117.                FIN SI
118.            FIN SI
119.        FIN PARA
120.        Ejecutar_Evaporacion_De_Marcados(Lista_BH)
121.    FIN SI

122.    // --- FASE 5: COLISIÓN Y FUSIÓN POR PROXIMIDAD EXTREMA ---
123.    SI (Longitud(Lista_BH) > 1) ENTONCES:
124.        PARA i desde 0 hasta Longitud(Lista_BH) - 1 HACER:
125.            PARA j desde i + 1 hasta Longitud(Lista_BH) - 1 HACER:
126.                BH1 = Lista_BH[i]
127.                BH2 = Lista_BH[j]
128.                 
129.                SI (Calcular_Distancia_Hamming(BH1, BH2) <= Distancia_Max_Fusion) ENTONCES:
130.                    Imprimir("¡COLISIÓN CÓSMICA! Dos atractores se han encontrado en el hipercubo.")
131.                    SI (Evaluar_Fitness_Mochila(BH1) >= Evaluar_Fitness_Mochila(BH2)) ENTONCES:
132.                        Marcar_Para_Eliminar(BH2)
133.                    SINO:
134.                        Marcar_Para_Eliminar(BH1)
135.                    FIN SI
136.                FIN SI
137.            FIN PARA
138.        FIN PARA
139.        Ejecutar_Eliminacion_De_Marcados(Lista_BH)
140.    FIN SI

141.    Reevaluar_Fitness_Toda_La_Población()
142.    Incrementar Iteración
143. FIN MIENTRAS

144. DEVOLVER el miembro con el mejor fitness absoluto dentro de Lista_BH (o población si está vacía)
145. FIN
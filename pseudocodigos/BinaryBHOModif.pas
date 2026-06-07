Algoritmo: BBH-MMKP con Slingshot, Umbral Escalable, BH Móvil, Fusión y Evaporación por Radiación de Hawking (Con Protección de Élite)

1.  INICIO
2.  Definir Parámetros: Num_Estrellas, Max_Iter, Pr, Prob_Slingshot, Delta_Incremento, Distancia_Max_Fusion, Limite_Evaporacion, Delta_Enfriamiento
3.  Calcular F_crit inicial: F_crit = (Suma_Total_Beneficios / Total_Objetos) * Total_Grupos
4.  Inicializar Lista_BH como una lista vacía

5.  // Inicialización de la población de estrellas
6.  PARA cada estrella S desde 1 hasta Num_Estrellas:
7.      Inicializar S con un vector de ceros
8.      Reparar_Estructura_MMKP(S) // Garantiza exactamente un objeto por grupo
9.      Evaluar_Fitness_Mochila(S) // Calcula la función objetivo Z (0 si es inviable)
10. FIN PARA

11. // Bucle Principal de Simulación Cósmica
12. MIENTRAS (Iteración < Max_Iter) HACER:

13.     // --- FASE 1: REGISTRO DE AGUJEROS NEGROS CON UMBRAL ESCALABLE ---
14.     PARA cada estrella S de la población:
15.         ya_es_bh = Comprobar_Si_Existe_Clon_En_Lista(S, Lista_BH)
16.         SI (Fitness(S) >= F_crit) Y (ya_es_bh == FALSO) ENTONCES:
17.             Registrar S en Lista_BH 
18.             Inicializar Contador_Estancamiento(S) = 0
19.             F_crit = F_crit * (1 + Delta_Incremento) // Escalamos la exigencia del umbral
20.         FIN SI
21.     FIN PARA

22.     // --- FASE 2: MOVIMIENTO DE ESTRELLAS Y EVENTOS GRAVITATORIOS ---
23.     PARA cada estrella S de la población:
24.         es_bh_activo = Comprobar_Si_Existe_Clon_En_Lista(S, Lista_BH)
25.         SI (es_bh_activo == FALSO) ENTONCES:
26.             SI (Lista_BH NO está vacía) ENTONCES:
27.                 BH_Asignado = Encontrar_BH_Mas_Cercano_Hamming(S, Lista_BH)
28.                 
29.                 // Atracción Gravitatoria paso a paso (Pulling Rate)
30.                 PARA cada dimensión 'd' en la estrella S:
31.                     SI (Generar_Aleatorio(0, 1) < Pr) ENTONCES: S(d) = BH_Asignado(d) FIN SI
32.                 FIN PARA
33.                 Reparar_Estructura_MMKP(S)
34.                 Evaluar_Fitness_Mochila(S)
35.                 
36.                 // Evaluación de la frontera crítica (Horizonte de Eventos)
37.                 SI (Calcular_Distancia_Hamming(S, BH_Asignado) < Radio_Horizonte) ENTONCES:
38.                     SI (Generar_Aleatorio(0, 1) < Prob_Slingshot) ENTONCES:
39.                         // EFECTO SLINGSHOT (Evasión por aceleración elástica)
40.                         PARA cada dimensión 'd' en la estrella S:
41.                             SI (S(d) != BH_Asignado(d)) ENTONCES: S(d) = NOT(S(d)) FIN SI
42.                         FIN PARA
43.                         Reparar_Estructura_MMKP(S)
44.                         SI (Evaluar_Fitness_Mochila(S) == 0) ENTONCES: Reiniciar_Mochila_Aleatoria(S) FIN SI
45.                     SINO:
46.                         Reiniciar_Mochila_Aleatoria(S) // Absorción tradicional en la singularidad
47.                     FIN SI
48.                 FIN SI
49.             SINO:
50.                 Mutar_Estrella_Aleatoriamente(S, Tasa_Alta) // Caos inicial si no hay líderes
51.                 Reparar_Estructura_MMKP(S)
52.             FIN SI
53.         FIN SI
54.     FIN PARA

55.     // --- FASE 3: MOVIMIENTO DE AUTO-REFINAMIENTO DE LOS AGUJEROS NEGROS ---
56.     PARA cada BH en Lista_BH:
57.         BH_Intento = Clonar_Copia_Profunda(BH)
58.         Grupo_Azar = Generar_Entero_Aleatorio(0, Total_Grupos - 1)
59.         Mutar_Unico_Objeto_Del_Grupo(BH_Intento, Grupo_Azar)
60.         Reparar_Estructura_MMKP(BH_Intento)
61.         
62.         SI (Evaluar_Fitness_Mochila(BH_Intento) > Evaluar_Fitness_Mochila(BH)) ENTONCES:
63.             BH = BH_Intento // El pozo gravitatorio se desplaza a una mejor coordenada local
64.             Contador_Estancamiento(BH) = 0 // Resetea su contador por éxito evolutivo
65.         SINO:
66.             Contador_Estancamiento(BH) = Contador_Estancamiento(BH) + 1 // Acumula rigidez
67.         FIN SI
68.     FIN PARA

69.     // --- FASE 4: EVAPORACIÓN POR RADIACIÓN DE HAWKING CON PROTECCIÓN DE ÉLITE ---
70.     SI (Longitud(Lista_BH) > 0) ENTONCES:
71.         Mejor_BH_Global = Encontrar_BH_Con_Maximo_Fitness(Lista_BH) // La Mero-Élite
72.         
73.         PARA cada BH en Lista_BH:
74.             SI (BH != Mejor_BH_Global) ENTONCES: // Blindaje cuántico: la mejor solución es inmune
75.                 SI (Contador_Estancamiento(BH) >= Limite_Evaporacion) ENTONCES:
76.                     Imprimir("¡RADIACIÓN DE HAWKING! Un agujero negro secundario perdió su masa.")
77.                     Marcar_Para_Evaporar(BH)
78.                     F_crit = F_crit * (1 - Delta_Enfriamiento) // Bajamos el umbral para liberar rigidez
79.                 FIN SI
80.             FIN SI
81.         FIN PARA
82.         Ejecutar_Evaporacion_De_Marcados(Lista_BH) // Remueve los pozos estancados
83.     FIN SI

84.     // --- FASE 5: COLISIÓN Y FUSIÓN POR PROXIMIDAD EXTREMA ---
85.     SI (Longitud(Lista_BH) > 1) ENTONCES:
86.         PARA i desde 0 hasta Longitud(Lista_BH) - 1 HACER:
87.             PARA j desde i + 1 hasta Longitud(Lista_BH) - 1 HACER:
88.                 BH1 = Lista_BH[i]
89.                 BH2 = Lista_BH[j]
90.                 
91.                 SI (Calcular_Distancia_Hamming(BH1, BH2) <= Distancia_Max_Fusion) ENTONCES:
92.                     Imprimir("¡COLISIÓN CÓSMICA! Dos atractores se han encontrado en el hipercubo.")
93.                     SI (Evaluar_Fitness_Mochila(BH1) >= Evaluar_Fitness_Mochila(BH2)) ENTONCES:
94.                         Marcar_Para_Eliminar(BH2)
95.                     SINO:
96.                         Marcar_Para_Eliminar(BH1)
97.                     FIN SI
98.                 FIN SI
99.             FIN PARA
100.        FIN PARA
101.        Ejecutar_Eliminacion_De_Marcados(Lista_BH) // Deja solo a los atractores dominantes
102.    FIN SI

103.    Reevaluar_Fitness_Toda_La_Población()
104.    Incrementar Iteración
105. FIN MIENTRAS

106. DEVOLVER el miembro con el mejor fitness absoluto dentro de Lista_BH (o población si está vacía)
107. FIN
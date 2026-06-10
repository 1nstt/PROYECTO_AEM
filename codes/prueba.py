import numpy as np
import time
from cargar_instancias import cargar_instancia_khan
from clasebase import BBH_MMKP_UDP_Optimizer 

if __name__ == "__main__":
    ruta_instancia = "../Benchmarks/I07.txt"
    
    print("=========================================================")
    print("   MÁXIMA OPTIMIZACIÓN ENERGETICA: PERFIL AGRESIVO DE FO")
    print("=========================================================\n")
    
    print("[info] cargando datos desde el benchmark...")
    datos_i07 = cargar_instancia_khan(ruta_instancia)
    
    print("[info] inicializando el optimizador con hiperparámetros de ajuste fino...")
    
    # 2000 it
    num_iteraciones = 2000
    optimizador = BBH_MMKP_UDP_Optimizer(
        datos_instancia=datos_i07,
        num_estrellas=25,                 # SN (Population size) idéntico del paper
        max_iter=num_iteraciones,         # maxCycle = 2000
        pr=0.10,                          # pr = 0.10 mapea exactamente d_emp = n/n_i (10%)
        prob_slingshot=0.08,              # Perturbación moderada de escape
        radio_horizonte=7,                # Distancia Hamming límite estándar
        delta_incremento=0.006,           # Ritmo balanceado de f_crit
        distancia_max_fusion=2,           # Control estricto de duplicados en vecindad
        limite_evaporacion=75,            # Ciclos tolerados sin mejora para Hawking
        delta_enfriamiento=0.006,         # Enfriamiento térmico simétrico
        extra_fcrit_inicial=-2000     # Calibrador dinámico para evitar bloqueos iniciales
    )
    print("[info] ejecutando simulación de alta intensidad...")
    
    tiempo_inicio = time.time()
    mejor_solucion = optimizador.optimizar()
    tiempo_fin = time.time()
    
    tiempo_cpu_total = tiempo_fin - tiempo_inicio
    
    print("\n=========================================================")
    print("            RESULTADOS DEL MODELO DE MÁXIMO RENDIMIENTO    ")
    print("=========================================================")
    print(f"▶ beneficio máximo alcanzado (Función Objetivo Z): {mejor_solucion.fitness}")
    print(f"▶ benchmark de referencia mabc_2000: 24050.0")
    print(f"▶ tiempo total consumido por la cpu: {tiempo_cpu_total:.4f} segundos")
    print(f"▶ tiempo promedio por iteración: {(tiempo_cpu_total / num_iteraciones) * 1000:.4f} milisegundos")
    
    # --- NUEVAS MÉTRICAS DE TELEMETRÍA AVANZADA ---
    print(f"▶ censo poblacional: récord de atractores (BHs) simultáneos: {optimizador.max_bhs_simultaneos}")
    print(f"▶ eventos slingshot totales gatillados: {optimizador.total_slingshots_gatillados}")
    print(f"▶ slingshots exitosos (mejoraron el fitness estelar): {optimizador.slingshots_exitosos_fitness}")
    print(f"▶ slingshots viables: {optimizador.slingshots_factibles} | infactibles (respawn): {optimizador.slingshots_infactibles_respawn}")
    # ----------------------------------------------

    consumos_finales = np.dot(mejor_solucion.vector_binario, datos_i07['r_ij_k'])
    print(f"▶ consumo total por recurso k: {consumos_finales}")
    
    if np.all(consumos_finales <= datos_i07['b_k']):
        print("▶ estado de restricciones k: solución perfectamente viable ✔")
    else:
        print("▶ estado de restricciones k: la solución excedió la mochila ❌")
        
    total_seleccionados = np.sum(mejor_solucion.vector_binario)
    print(f"▶ total de ítems seleccionados: {total_seleccionados} de {datos_i07['n']} grupos")
    
    print("\n▶ vector binario óptimo (solución x_ij):")
    print(mejor_solucion.vector_binario.tolist())
    print("=========================================================")
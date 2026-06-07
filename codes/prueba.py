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
    
    # Elevamos las iteraciones a 3000 para compensar el enfriamiento lento de f_crit
    num_iteraciones = 3000 
    
    optimizador = BBH_MMKP_UDP_Optimizer(
        datos_instancia=datos_i07,
        num_estrellas=40,               # Más estrellas buscando combinaciones válidas
        max_iter=num_iteraciones,       # Más ciclos de explotación y refinamiento
        pr=0.45,                        # Equilibrio justo para evitar convergencia prematura
        prob_slingshot=0.12,            # Escape controlado en zonas cercanas al horizonte
        radio_horizonte=15,             # Mayor área de captura de estrellas para reestructuración
        delta_incremento=0.0015,        # Subida lenta de f_crit: permite registrar más BHs alternativos
        distancia_max_fusion=2,         # Colisión óptima para mantener diversidad en el espacio binario
        limite_evaporacion=50,          # Hawking agresivo: BHs estancados se evaporan rápido para resetear zonas
        delta_enfriamiento=0.004        # Enfriamiento balanceado tras evaporación
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
    
    consumos_finales = np.dot(mejor_solucion.vector_binario, datos_i07['r_ij_k'])
    print(f"▶ consumo total por recurso k: {consumos_finales}")
    
    if np.all(consumos_finales <= datos_i07['b_k']):
        print("▶ estado de restricciones k: solución perfectamente viable ✔")
    else:
        print("▶ estado de restricciones k: la solución excedió la mochila ❌")
        
    total_seleccionados = np.sum(mejor_solucion.vector_binario)
    print(f"▶ total de ítems seleccionados: {total_seleccionados} de {datos_i07['n']} grupos")
    print("=========================================================")
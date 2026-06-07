import numpy as np
import time
from cargar_instancias import cargar_instancia_khan
from clasebase import BBH_MMKP_UDP_Optimizer 

if __name__ == "__main__":
    ruta_instancia = "../Benchmarks/I07.txt"
    
    print("=========================================================")
    print("   EJECUCIÓN BBH-MMKP CON EVAPORACIÓN (HAWKING RADIATION)")
    print("=========================================================\n")
    
    print("[info] cargando datos desde el benchmark...")
    datos_i07 = cargar_instancia_khan(ruta_instancia)
    
    print("[info] inicializando la población de estrellas...")
    optimizador = BBH_MMKP_UDP_Optimizer(
        datos_instancia=datos_i07,
        num_estrellas=25,       # escala de población del paper
        max_iter=2000,          # 2000 iteraciones para dar tiempo a la radiación
        pr=0.5,                 
        prob_slingshot=0.08     
    )
    
    # inyectar hiperparámetros base antes de arrancar
    optimizador.radio_horizonte = 10
    optimizador.delta_incremento = 0.005
    optimizador.distancia_max_fusion = 2
    
    print("[info] ejecutando el sistema dinámico...")
    
    tiempo_inicio = time.time()
    mejor_solucion = optimizador.optimizar()
    tiempo_fin = time.time()
    
    tiempo_cpu_total = tiempo_fin - tiempo_inicio
    
    print("\n=========================================================")
    print("            RESULTADOS DEL MODELO EVAPORATIVO            ")
    print("=========================================================")
    print(f"▶ beneficio máximo alcanzado (Función Objetivo Z): {mejor_solucion.fitness}")
    print(f"▶ benchmark de referencia mabc_2000: 24050.0")
    print(f"▶ tiempo total consumido por la cpu: {tiempo_cpu_total:.4f} segundos")
    print(f"▶ tiempo promedio por iteración: {(tiempo_cpu_total / 2000) * 1000:.4f} milisegundos")
    
    consumos_finales = np.dot(mejor_solucion.vector_binario, datos_i07['r_ij_k'])
    print(f"▶ consumo total por recurso k: {consumos_finales}")
    
    if np.all(consumos_finales <= datos_i07['b_k']):
        print("▶ estado de restricciones k: solución perfectamente viable ✔")
    else:
        print("▶ estado de restricciones k: la solución excedió la mochila ❌")
        
    total_seleccionados = np.sum(mejor_solucion.vector_binario)
    print(f"▶ total de ítems seleccionados: {total_seleccionados} de {datos_i07['n']} grupos")
    print("=========================================================")
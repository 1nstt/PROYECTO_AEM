import numpy as np
import os
import time
from cargar_instancias import cargar_instancia_khan
from clasebase import BBH_MMKP_UDP_Optimizer 

if __name__ == "__main__":
   
    # NOMBRE DEL ARCHIVO ACTUAL CON EL NOMBRE DE LA INSTANCIA
    id_instancia = os.path.splitext(os.path.basename(__file__))[0]
    ruta_instancia = f"../Benchmarks/{id_instancia}.txt"
    
    # Encabezados base
    linea_decorativa = "========================================================="
    print(linea_decorativa)
    print("   MÁXIMA OPTIMIZACIÓN ENERGETICA: PERFIL AGRESIVO DE FO")
    print(f"   EJECUTANDO EXPERIMENTO AUTOMATIZADO: {id_instancia}")
    print(linea_decorativa + "\n")
    
    datos_instancia = cargar_instancia_khan(ruta_instancia)
    
    num_iteraciones = 2000
    optimizador = BBH_MMKP_UDP_Optimizer(
        datos_instancia=datos_instancia,
        num_estrellas=25,                 # Ajustado a 25 para simetría poblacional con MABC
        max_iter=num_iteraciones,
        pr=0.10,
        prob_slingshot=0.08,
        radio_horizonte=7,
        delta_incremento=0.006,
        distancia_max_fusion=2,
        limite_evaporacion=75,
        delta_enfriamiento=0.006,
        extra_fcrit_inicial=-3000          
    )
    
    tiempo_inicio = time.time()
    mejor_solucion = optimizador.optimizar()
    tiempo_fin = time.time()
    tiempo_cpu_total = tiempo_fin - tiempo_inicio
    
    # =================================================================
    # CAPTURA DINÁMICA DEL REPORTE FINAL EN STRING
    # =================================================================
    string_reporte = ""
    string_reporte += f"\n{linea_decorativa}\n"
    string_reporte += "            RESULTADOS DEL MODELO DE MÁXIMO RENDIMIENTO    \n"
    string_reporte += f"{linea_decorativa}\n"
    string_reporte += f"▶ beneficio máximo alcanzado (Función Objetivo Z): {mejor_solucion.fitness}\n"
    string_reporte += f"▶ tiempo total consumido por la cpu: {tiempo_cpu_total:.4f} segundos\n"
    string_reporte += f"▶ tiempo promedio por iteración: {(tiempo_cpu_total / num_iteraciones) * 1000:.4f} milisegundos\n\n"
    
    string_reporte += f"▶ censo poblacional: récord de atractores (BHs) simultáneos: {optimizador.max_bhs_simultaneos}\n"
    string_reporte += f"▶ censo poblacional: total histórico de atractores (BHs) nacidos: {optimizador.total_bhs_creados_historico}\n"
    string_reporte += f"▶ eventos slingshot totales gatillados: {optimizador.total_slingshots_gatillados}\n"
    string_reporte += f"▶ slingshots exitosos (mejoraron el fitness estelar): {optimizador.slingshots_exitosos_fitness}\n"
    string_reporte += f"▶ slingshots viables (factibles): {optimizador.slingshots_factibles} | infactibles (respawn): {optimizador.slingshots_infactibles_respawn}\n\n"
    
    consumos_finales = np.dot(mejor_solucion.vector_binario, datos_instancia['r_ij_k'])
    string_reporte += f"▶ consumo total por recurso k: {consumos_finales}\n"
    
    if np.all(consumos_finales <= datos_instancia['b_k']):
        string_reporte += "▶ estado de restricciones k: solución perfectamente viable \n"
    else:
        string_reporte += "▶ estado de restricciones k: la solución excedió la mochila \n"
        
    total_seleccionados = np.sum(mejor_solucion.vector_binario)
    string_reporte += f"▶ total de ítems seleccionados: {total_seleccionados} de {datos_instancia['n']} grupos\n"
    string_reporte += f"{linea_decorativa}\n"
    
    # Imprimir el reporte final en la consola de VS Code
    print(string_reporte)
    
    # =================================================================
    # INVOCACIÓN OPCIONAL DEL MÉTODO GRÁFICO
    # =================================================================
    optimizador.generar_reportes_y_graficos(nombre_instancia=id_instancia, texto_consola=string_reporte)
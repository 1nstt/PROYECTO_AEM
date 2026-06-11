import os
import subprocess
import sys
import time
from pathlib import Path

if __name__ == "__main__":
    # =================================================================
    # CONFIGURACION DEL EXPERIMENTO MASIVO
    # =================================================================
    ruta_codes = Path("codes")
    veces_cada_instancia = 5  # PARAMETRO MODIFICABLE
    
   
    instancias = [
        "I07", "I09", "I11", "I13",
        "INST01", "INST03", "INST05", "INST07", "INST09",
        "INST11", "INST13", "INST15", "INST17", "INST19", "INST20"
    ]
    # =================================================================
    
    metricas_globales = {inst: {"exitos": 0, "errores": 0, "tiempos": []} for inst in instancias}
    total_scripts_exitosos = 0
    total_scripts_fallidos = 0
    tiempo_inicio_batch = time.time()
    
    # Clonamos las variables de entorno del sistema y forzamos UTF-8 para Python
    entorno_utf8 = os.environ.copy()
    entorno_utf8["PYTHONIOENCODING"] = "utf-8"
    entorno_utf8["PYTHONUTF8"] = "1"
    
    linea_decorativa = "========================================================="
    print(linea_decorativa)
    print("EJECUCION MASIVA")
    print(f"   PLANIFICACION: {len(instancias)} instancias x {veces_cada_instancia} corridas c/u")
    print(linea_decorativa + "\n")
    
    for idx_inst, inst in enumerate(instancias, 1):
        archivo_py = ruta_codes / f"{inst}.py"
        
        if not archivo_py.exists():
            print(f"[alerta] Archivo no encontrado: {archivo_py.name} | Saltando lote...")
            total_scripts_fallidos += veces_cada_instancia
            metricas_globales[inst]["errores"] = veces_cada_instancia
            continue
            
        print(f"\n-> [{idx_inst}/{len(instancias)}] Iniciando lote para la instancia: {inst}")
        print(linea_decorativa)
        
        for corrida in range(1, veces_cada_instancia + 1):
            print(f"   -> Corriendo ciclo {corrida}/{veces_cada_instancia}... ", end="", flush=True)
            
            t_inicio_corrida = time.time()
            try:
               
                resultado = subprocess.run(
                    [sys.executable, f"{inst}.py"],
                    cwd=str(ruta_codes),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=entorno_utf8,
                    text=True,
                    encoding="utf-8",
                    errors="ignore"
                )
                
                t_fin_corrida = time.time() - t_inicio_corrida
                metricas_globales[inst]["exitos"] += 1
                metricas_globales[inst]["tiempos"].append(t_fin_corrida)
                total_scripts_exitosos += 1
                print(f"OK ({t_fin_corrida:.2f}s)")
                
            except subprocess.CalledProcessError as err:
                metricas_globales[inst]["errores"] += 1
                total_scripts_fallidos += 1
                print("ERROR")
                
                # Captura el error de forma segura en caso de fallos reales del algoritmo
                error_texto = err.stderr if err.stderr else "Error desconocido de ejecucion"
                lineas_error = error_texto.strip().splitlines()
                detalle = lineas_error[-1] if lineas_error else "Fallo en tiempo de ejecucion"
                print(f"      [Detalle del fallo]: {detalle}")
                
    tiempo_total_batch = time.time() - tiempo_inicio_batch
    
    # Reporte Consolidado Final
    print("\n" + linea_decorativa)
    print("         RESUMEN CONSOLIDADO DEL EXPERIMENTO")
    print(linea_decorativa)
    print(f"-> Tiempo total de procesamiento CPU: {tiempo_total_batch:.2f} segundos")
    print(f"-> Total de corridas planificadas : {len(instancias) * veces_cada_instancia}")
    print(f"-> Total de ejecuciones EXITOSAS  : {total_scripts_exitosos}")
    print(f"-> Total de ejecuciones FALLIDAS  : {total_scripts_fallidos}\n")
    
    print("TABLA DE RENDIMIENTO POR INSTANCIA:")
    print("-" * 65)
    print(f"{'Instancia':<12} | {'Exitos':<8} | {'Errores':<8} | {'Tiempo Promedio':<15}")
    print("-" * 65)
    
    for inst, datos in metricas_globales.items():
        tiempos = datos["tiempos"]
        promedio_str = f"{sum(tiempos)/len(tiempos):.3f}s" if tiempos else "N/A"
        print(f"{inst:<12} | {datos['exitos']:<8} | {datos['errores']:<8} | {promedio_str:<15}")
        
    print("-" * 65)
    print("Simulacion masiva finalizada de forma controlada.")
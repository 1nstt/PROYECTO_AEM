import numpy as np

def cargar_instancia_khan(ruta_archivo: str) -> dict:
    # todos los comentarios de lectura parten en minúsculas
    with open(ruta_archivo, 'r') as f:
        lineas = [l.strip() for l in f.readlines() if l.strip()]
        
    # 1. leer la primera línea con las dimensiones básicas
    partes_dimension = lineas[0].split()
    n_grupos = int(partes_dimension[0])     # n
    items_por_grupo = int(partes_dimension[1]) # N_i
    m_recursos = int(partes_dimension[2])   # m
    
    # 2. leer la segunda línea con las capacidades b_k
    b_k = np.array([float(x) for x in lineas[1].split()])
    
    # 3. inicializar contenedores para las variables del modelo
    V_ij = []
    r_ij_k = []
    mapeo_grupos = {}
    N_i = {}
    
    idx_linea = 2
    id_grupo_actual = 0
    
    # 4. recorrer el archivo procesando cada bloque de datos
    while idx_linea < len(lineas):
        linea_actual = lineas[idx_linea].split()
        
        # comprobar si es un identificador de grupo aislado (ej. "1", "2")
        if len(linea_actual) == 1:
            # si la línea única no es un número (ej: 'Solutions'), ignoramos el resto del archivo
            if not linea_actual[0].isdigit():
                break
                
            id_grupo_actual = int(linea_actual[0]) - 1 # ajustar a índice 0 de python
            mapeo_grupos[id_grupo_actual] = []
            N_i[id_grupo_actual] = items_por_grupo
            idx_linea += 1
            continue
            
        # procesar las líneas del ítem con un try-except protector
        try:
            beneficio = float(linea_actual[0])
            consumos = [float(x) for x in linea_actual[1:]]
            
            # si por algún motivo la línea no trae todos los consumos k esperados, la saltamos
            if len(consumos) != m_recursos:
                idx_linea += 1
                continue
                
            # guardar en las estructuras globales de la población
            idx_lineal_item = len(V_ij)
            V_ij.append(beneficio)
            r_ij_k.append(consumos)
            
            # asociar el ítem a su conjunto de grupo correspondiente
            mapeo_grupos[id_grupo_actual].append(idx_lineal_item)
            
        except ValueError:
            # si encuentra texto como 'Solutions' u otra palabra, salta la línea sin caerse
            pass
            
        idx_linea += 1

    # 5. empaquetar todo en el diccionario final compatible con el optimizador
    return {
        'n': n_grupos,
        'N_i': N_i,
        'm': m_recursos,
        'b_k': b_k,
        'r_ij_k': np.array(r_ij_k),
        'V_ij': np.array(V_ij),
        'mapeo_grupos': mapeo_grupos
    }

# --- bloque de ejecución y testeo de la instancia ---
if __name__ == "__main__":
    # usando los dos puntos para salir de la carpeta codes
    ruta = "../Benchmarks/I07.txt" 
    
    print("--- PROCESANDO ARCHIVO DE INSTANCIA ---")
    datos_i07 = cargar_instancia_khan(ruta)
    
    # despliegue de prints para verificar la consistencia matemática de la i07
    print("\n==============================================")
    print("¡INSTANCIA CARGADA EXITOSAMENTE CON EL PARSER!")
    print("==============================================")
    print(f"cantidad de grupos (n) detectados: {datos_i07['n']} (esperado: 100)")
    print(f"cantidad de recursos (m) detectados: {datos_i07['m']} (esperado: 10)")
    print(f"dimensiones finales de r_ij_k (matriz de consumo): {datos_i07['r_ij_k'].shape} (esperado: (1000, 10))")
    print(f"cantidad de beneficios V_ij procesados: {len(datos_i07['V_ij'])} (esperado: 1000)")
    print(f"vector de capacidades máximas b_k:\n{datos_i07['b_k']}")
    print("==============================================\n")
Algoritmo: Optimización por Agujero Negro Binario (BBH)

1. INICIO
2. Inicializar una población de estrellas de forma aleatoria (con valores 0 y 1).
3. Evaluar la aptitud (fitness) de cada estrella según la función objetivo.

4. MIENTRAS (no se cumpla el criterio de parada, ej. número de iteraciones):
    
    5. Seleccionar la estrella con la mejor aptitud y definirla como el Agujero Negro (BH).
    
    6. PARA cada estrella S de la población (que no sea el BH):
        
        // Llamada a la función para mover las soluciones hacia el BH
        7. PARA cada dimensión 'd' en la estrella S:
            8. Generar un número aleatorio r entre 0 y 1.
            
            9. SI (r < pulling_rate_Pr) ENTONCES:
                10. Hacer S(d) igual a BH(d)  // Adopta el valor del Agujero Negro
            11. SINO:
                12. No cambiar S(d)          // Mantiene su propio valor
            13. FIN SI
        14. FIN PARA (dimensión)
        
        // Simulación del horizonte de sucesos (Eliminación/Reemplazo)
        15. SI la estrella S está demasiado cerca del BH (o cruzó el horizonte):
            16. Eliminar la estrella S.
            17. Generar una nueva estrella de forma aleatoria para reemplazar a S.
        18. FIN SI
        
    19. FIN PARA (estrella)

20. FIN MIENTRAS

21. DEVOLVER el Agujero Negro (BH) como la solución óptima encontrada.
22. FIN
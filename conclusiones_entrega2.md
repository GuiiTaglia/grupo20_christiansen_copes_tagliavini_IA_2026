Conclusiones:

Para resolver el problema mediante inteligencia artificial utilizamos ChatGPT 5.5. El prompt fue: "Dame la resolucion completa del siguiente enunciado de CSP. Teniendo en cuenta las restricciones de los modulos del campamento espacial y las indicaciones de implementacion" y el enunciado completo. Al pasar los tests, la solucion directa de la IA fallo en los casos medianos y avanzados, quedandose congelada y sobrepasando el limite de tiempo (más de 120 segundos en los casos de prueba como m2 o m3), ademas de fallar por retornar None erróneamente ante la ausencia de modulos.

**Ejemplos:**

**Resultados de IA:**

text
FAILED test_entrega2.py::test_resultado_es_correcto[case7] - AssertionError (s1: sin módulos retornó None)
UserWarning: El caso [m3: cráteres que restringen la ubicación de los módulos] demoró demasiado tiempo (más de 120 segundos), probablemente algo no está bien con la implementación del CSP.

**Resultados de Nuestra solución:**

text
PASSED test_entrega2.py::test_resultado_es_correcto[case1] (s1: sin módulos retornó [])
PASSED test_entrega2.py::test_resultado_es_correcto[case7] (m2: dos laboratorios resuelto en 0.02 segundos)
PASSED test_entrega2.py::test_resultado_es_correcto[case8] (m3: cráteres resuelto en 0.05 segundos)

Vemos **semejanzas** en el planteo de las variables y la inicializacion de los dominios, excluyendo los crateres correctamente mediante listas por comprension. Ambas soluciones identifican de la misma manera las restricciones unarias basicas como la de las esclusas en los bordes (airlock_border / airlock_on_edge) y las habitacionales en el interior (hab_inside / hab_in_interior). Además, ambos códigos coinciden en usar la misma lógica (la distancia de Manhattan) para chequear si los módulos no son adyacentes.

En cuanto a las **diferencias**, la mas notoria se encuentra en el modelado de la restriccion global de no superposicion. La IA aplico una restricción N-aria poniendo la lista completa de variables a la funcion different_positions con una comprobación global de conjuntos (len(set(values)) == len(values)). Lo que causo esto fue una explosión combinatoria masiva en el motor de backtrack, forzandolo a esperar que se asignen todos los modulos para luego verificar si chocaban. En nuestra solucion la reescribimos de manera binaria (en parejas de a dos variables usando bucles for combinatorios), permitiendo descartar de manera temprana las ramas inválidas en milisegundos. Tambien podemos notar como diferencia el manejo de la Ruta de Evacuacion. La IA resolvio esta regla fuera del CSP (aplicando la verificacion como un filtro manual sobre la solucion ya hecha) lo cual funciona, pero invalida soluciones completas al final del camino si la unica habitacion elegida quedo bloqueada. En nuestra solucion pusimos la ruta de evacuacion como una restriccion dinamica dentro del propio objeto CspProblem, logrando que el motor de busqueda podara las celdas sin salida en el momento. Por ultimo, la IA omitio por completo el caso base donde los modulos requeridos son cero, provocando que CspProblem fallara internamente al recibir variables vacias, lo cual nosotros solucionamos mediante una intercepcion temprana (early return).

En conclusion, podemos decir que la resolucion directa de la IA comete grandes errores de diseño al ignorar la eficiencia interna de las librerias. Al plantear restricciones globales en lugar de binarias, un problema de pocos milisegundos termina siendo un bucle infinito por falta de optimizacion. En nuestra intervencion analizamos el comportamiento del motor de backtracking, estructuramos mejor las penalizaciones en parejas y contemplamos los casos limite de las pruebas que la IA omitio por dar una respuesta rapida. Las soluciones de las IA pueden ser utiles por momentos para ayudarnos como base, pero siempre es necesaria una intervencion para refinar una solucion optima. 

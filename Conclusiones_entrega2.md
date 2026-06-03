##Conclusiones:

Para resolver el problema mediante inteligencia artificial utilizamos ChatGPT basado en GPT-5.5.
Para el prompt simplemente escribimos: "Dame la resolucion completa del siguiente enunciado de CSP. Teniendo en cuenta las restricciones de los modulos del campamento espacial y las indicaciones de implementacion" y el enunciado completo. Al pasar los tests, la solucion directa de la IA fallo en los casos medianos y avanzados, quedandose congelada y excediendo el limite de tiempo critico (más de 120 segundos en los casos de prueba como m2 o m3), ademas de fallar por retornar None erróneamente ante la ausencia de modulos (s1).

_Ejemplos:_

_Resultados de IA:_

text
FAILED test_entrega2.py::test_resultado_es_correcto[case7] - AssertionError (s1: sin módulos retornó None)
UserWarning: El caso [m3: cráteres que restringen la ubicación de los módulos] demoró demasiado tiempo (más de 120 segundos), probablemente algo no está bien con la implementación del CSP.

_Resultados de Nuestra solución:_

text
PASSED test_entrega2.py::test_resultado_es_correcto[case1] (s1: sin módulos retornó [])
PASSED test_entrega2.py::test_resultado_es_correcto[case7] (m2: dos laboratorios resuelto en 0.02 segundos)
PASSED test_entrega2.py::test_resultado_es_correcto[case8] (m3: cráteres resuelto en 0.05 segundos)

Vemos _semejanzas_ en el planteo de las variables y la inicializacion de los dominios, excluyendo los crateres correctamente mediante listas por comprension. Ambas soluciones identifican de la misma manera las restricciones unarias basicas como la de las esclusas en los bordes (airlock_border / airlock_on_edge) y las habitacionales en el interior (hab_inside / hab_in_interior). Tambien coinciden en el uso logico del metodo auxiliar matematico para calcular la adyacencia Manhattan ortogonal.

En cuanto a las _diferencias_, la mas critica radica en el modelado de la restriccion global de no superposicion. La IA aplico una restricción N-aria inyectando la lista completa de variables a la función different_positions con una comprobación global de conjuntos (len(set(values)) == len(values)). Esto causó una explosión combinatoria masiva en el motor de backtrack de simpleai, forzándolo a esperar que se asignen todos los modulos para recién verificar si chocaban. Nuestra solucion optima la reescribio de manera binaria (en parejas de a dos variables usando bucles for combinatorios), permitiendo el descarte temprano de ramas inválidas en milisegundos.

Otra diferencia notoria es el manejo de la _Ruta de Evacuacion_. La IA resolvio esta regla de forma imperativa fuera del CSP, es decir, aplicando la verificacion como un filtrado manual post-procesamiento sobre la solucion ya armada. Si bien funciona, invalida soluciones completas al final del camino si la unica habitacion elegida quedo bloqueada. Nuestra solucion integro la ruta de evacuacion como una restriccion dinamica nativa dentro del propio objeto CspProblem, garantizando que el motor de busqueda podara las celdas sin salida sobre la marcha. Finalmente, la IA omitio por completo el caso base donde los modulos requeridos son cero (s1), provocando que CspProblem fallara internamente al recibir variables vacias, lo cual nosotros solucionamos mediante una intercepcion temprana (early return).

En conclusion, podemos decir nuevamente que la resolución directa de una IA comete errores severos de arquitectura algoritmica al ignorar la eficiencia interna de las librerias de busqueda. Al plantear restricciones globales en lugar de binarias, un problema de pocos milisegundos termina siendo un bucle infinito por falta de optimizacion. La intervencion como estudiantes nos permitio analizar el comportamiento del motor de backtracking, estructurar mejor las penalizaciones en parejas y contemplar los casos limite de las pruebas que la IA omitio por dar una respuesta rapida.

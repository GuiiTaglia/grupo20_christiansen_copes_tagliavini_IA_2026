Conclusiones

Para resolver el problema mediante inteligencia artificial utilizamos gemini 3.1 pro. Para el prompt simplemente escribimos: "Dame la resolución completa del siguiente enunciado. Teniendo en cuenta las restricciones pedidas y las acciones que puede ejecutar el rover. Además de las indicaciones de implementación pedidas por la cátedra." + el enunciado completo. Al pasar los tests, algunos pasan y otros no (pero solo por que una palabra tenia acento), además que demora mucho para realizarlos (más de 900 segundos como el de la muestra en (0, 30) o el de muestras opuestas y otros). **Ejemplos:**

**Resultados de IA:**

1\.
PASSED
test_entrega1.py::test_resultado_es_correcto[case8] 
Resolviendo caso [m3: 1 muestra lejana]
rover=(0, 0) battery=20 shadows=() igneous=((0, 30),) sediments=()
...
Solución obtenida en 909.7 segundos

**Resultados de Nuestra solución:**

1\.
PASSED
test_entrega1.py::test_resultado_es_correcto[case8] 
Resolviendo caso [m3: 1 muestra lejana]
rover=(0, 0) battery=20 shadows=() igneous=((0, 30),) sediments=()
...
Solución obtenida en 0.3 segundos

Vemos **semejanzas** en el uso de un método constructor para inicializar el estado del rover (def \_\_init\_\_). Utiliza el método A\* para realizar la búsqueda, la función cost es casi igual. La IA tuvo en cuenta que nunca se debe llegar a 0 de batería, por lo que siempre hace las validaciones necesarias para que sea batería > 0 y la función goal, si bien esta escrita en menos lineas de código, cumple la misma función.

En cuanto a las **diferencias**, vemos que el estado no es el mismo en relación a las muestras. Nosotros agrupamos todas las muestras en un único frozenset de tuplas, para luego remplazar los valores con .replace. La IA hace dos conjuntos independientes, y maneja la carga con 0, 1, o 2 (esto nos parece mejor, ya que nuestra solución tiene que recorrer ese set completo para buscar las coordenadas, lo cual es menos eficiente). En relación a la heurísitca, la IA la mantiene super simple, sumando solo el tiempo de recolectar y depositar, ignorando distancias y cambios de taladros. Nuestra solución contiene, además, la distancia a la muestra mas cercana, calculando el tiempo de viaje ideal y teniendo en cuenta los cambios mínimos del taladro. En nuestra resolución también agregamos un límite del mapa y verificamos que cada vez que se mueve sea una posición valida, esto la IA lo omite o asumió que la grilla no tenía limites. Como ultima diferencia vemos que la resolución de la IA, permite cambiar el taladro en cualquier momento, que nosotros en un principio habíamos resuelto de esa manera. Pero cuando cambiamos a que solo pueda hacer el cambio si esta encima de una muestra los tiempos de búsqueda fueron mucho mejor y los test nos dejaron de tirar warnings de tiempo. 

Para concluir, vemos que una resolución de un estudiante puede ser un poco mas amigable de leer, utilizando estructuras de datos, centralizando los datos y con una heurística un poco mas pensada, sin ser simplemente una respuesta rápida para realizar la solución. Pero también al querer hacer un código fácil de leer y entender (ya que no sabíamos mucho de python) obviamos un poco la eficiencia y hicimos que en cierta parte del código la resolución sea un poco más lenta. 

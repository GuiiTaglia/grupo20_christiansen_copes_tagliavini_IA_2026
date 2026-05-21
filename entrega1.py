from simpleai.search import (
    SearchProblem,
    astar,
)
import math
from collections import namedtuple

EstadoRover = namedtuple('EstadoRover', [
    'pos', 
    'bateria', 
    'taladro_equipado', 
    'carga', 
    'muestras_restantes'
    ])
#PREGUNTAR POR EL USO DE NAMEDTUPLE, PERO PARA MI ES MAS FACIL DE MANEJAR (nos permite hacer .pos, .bateria, etc en vez de usar indices)

TIEMPO = {
    "moverse": 1,
    "sobremarcha": 1,
    "equipar": 3,
    "recolectar": 2,
    "depositar": 1, 
    "recargar": 4,
}

BATERIA = {
    "moverse": 1,
    "sobremarcha": 4,
    "equipar": 1,
    "recolectar": 3,
    "depositar": 1,  
    "recargar": 10,
}
TALADROS = {
    "ignea": "termico",
    "sedimentaria": "percusion"
}
BATERIA_MAX = 20
CANT_MAX_MUESTRAS = 2
MAPA_LIM=30 #PREGUNTAR, pero lo suponemos por los test que se dieron.
DIRECCIONES = [(0, 1), (1, 0), (0, -1), (-1, 0)]  
class Entrega1Problem(SearchProblem):

    def __init__(self, rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias): #PREGUNTAR si esta bien para inicializar los datos del problema, es como tener un punto de partida
        self.zonas_sombra = set(zonas_sombra)
        
        muestras = frozenset (
            [(pos, 'ignea') for pos in muestras_igneas] + 
            [(pos, 'sedimentaria') for pos in muestras_sedimentarias]
        )

        estado_inicial = EstadoRover(
            pos=rover_inicio,
            bateria=bateria_inicial,
            taladro_equipado=None,
            carga=(),
            muestras_restantes=muestras,
        )
        super().__init__(estado_inicial)
    
#de ayuda para la heuristica, calcular el tiempo minimo de viaje
    def min_tiempo_viaje(self, distancia, bateria):
        if distancia == 0:
            return 0
        mejor = float('inf') 
        for k in range(distancia // 2 + 1):  # k = cantidad de sobremarcha
            pasos_normales = distancia - 2 * k
            bateria_necesaria = 4 * k + pasos_normales + 1  # +1 para nunca llegar a 0
            deficit = max(0, bateria_necesaria - bateria)
            recargas = math.ceil(deficit / 10) if deficit > 0 else 0
            tiempo = k + pasos_normales + recargas * TIEMPO["recargar"]
            mejor = min(mejor, tiempo)
        return mejor

#de ayuda para calcular la distancia entre dos puntos
    def distancia_manhattan(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

#de ayuda para validar que el rover no se salga del mapa
    def es_posicion_valida(self, pos):
        return -MAPA_LIM <= pos[0] <= MAPA_LIM and -MAPA_LIM <= pos[1] <= MAPA_LIM

#de ayuda para saber que tipo de muestra hay en la posiciona actual del rover
    def muestra_en_posicion(self, pos, muestras_restantes):
        for pos_m, tipo in muestras_restantes:
            if pos_m == pos:
                return tipo
        return None

    def actions(self, state):
        acciones_validas = []
       
        #moverse
        if state.bateria - BATERIA["moverse"] > 0:
            for dx, dy in DIRECCIONES:
                destino = (state.pos[0] + dx, state.pos[1] + dy)
                if self.es_posicion_valida(destino):
                    acciones_validas.append(('moverse', destino))
        
        #sobremarcha
        if state.bateria - BATERIA["sobremarcha"] > 0:
            for dx, dy in DIRECCIONES:
                destino = (state.pos[0] + 2*dx, state.pos[1] + 2*dy)
                if self.es_posicion_valida(destino):
                    acciones_validas.append(('sobremarcha', destino))
        
        #equipar taladro
        if state.bateria - BATERIA["equipar"] > 0:
            tipo_muestra = self.muestra_en_posicion(state.pos, state.muestras_restantes)
            if tipo_muestra is not None:
                taladro_requerido = TALADROS[tipo_muestra]
                if state.taladro_equipado != taladro_requerido: 
                    acciones_validas.append(('equipar', taladro_requerido))
     
        #recolectar
        tipo_muestra = self.muestra_en_posicion(state.pos, state.muestras_restantes)
        if (
            tipo_muestra is not None 
            and state.taladro_equipado == TALADROS[tipo_muestra]
            and len(state.carga) < CANT_MAX_MUESTRAS
            and state.bateria - BATERIA["recolectar"] > 0
        ): 
            acciones_validas.append(('recolectar', tipo_muestra))
        
        #depositar
        es_ultima = (len(state.muestras_restantes) == 0 and len(state.carga) > 0)
        puede_depositar = len(state.carga) == CANT_MAX_MUESTRAS or es_ultima
        if puede_depositar and state.bateria - BATERIA["depositar"] > 0:
            acciones_validas.append(('depositar', None))
        
        #recargar
        if state.pos not in self.zonas_sombra and state.bateria < BATERIA_MAX:
            acciones_validas.append(('recargar', None))
        
        return acciones_validas
    
    def result(self, state, action):
        tipo_accion, parametro = action

        if tipo_accion == "moverse":
            return state._replace(
                pos=parametro,
                bateria=state.bateria - BATERIA["moverse"],
            )

        elif tipo_accion == "sobremarcha":
            return state._replace(
                pos=parametro,
                bateria=state.bateria - BATERIA["sobremarcha"],
            )

        elif tipo_accion == "equipar":
            return state._replace(
                taladro_equipado=parametro,
                bateria=state.bateria - BATERIA["equipar"],
            )
        
        elif tipo_accion == "recolectar":
            nueva_carga = tuple(sorted(state.carga + (parametro,)))
            return state._replace(
                bateria=state.bateria - BATERIA["recolectar"],
                carga=nueva_carga,
                muestras_restantes=state.muestras_restantes - {(state.pos, parametro)},
            )

        elif tipo_accion == "depositar":
            return state._replace(
                bateria=state.bateria - BATERIA["depositar"],
                carga=(),
            )

        elif tipo_accion == "recargar":
            return state._replace(
                bateria=min(state.bateria + 10, BATERIA_MAX),
            )
        
    def is_goal(self, state):
        return len(state.muestras_restantes) == 0 and len(state.carga) == 0

    def heuristic(self, state):
        if not state.muestras_restantes and not state.carga:
            return 0
        n_restantes = len(state.muestras_restantes)
        n_carga = len(state.carga)

        # por cada muestra restante, el costo de recolectar + depositar (2 + 1 = 3)
        h1 = n_restantes * (TIEMPO["recolectar"] + TIEMPO["depositar"])

        # el tiempo (que es 1) por cada muestra cargada que hay que depositar
        h_carga = n_carga * TIEMPO["depositar"]

        #los cambios necesarios del taladro
        h2 = 0
        if state.muestras_restantes:
            taladros_requeridos = set(TALADROS[tipo] for _, tipo in state.muestras_restantes)
            if state.taladro_equipado in taladros_requeridos:
                cambios = len(taladros_requeridos) - 1
            else:
                cambios = len(taladros_requeridos)
            h2 = cambios * TIEMPO["equipar"]

        # distancia a la muestra más cercana
        if state.muestras_restantes:
            min_dist = min(self.distancia_manhattan(state.pos, pos) for pos, _ in state.muestras_restantes)
            h3 = self.min_tiempo_viaje(min_dist, state.bateria)
        else:
            h3 = 0

        return h1 + h_carga + h2 + h3
    
    def cost(self, state, action, state2):
        tipo_accion, parametro = action
        costo_base = TIEMPO[tipo_accion]

        if tipo_accion == "depositar":
            return costo_base * len(state.carga)
        else:
            return costo_base        
    
    
def planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
    
    problema = Entrega1Problem(
        rover_inicio, 
        bateria_inicial, 
        zonas_sombra, 
        muestras_igneas, 
        muestras_sedimentarias
    )
    resultado= astar(problema, graph_search=True)
    if resultado is None:
        return "No se encontró una solución"    
    return [accion for accion, _ in resultado.path() if accion is not None]
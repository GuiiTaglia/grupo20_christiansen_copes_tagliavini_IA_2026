from simpleai.search import (
    SearchProblem,
    greedy,
    astar
)
from collections import namedtuple
from typing import Tuple, FrozenSet, Optional

EstadoRover = namedtuple('EstadoRover', [
    'pos', 
    'bateria', 
    'taladro_equipado', 
    'carga', 
    'muestras_restantes'
    ])


TIEMPO = {
    "moverse": 1,
    "sobremarcha": 1,
    "equipar": 1,
    "recolectar": 2,
    "depositar": 1,  # por muestra depositada
    "recargar": 4,
}

BATERIA = {
    "moverse": 1,
    "sobremarcha": 4,
    "equipar": 1,
    "recolectar": 3,
    "depositar": 1,  # por muestra depositada
    "recargar": 20,
}
TALADROS = {
    "igneas": "termico",
    "sedimentarias": "percusion"
}
BATERIA_MAX = 20
CANT_MAX_MUESTRAS = 2
MAPA= (5, 5)  
DIRECCIONES = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # derecha, abajo, izquierda, arriba
class Entrega1Problem(SearchProblem):

    def __init__(self, rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
        self.zonas_sombra = set(zonas_sombra)
        
        muestras = frozenset (
            [(pos, 'igneas') for pos in muestras_igneas] + 
            [(pos, 'sedimentarias') for pos in muestras_sedimentarias]
        )

        estado_inicial = EstadoRover(
            pos=rover_inicio,
            bateria=bateria_inicial,
            taladro_equipado=None,
            carga=(),
            muestras_restantes=muestras,
        )
        super().__init__(estado_inicial)
#valida que la posicion este dentro del mapa
    def es_posicion_valida(self, pos):
        return 0 <= pos[0] < MAPA[0] and 0 <= pos[1] < MAPA[1]

# De ayuda para saber que tipo de muestra hay en la posiciona actual del rover
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
            for tipo in TALADROS.keys():
                if tipo != state.taladro_equipado:
                    acciones_validas.append(('equipar', tipo))
     
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
        if puede_depositar and state.bateria - BATERIA["depositar"] * len(state.carga) > 0:
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
            return state._replace(
                bateria=state.bateria - BATERIA["recolectar"],
                carga=state.carga + (parametro,),
                muestras_restantes=frozenset(
                    m for m in state.muestras_restantes
                    if m != (state.pos, parametro)
                ),
            )

        elif tipo_accion == "depositar":
            return state._replace(
                bateria=state.bateria - BATERIA["depositar"] * len(state.carga),
                carga=(),
            )

        elif tipo_accion == "recargar":
            return state._replace(
                bateria=min(state.bateria + 10, BATERIA_MAX),
            )
        
    def is_goal(self, state):
        return len(state.muestras_restantes) == 0 and len(state.carga) == 0

    def heuristic(self, state):
        return super().heuristic(state)
        #heuristica: 2*muestras en mapa + cambios mínimos taladro * 3 + distancia de manhattan/2 + (cant muestras faltantes + cant muestras cargadas)/2 
    def cost(self, state, action, state2): 
        return super().cost(state, action, state2)        
    
    
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
    return [accion for accion, _ in resultado.path()]
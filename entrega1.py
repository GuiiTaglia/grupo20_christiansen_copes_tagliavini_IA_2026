from simpleai.search import (
    SearchProblem,
    greedy,
    astar
)
from dataclasses import dataclass
from typing import Tuple, FrozenSet, Optional

@dataclass(frozen=True)
class EstadoRover:
    pos: Tuple[int, int]
    bateria: int
    taladro_equipado: Optional[str]  # 'igneas', 'sedimentarias' o None
    carga: Tuple[str, ...]  # muestras recolectadas
    muestras_restantes: FrozenSet[Tuple]    # muestras que aún no se han recolectado
    capsulas_depositadas: int

TIEMPO = {
    "moverse": 1,
    "sobremarcha": 1,
    "equipar_taladro": 1,
    "recolectar": 2,
    "depositar": 1,  # por muestra depositada
    "recargar": 4,
}

BATERIA = {
    "moverse": -1,
    "sobremarcha": -4,
    "equipar_taladro": -1,
    "recolectar": -3,
    "depositar": -1,  # por muestra depositada
    "recargar": +20,
}
TALADROS = {
    "igneas": "termico",
    "sedimentarias": "percusion"
}
BATERIA_MAX = 20
CANT_MAX_MUESTRAS = 2
DIRECCIONES = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # derecha, abajo, izquierda, arriba
class Entrega1Problem(SearchProblem):

    def __init__(self, rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
        self.zonas_sombra = set(zonas_sombra)
        
        muestras = frozenset([
            *( (pos, 'ignea') for pos in muestras_igneas ),
            *( (pos, 'sedimentaria') for pos in muestras_sedimentarias ),
        ])
        self.total_muestras = len(muestras)
        estado_inicial = EstadoRover(
            pos=rover_inicio,
            bateria=bateria_inicial,
            taladro_equipado=None,
            carga=(),
            muestras_restantes=muestras,
        )
        super().__init__(estado_inicial)

        #funcion q nos va a ayudar para saber q muestra hay en la posicion que esta parado el rover
        def muestra_en_posicion(self, pos, muestras_restantes):
            for pos_m, tipo in muestras_restantes:
                if pos_m == pos:
                    return tipo
                return None
        
        #funcion para saber si es la ultima carga y no quedan muestras para recolectar
        def es_ultima_carga(self, carga, muestras_restantes):
            return len(muestras_restantes) == 0 and len(carga) > 0

    def actions(self, state):
        acciones_validas = []
        #moverse
        if state.bateria - BATERIA["moverse"] > 0:
            for dx, dy in DIRECCIONES:
                destino = (state.pos[0] + dx, state.pos[1] + dy)
                acciones_validas.append(('moverse', destino))
        
        #sobremarcha
        if state.bateria - BATERIA["sobremarcha"] > 0:
            for dx, dy in DIRECCIONES:
                destino = (state.pos[0] + 2*dx, state.pos[1] + 2*dy)
                acciones_validas.append(('sobremarcha', destino))
        
        #equipar taladro
        if state.bateria - BATERIA["equipar_taladro"] > 0:
            for tipos in TALADROS.keys():
                if tipos != state.taladro_equipado:
                    acciones_validas.append(('equipar_taladro', tipos))
     
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
        puede_depositar = (
            len(state.carga) == CANT_MAX_MUESTRAS or self.es_ultima_carga(state.carga, state.muestras_restantes)
        )
        if len(state.carga) > 0 and state.bateria - BATERIA["depositar"]*len(state.carga) > 0 and puede_depositar:
            acciones_validas.append(('depositar', None))
        
        #recargar
        if state.pos not in self.zonas_sombra and state.bateria < BATERIA_MAX:
            acciones_validas.append(('recargar', None))
        
        return acciones_validas
    
    def result(self, state, action):
        return super().result(state, action)

    def is_goal(self, state):
        return super().is_goal(state)

    def heuristic(self, state):
        return super().heuristic(state)
        #heuristica: 2*muestras en mapa + cambios mínimos taladro * 3 + distancia de manhattan/2 + (cant muestras faltantes + cant muestras cargadas)/2 
    def cost(self, state, action, state2): 
        return super().cost(state, action, state2)        
    
    
def planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
    
    problema = (
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

if __name__ == "__main__":    
    rover_inicio = (0, 0)
    bateria_inicial = 100
    zonas_sombra = [(1, 1), (2, 2)]
    muestras_igneas = [(3, 3), (4, 4)]
    muestras_sedimentarias = [(5, 5), (6, 6)]
    resultado = planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias)
    print("Plan de acciones para el rover:")
    print(resultado)
    
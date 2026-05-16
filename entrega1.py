from simpleai.search import (
    SearchProblem,
    greedy,
    astar
)
from simpleai.search.viewers import WebViewer, BaseViewer
class Entrega1Problem(SearchProblem):
    def actions(self, state):
        return super().actions(state)
    #moverse
    #sobremarcha
    #equipar taladro
    #perforar y recolectar
    #depositar capsula con muestras
    #desplegar paneles solares para cargar baterias

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
    estado_inicial = (
        rover_inicio, 
        bateria_inicial, 
        tuple(muestras_igneas) + tuple(muestras_sedimentarias), 
        None, 
        0
    )
    problema=Entrega1Problem(estado_inicial, zonas_sombra=zonas_sombra)
    acciones_resultado= astar(problema, graph_search=True)
    return acciones_resultado

if __name__ == "__main__":    
    rover_inicio = (0, 0)
    bateria_inicial = 100
    zonas_sombra = [(1, 1), (2, 2)]
    muestras_igneas = [(3, 3), (4, 4)]
    muestras_sedimentarias = [(5, 5), (6, 6)]
    resultado = planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias)
    print("Plan de acciones para el rover:")
    print(resultado)
    
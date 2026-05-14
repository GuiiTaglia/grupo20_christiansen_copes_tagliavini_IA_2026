from simpleai.search import (
    SearchProblem,
    greedy
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
        
    def cost(self, state, action, state2):
        return super().cost(state, action, state2)

    #def planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):

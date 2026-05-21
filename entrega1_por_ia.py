from simpleai.search import SearchProblem, astar

class MisionMarte(SearchProblem):
    def __init__(self, rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
        self.zonas_sombra = set(zonas_sombra)
        
        # El estado inicial debe ser inmutable (hashable)
        estado_inicial = (
            rover_inicio,                 # (fila, columna)
            bateria_inicial,              # int (1 a 20)
            None,                         # taladro activo: None, "termico" o "percusión"
            0,                            # cantidad de muestras en bodega (0 a 2)
            frozenset(muestras_igneas),   # posiciones de rocas ígneas restantes
            frozenset(muestras_sedimentarias) # posiciones de rocas sedimentarias restantes
        )
        super().__init__(initial_state=estado_inicial)

    def actions(self, state):
        pos, bat, taladro, carga, igneas, sedimentarias = state
        r, c = pos
        acciones_disp = []

        # 1. Moverse (Toma 1 min, consume 1 bat)
        if bat > 1:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                acciones_disp.append(("moverse", (r + dr, c + dc)))

        # 2. Sobremarcha / Overdrive (Toma 1 min, consume 4 bat)
        if bat > 4:
            for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                acciones_disp.append(("sobremarcha", (r + dr, c + dc)))

        # 3. Equipar taladro (Toma 3 min, consume 1 bat)
        if bat > 1:
            if taladro != "termico":
                acciones_disp.append(("equipar", "termico"))
            if taladro != "percusión":
                acciones_disp.append(("equipar", "percusión"))

        # 4. Perforar y recolectar (Toma 2 min, consume 3 bat)
        if bat > 3 and carga < 2:
            if pos in igneas and taladro == "termico":
                acciones_disp.append(("recolectar", "ignea"))
            if pos in sedimentarias and taladro == "percusión":
                acciones_disp.append(("recolectar", "sedimentaria"))

        # 5. Depositar cápsula (Toma 1 min x muestra, consume 1 bat)
        if bat > 1 and carga > 0:
            faltantes_en_mapa = len(igneas) + len(sedimentarias)
            # Solo podemos armar cápsula si tenemos 2, o si son literalmente las últimas del mapa
            if carga == 2 or faltantes_en_mapa == 0:
                acciones_disp.append(("depositar", None))

        # 6. Desplegar paneles solares / recargar (Toma 4 min, recupera hasta 10 bat)
        # Solo no se permite si estamos en una zona de sombra. 
        if pos not in self.zonas_sombra and bat < 20:
            acciones_disp.append(("recargar", None))

        return acciones_disp

    def result(self, state, action):
        pos, bat, taladro, carga, igneas, sedimentarias = state
        tipo_accion, param = action

        if tipo_accion == "moverse":
            return (param, bat - 1, taladro, carga, igneas, sedimentarias)
        
        elif tipo_accion == "sobremarcha":
            return (param, bat - 4, taladro, carga, igneas, sedimentarias)
        
        elif tipo_accion == "equipar":
            return (pos, bat - 1, param, carga, igneas, sedimentarias)
        
        elif tipo_accion == "recolectar":
            nueva_carga = carga + 1
            # Quitamos la muestra recién recolectada de los conjuntos restantes
            nuevas_igneas = igneas - {pos} if param == "ignea" else igneas
            nuevas_sed = sedimentarias - {pos} if param == "sedimentaria" else sedimentarias
            return (pos, bat - 3, taladro, nueva_carga, nuevas_igneas, nuevas_sed)
        
        elif tipo_accion == "depositar":
            return (pos, bat - 1, taladro, 0, igneas, sedimentarias)
        
        elif tipo_accion == "recargar":
            return (pos, min(20, bat + 10), taladro, carga, igneas, sedimentarias)

    def cost(self, state1, action, state2):
        tipo_accion = action[0]
        
        if tipo_accion in ("moverse", "sobremarcha"):
            return 1
        elif tipo_accion == "equipar":
            return 3
        elif tipo_accion == "recolectar":
            return 2
        elif tipo_accion == "depositar":
            carga_actual = state1[3]
            return carga_actual * 1  # 1 minuto por cada muestra que se está entregando
        elif tipo_accion == "recargar":
            return 4
            
        return 0

    def is_goal(self, state):
        _, _, _, carga, igneas, sedimentarias = state
        # El objetivo es que no queden muestras en el mapa ni en el inventario del rover
        return len(igneas) == 0 and len(sedimentarias) == 0 and carga == 0

    def heuristic(self, state):
        _, _, _, carga, igneas, sedimentarias = state
        # Tiempo ineludible: Cada muestra en el mapa obligatoriamente costará 
        # 2 minutos en ser recolectada y 1 minuto en ser depositada (total 3).
        # Además, cada muestra ya cargada en la bodega costará 1 minuto depositarla.
        # No sumamos tiempo de movimiento para garantizar admisibilidad estricta.
        return (len(igneas) + len(sedimentarias)) * 3 + (carga * 1)


def planear_rover(rover_inicio=(0, 0), bateria_inicial=20, zonas_sombra=[], muestras_igneas=[], muestras_sedimentarias=[]):
    """
    Función que configura el problema de búsqueda del Rover en Marte 
    y retorna la lista de acciones óptimas para cumplir el objetivo.
    """
    problema = MisionMarte(
        rover_inicio=rover_inicio,
        bateria_inicial=bateria_inicial,
        zonas_sombra=zonas_sombra,
        muestras_igneas=muestras_igneas,
        muestras_sedimentarias=muestras_sedimentarias
    )
    
    # Se utiliza A* con búsqueda en grafo (evita explorar estados repetidos)
    resultado = astar(problema, graph_search=True)
    
    acciones_finales = []
    
    # Extraemos solo las acciones y descartamos los nodos/estados intermedios
    if resultado is not None:
        for accion, _ in resultado.path():
            if accion is not None:  # Ignorar la acción 'None' del estado inicial
                acciones_finales.append(accion)
                
    return acciones_finales
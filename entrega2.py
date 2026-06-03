from simpleai.search import (
    CspProblem,
    backtrack
)

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    if habs == 0 and generators == 0 and labs == 0 and deposits == 0 and airlocks == 0:
        return []
    
    rows, cols = camp_size
        
    variables = []
    types_count = {
        "hab": habs,
        "gen": generators,
        "lab": labs,
        "dep": deposits,
        "air": airlocks
    }
        
    for m_type, count in types_count.items():
        for i in range(count):
            variables.append(f"{m_type}_{i}")
                
    all_cells = [(r, c) for r in range(rows) for c in range(cols)]
    valid_cells = [cell for cell in all_cells if cell not in craters]
    domains = {v: valid_cells for v in variables}

    #Restricciones

    # Auxiliar: Verifica adyacencia ortogonal
    def is_adjacent(pos1, pos2):
        r1, c1 = pos1
        r2, c2 = pos2
        return abs(r1 - r2) + abs(c1 - c2) == 1

    # 1 Sin superposición
    #def no_overlap(variables, values):
    #    return len(set(values)) == len(values)

    def no_overlap(variables, values):
        return values[0] != values[1]

    # 3. Esclusas en el borde
    def airlock_on_edge(variables, values):
        r, c = values[0]
        return r == 0 or r == rows - 1 or c == 0 or c == cols - 1

    # 4. Habitacionales al interior (no en el borde)
    def hab_in_interior(variables, values):
        r, c = values[0]
        return 0 < r < rows - 1 and 0 < c < cols - 1

    # 5 y 6. Seguridad energética (Gen no cerca de Hab o de otro Gen)
    def energy_safety(variables, values):
        return not is_adjacent(values[0], values[1])

    # 7. Cadena de suministro científico (Lab adj a al menos un Dep)
    def lab_needs_deposit(variables, values):
        lab_pos = values[0]
        dep_positions = values[1:]
        return any(is_adjacent(lab_pos, dep_pos) for dep_pos in dep_positions)

    # 8. Ruta de evacuación (Hab adj a celda vacía)
    def evacuation_route(variables, values):
        hab_pos = values[0]
        other_positions = values[1:]
        r, c = hab_pos
        neighbors = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
            
        for n in neighbors:
            nr, nc = n
            # Si el vecino está en el mapa, no es cráter y no hay ningún módulo allí
            if (0 <= nr < rows and 0 <= nc < cols and 
                n not in craters and n not in other_positions):
                return True
        return False

    constraints = []

    for i, v1 in enumerate(variables):
        for v2 in variables[i+1:]:
            constraints.append(([v1, v2], no_overlap))

    for v in variables:
        if v.startswith("air"):
            constraints.append(([v], airlock_on_edge))
        if v.startswith("hab"):
            constraints.append(([v], hab_in_interior))

    gens = [v for v in variables if v.startswith("gen")]
    habs_vars = [v for v in variables if v.startswith("hab")]
        
    for g in gens:
        for h in habs_vars:
            constraints.append(([g, h], energy_safety))
        for g2 in gens:
            if g < g2: 
                constraints.append(([g, g2], energy_safety))

    labs_vars = [v for v in variables if v.startswith("lab")]
    deps_vars = [v for v in variables if v.startswith("dep")]
    if deps_vars:
        for l in labs_vars:
            constraints.append(([l] + deps_vars, lab_needs_deposit))
    elif labs_vars:
        return None

    for h in habs_vars:
        others = [v for v in variables if v != h]
        constraints.append(([h] + others, evacuation_route))

    problem = CspProblem(variables, domains, constraints)
    solution = backtrack(problem)

    if solution is None:
        return None
        
    result = []
    for var, pos in solution.items():
        m_type = var.split('_')[0]
        result.append((m_type, pos[0], pos[1]))
            
    return result


    

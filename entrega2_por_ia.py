from simpleai.search import CspProblem, backtrack


def adjacent(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) == 1


def build_camp(
    camp_size,
    habs,
    generators,
    labs,
    deposits,
    airlocks,
    craters,
):
    rows, cols = camp_size

    variables = []

    hab_vars = [f"hab_{i}" for i in range(habs)]
    gen_vars = [f"gen_{i}" for i in range(generators)]
    lab_vars = [f"lab_{i}" for i in range(labs)]
    dep_vars = [f"dep_{i}" for i in range(deposits)]
    air_vars = [f"air_{i}" for i in range(airlocks)]

    variables.extend(hab_vars)
    variables.extend(gen_vars)
    variables.extend(lab_vars)
    variables.extend(dep_vars)
    variables.extend(air_vars)

    domain = [
        (r, c)
        for r in range(rows)
        for c in range(cols)
        if (r, c) not in craters
    ]

    domains = {var: domain[:] for var in variables}

    constraints = []

    # -------------------------
    # Sin superposición
    # -------------------------

    def different_positions(vars, values):
        return len(values) == len(set(values))

    constraints.append((variables, different_positions))

    # -------------------------
    # Esclusas en borde
    # -------------------------

    def airlock_border(vars, values):
        r, c = values[0]

        return (
            r == 0
            or r == rows - 1
            or c == 0
            or c == cols - 1
        )

    for air in air_vars:
        constraints.append(([air], airlock_border))

    # -------------------------
    # Habitacionales interiores
    # -------------------------

    def hab_inside(vars, values):
        r, c = values[0]

        return (
            0 < r < rows - 1
            and
            0 < c < cols - 1
        )

    for hab in hab_vars:
        constraints.append(([hab], hab_inside))

    # -------------------------
    # Hab - Gen no adyacentes
    # -------------------------

    def not_adjacent(vars, values):
        return not adjacent(values[0], values[1])
    
    def gen_not_adjacent(vars, values):
        if len(values) < 2:
            return True

        (r1, c1) = values[0]
        (r2, c2) = values[1]

        return abs(r1 - r2) + abs(c1 - c2) != 1
    
    for i in range(len(gen_vars)):
        for j in range(i + 1, len(gen_vars)):
            constraints.append(
                ([gen_vars[i], gen_vars[j]], gen_not_adjacent)
            )

    for hab in hab_vars:
        for gen in gen_vars:
            constraints.append(
                ([hab, gen], not_adjacent)
            )

    # -------------------------
    # Gen - Gen no adyacentes
    # -------------------------

    def different(vars, values):
        if len(values) < 2:
            return True

        return values[0] != values[1]
    
    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            constraints.append(
                ([variables[i], variables[j]], different)
            )

    # -------------------------
    # Lab adyacente a algún dep
    # -------------------------

    def lab_near_deposit(vars, values):
        if len(values) < len(vars):
            return True

        lab_pos = values[0]

        for dep_pos in values[1:]:
            if adjacent(lab_pos, dep_pos):
                return True

        return False

    for lab in lab_vars:
        constraints.append(
            ([lab] + dep_vars, lab_near_deposit)
        )

    # Resolver CSP
    problem = CspProblem(
        variables,
        domains,
        constraints,
    )

    solution = backtrack(problem)

    if solution is None:
        return None

    # -------------------------
    # Ruta de evacuación
    # -------------------------

    occupied = set(solution.values())

    for hab in hab_vars:

        r, c = solution[hab]

        neighbors = [
            (r - 1, c),
            (r + 1, c),
            (r, c - 1),
            (r, c + 1),
        ]

        free_exit = False

        for nr, nc in neighbors:

            if not (
                0 <= nr < rows
                and 0 <= nc < cols
            ):
                continue

            if (nr, nc) in craters:
                continue

            if (nr, nc) in occupied:
                continue

            free_exit = True
            break

        if not free_exit:
            return None

    result = []

    for name, (r, c) in solution.items():

        if name.startswith("hab"):
            t = "hab"
        elif name.startswith("gen"):
            t = "gen"
        elif name.startswith("lab"):
            t = "lab"
        elif name.startswith("dep"):
            t = "dep"
        else:
            t = "air"

        result.append((t, r, c))

    return result
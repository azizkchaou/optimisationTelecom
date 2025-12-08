def generate_demo_data():
    """
    Generates a dictionary of demo data.
    """
    plans = [
        {'id': 'P1', 'name': 'Entry 1GB', 'data_limit': 1.0, 'cost': 2.0},
        {'id': 'P2', 'name': 'Standard 10GB', 'data_limit': 10.0, 'cost': 5.0},
        {'id': 'P3', 'name': 'Pro 50GB', 'data_limit': 50.0, 'cost': 15.0},
        {'id': 'P4', 'name': 'Ultra 100GB', 'data_limit': 100.0, 'cost': 25.0},
    ]

    # Segments with diff sensitivities (a = intercept, b = slope)
    # q = a - b*p
    # Low budget: High sensitivity (b high), Low intercept
    # High budget: Low sensitivity (b low), High intercept
    segments = [
        {
            'id': 'S_Low', 'name': 'Budget Users', 'size': 5000,
            'params': {
                'P1': {'a': 5000, 'b': 200},  # Willing to pay up to 25
                'P2': {'a': 4000, 'b': 200},
                'P3': {'a': 1000, 'b': 100},
                'P4': {'a': 0, 'b': 0},
            }
        },
        {
            'id': 'S_Med', 'name': 'Average Users', 'size': 3000,
            'params': {
                'P1': {'a': 1000, 'b': 50},
                'P2': {'a': 3000, 'b': 80},  # Willing to pay up to 37.5
                'P3': {'a': 2500, 'b': 60},
                'P4': {'a': 1000, 'b': 20},
            }
        },
        {
            'id': 'S_High', 'name': 'Power Users', 'size': 1000,
            'params': {
                'P1': {'a': 0, 'b': 0},
                'P2': {'a': 500, 'b': 10},
                'P3': {'a': 1000, 'b': 15},
                'P4': {'a': 1000, 'b': 10}, # Willing to pay up to 100
            }
        }
    ]

    capacity = 100000.0 # big enough default

    return plans, segments, capacity

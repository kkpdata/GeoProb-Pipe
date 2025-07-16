
def system_variable_setup(a: float, b: float, c: float):
    print(a, b, c)

def limit_state_example_1(a: float, b: float):
    return 1.9 - (a + b)

def limit_state_example_2(b: float, c: float):
    return 1.85 - (1.5 * b + 0.5 * c)


def system_variable_setup(a: float, b: float, c: float):
    """ Dummy functie waarmee variabele namen worden geïnitieerd.

    Deze staat toe dat je de distributies toevoegt aan de ReliabilityProject voordat je de systeemmodellen toevoegt.
    Je kunt in één keer alle variabelen toevoegen wat de code overzichtelijker maakt. """
    print(a, b, c)

def heave(a: float, b: float):
    return 1.9 - (a + b)  # TODO Nu

def uplift(b: float, c: float):
    return 1.85 - (1.5 * b + 0.5 * c)  # TODO Nu

def piping(b: float, c: float):
    return 1.85 - (1.5 * b + 0.5 * c)  # TODO Nu

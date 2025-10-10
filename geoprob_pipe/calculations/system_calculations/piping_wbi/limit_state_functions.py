from geoprob_pipe.calculations.limit_states.piping_lm import limit_state_wbi as system_variable_setup


# noinspection PyPep8Naming
def calc_Z_u(**kwargs) -> float:
    r"""Grenstoestandfunctie voor opbarsten (uplift).

    Returns:
        float: Z waarde van de grenstoestandfunctie voor opbarsten
    """
    return system_variable_setup(**kwargs)[0]


# noinspection PyPep8Naming
def calc_Z_h(**kwargs) -> float:
    r""" Wrapper over de grenstoestandfunctie voor heave zodat deze bruikbaar is voor de Probabilistic Library.

    Returns:
        float: Z waarde van de grenstoestandfunctie voor heave
    """
    return system_variable_setup(**kwargs)[1]


# noinspection PyPep8Naming
def calc_Z_p(**kwargs) -> float:
    r"""Grenstoestandfunctie voor het mechanisme piping

    Returns:
        float: Z waarde van de grenstoestandfunctie voor piping
    """
    return system_variable_setup(**kwargs)[2]


MODEL_NAMES = {
    calc_Z_u.__name__: "Uplift",
    calc_Z_h.__name__: "Heave",
    calc_Z_p.__name__: "Piping",
}

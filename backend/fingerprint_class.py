import random as pseudo

def random():
    outcome = pseudo.random()
    if outcome < 0.338:
        return "left loop"
    elif outcome < 0.655:
        return "right loop"
    elif outcome < 0.934:
        return "whorl"
    elif outcome < 0.971:
        return "arch"
    else:
        return "tented arch"

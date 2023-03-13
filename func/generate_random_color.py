import random


def generate_random_color():
    # generate a random hex color code
    r = lambda: random.randint(0, 255)
    color = int('0x{:02X}{:02X}{:02X}'.format(r(), r(), r()), 16)
    return color
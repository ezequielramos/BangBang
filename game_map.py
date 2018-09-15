import random

def reduceNoise(map_curve):
    for i in range(len(map_curve) - 1):
        map_curve[i] = (map_curve[i] + map_curve[i+1]) / 2

    map_curve[-1] = (map_curve[-1] + map_curve[0]) / 2

def generate(width, height, reduce_noise=1000):
    map_curve = []
    for _ in range(width):
        map_curve.append(random.randint(50, height))

    for _ in range(reduce_noise):
        reduceNoise(map_curve)

    return map_curve
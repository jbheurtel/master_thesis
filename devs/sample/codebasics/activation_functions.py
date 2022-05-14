import math


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


sigmoid(100)
sigmoid(1)


def tanh(x):
    return (math.exp(x) - math.exp(-x)) / (math.exp(x) + math.exp(-x))

tanh(1)
tanh(-1)
tanh(-10)


def relu(x):
    return max(0, x)


relu(-1)
relu(1)


def leaky_relu(x):
    return max(0.1*x, x)


leaky_relu(8)
leaky_relu(-2)



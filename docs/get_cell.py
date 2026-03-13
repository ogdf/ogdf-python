import math
bbox = GA.boundingBox()
def get_cell(n, cells=5):
    x = math.floor(GA.x[n] / ((bbox.width() + 1) / cells))
    y = math.floor(GA.y[n] / ((bbox.height() + 1) / cells))
    return x + y * cells

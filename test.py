import mathinspector
from mathinspector.plot.example import helix
from numpy import linspace

X = linspace(0,12)

mathinspector.plot(helix(X))

from scipy.cluster.hierarchy import fclusterdata
from numpy import ndarray

data = [[1,1,1],\
        [10,10,10],\
        [1.5,1.5,1.5],\
        [4,4,4],\
        [9,9,9]]

x = fclusterdata(data,0.5)

print(x)


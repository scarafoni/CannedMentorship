from scipy.cluster.hierarchy import fclusterdata, fcluster, linkage
from numpy import ndarray

data = [[1,1,1],\
        [10,10,10],\
        [1.5,1.5,1.5],\
        [4,4,4]]

x = fclusterdata(data,0.5)

distances = [9,0.5,3,8.5,6,2.5]
y = linkage(distances)
print(x)
print(fcluster(y,.9))


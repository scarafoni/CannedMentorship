from numpy import ndarray
from scipy.cluster.hierarchy import fclusterdata, fcluster, linkage
import nltk
# transforms sentences into bag of words representation
def to_bow_mat(sentences):
    # filler
    return ndarray(shape=(len(sentences),4))


# hierarchical agglomerative classification algorithm
def hac(f_mat, dist_func='holder', thresh=0.5):
    distances = []
    if dist_func == 'holder':
        return fclusterdata(f_mat,thresh)
    else:
        distances = dist_func(f_mat)
    return fcluster(linkage(distances,thresh)) 

if __name__== '__main__':
    inputs1 = [\
               'spread the peanut butter',\
               'spread the peanut butter with the knife',\
               'spread the peanut butter on the bread',\
               'get two slices of bread',\
               'get a knife'\
               ]
    f_mat1 = to_bow_mat(inputs1)
    groups = hac(f_mat=f_mat1)
    print(groups)
    
              

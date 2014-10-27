from numpy import ndarray
from scipy.cluster.hierarchy import fclusterdata, fcluster, linkage
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import *
import string

# tokenize the text for processing
# this preprocessing inspired by duke university
def preprocess(input):
    # tokenize
    lowers = text.lower()
    no_punc = lowers.translate(None, string.punctuation)
    tokens = word_tokenize(no_punc)
    # remove stop words
    filtered = [x for x in tokens if x not in stopwords.words('english')]
    # stem word
    stemmed = []
    for x in filtered:
        stemmed.append(PorterStemmer.stem(x))
    return stemmed

#tfidf in sklearn
def sk_tfidf(tokens):
    tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')



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
    print(f_mat1)
    groups = hac(f_mat=f_mat1)
    # print(groups)
    
              

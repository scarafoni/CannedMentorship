from numpy import ndarray
from scipy.cluster.hierarchy import fclusterdata, fcluster, linkage
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.stem.porter import PorterStemmer
import string


# tokenization method from duke university
def stem_tokens(tokens, stemmer):
    stemmer = PorterStemmer()
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens, stemmer)
    return stems



# lower case, tokenize, stem, put into a feature matrix
def preprocess(inputs, extraction_method='tfidf'):
    token_dict = {}
    # lower case sentences, remove punctuation
    for sentence in sentences:
        lowers = sentence.lower()
        no_punctuation = lowers.translate(None, string.punctuation)
        token_dict[file] = no_punctuation

    # tokenize
    tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')

    #create the feature matrix (tf-idf
    if extraction_method == 'tfidf':
        return tfidf.fit_transform(token_dict.values())

    return "error"


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
    
              

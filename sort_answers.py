from numpy import ndarray
from scipy.cluster.hierarchy import fclusterdata, fcluster, linkage
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.stem.porter import PorterStemmer
import string


# proprocessing inspired by duke university
def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

#tokenize and stem the text
def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stemmer = PorterStemmer()
    stems = stem_tokens(tokens, stemmer)
    return stems



# lower case, tokenize, stem, put into a feature matrix
def preprocess(inputs):
    token_dict = {}
    # lower case sentences, remove punctuation
    i = 1
    for input in inputs:
        lowers = input.lower()
        no_punctuation = lowers.translate(None, string.punctuation)
        token_dict['input '+str(i)] = no_punctuation
        i += 1

    return token_dict

def feature_extraction(inputs,extraction_method="tfidf"):
    # preprocess- no punctuation, all lowercase
    token_dict = preprocess(inputs=inputs)
    print('td',token_dict)
    #create the feature matrix
    if extraction_method == 'tfidf':
        # tokenize
        tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')
        return tfidf.fit_transform(token_dict.values())

    return "error"


# hierarchical agglomerative classification algorithm
def hac(f_mat, dist_func='default', thresh=0.5):
    distances = []
    if dist_func == 'default':
        return fclusterdata(X=f_mat.toarray(),t=thresh)
    else:
        distances = dist_func(f_mat)
    return fcluster(linkage(distances,thresh)) 

if __name__== '__main__':
    inputs1 = [\
               'Spread the peanut butter.',\
               'spread the Peanut butter with the knife.',\
               'spread the Peanut butter on the bread.',\
               'get two Slices. of bread.',\
               'get a knife.'\
               ]
    fmat1 = feature_extraction(inputs=inputs1)
    print(fmat1.toarray())
    groups = hac(f_mat=fmat1)
    print(groups)
    
              

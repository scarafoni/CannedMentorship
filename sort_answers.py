import pkg_resources
# pkg_resources.require("numpy==1.7.0")
from numpy import ndarray
from scipy.cluster.hierarchy import fclusterdata, fcluster, linkage
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN, AffinityPropagation
import nltk
nltk.data.path.append('nltk_data/')
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
    tokens = []
    # lower case sentences, remove punctuation
    i = 1
    for input in inputs:
        lowers = input.lower()
        no_punctuation = lowers.translate(None, string.punctuation)
        tokens.append(no_punctuation)
        i += 1
    return tokens

def feature_extraction(inputs,extraction_method="tfidf"):
    # preprocess- no punctuation, all lowercase
    tokens = preprocess(inputs=inputs)
    # print('td',tokens)
    #create the feature matrix
    if extraction_method == 'tfidf':
        # tokenize
        tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')
        x = tfidf.fit_transform(tokens)
        return x
    return "error"


# hierarchical agglomerative classification algorithm
def hac(f_mat, dist_func='default', thresh=0.5):
    distances = []
    if dist_func == 'default':
        return fclusterdata(X=f_mat.toarray(),t=thresh)
    else:
        distances = dist_func(f_mat)
        # print('distances',distances)
    return fcluster(linkage(distances,thresh)) 

def dbscan(f_mat,thresh=0.7):
    groups = DBSCAN(eps=thresh,min_samples=1).fit_predict(fmat1.toarray())
    return groups

def ap(fmat):
    groups = AffinityPropagation().fit_predict(fmat1.toarray())
    return groups

def filter_inputs(inputs):
    feature_mat = feature_extraction(inputs=inputs)
    # print('feature matrix',feature_mat)
    groupings = hac(f_mat=feature_mat)
    # print('groupings',groupings)

    final = []
    # run through the sentence groups
    no_redundant = list(set(groupings))
    for group in no_redundant:
        maxlen = 0
        max_in_group = ''
        for group2,input in zip(groupings, inputs):
            if group == group2 and len(input) > maxlen:
                max_in_group = input
                maxlen = len(input)
        final.append(max_in_group)
    return final
                

if __name__== '__main__':
    inputs1 = [\
               'Spread the peanut butter.',\
               'spread the Peanut butter with the knife.',\
               'spread the Peanut butter on the bread.',\
               'get two Slices. of bread.',\
               'get a knife.'\
               ]
    inputs2 = [\
                'spread the peanut butter',\
                'spread the peanut butter',\
                'get a knife.'\
              ]
    fmat1 = feature_extraction(inputs=inputs1)
    print(fmat1.toarray())
    # groups = hac(f_mat=fmat1)
    # groups = DBSCAN(eps=0.7,min_samples=1).fit_predict(fmat1.toarray())
    groups = AffinityPropagation().fit_predict(fmat1.toarray())
    print('groups',groups)
    # print(filter_inputs(inputs2))
    
              

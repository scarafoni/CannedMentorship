import pkg_resources
# pkg_resources.require("numpy==1.7.0")
from numpy import ndarray
from scipy.cluster.hierarchy import fclusterdata, fcluster, linkage
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.stem.porter import PorterStemmer
nltk.data.path.append('nltk_data/')
import string



# proprocessing inspired by duke university
def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

#tokenize and stem the text
def tokenize(text):
    print('tokenize')
    tokens = nltk.word_tokenize(text)
    print('after word tokenize')
    stemmer = PorterStemmer()
    print('new stemmer')
    stems = stem_tokens(tokens, stemmer)
    print('after stemmer')
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
        print('em')
        tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')
        print('after tfidf')
        x = tfidf.fit_transform(token_dict.values())
        print('after tfidf fit')
        return x
    return "error"


# hierarchical agglomerative classification algorithm
def hac(f_mat, dist_func='default', thresh=0.5):
    distances = []
    if dist_func == 'default':
        return fclusterdata(X=f_mat.toarray(),t=thresh)
    else:
        distances = dist_func(f_mat)
    return fcluster(linkage(distances,thresh)) 

def filter_inputs(inputs):
    feature_mat = feature_extraction(inputs=inputs)
    groupings = hac(f_mat=feature_mat)
    print('groupings',groupings)

    final = []
    # run through the sentence groups
    no_redundant = list(set(groupings))
    for group in no_redundant:
        maxlen = 0
        max_in_group = ''
        for group2,input in zip(groupings, inputs):
            if group == group2 and len(input) > maxlen:
                max_in_group = input
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
    '''
    fmat1 = feature_extraction(inputs=inputs1)
    print(fmat1.toarray())
    groups = hac(f_mat=fmat1)
    print(groups)
    '''
    print(filter_inputs(inputs2))
    
              

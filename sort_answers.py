import pkg_resources
# pkg_resources.require("numpy==1.7.0")
from numpy import ndarray
import numpy
from scipy.cluster.hierarchy import fclusterdata, fcluster, linkage
from scipy.spatial.distance import pdist
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN, AffinityPropagation
import nltk
from nltk.util import ngrams
nltk.data.path.append('nltk_data/')
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import string
from word_similarity import vec_semantic_sim
import itertools


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
# each entries is a list of the abovified words in the sentence
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


def semantic_distance_matrix(sentences,method='wn'):
    distances = []
    tokens = preprocess(inputs=sentences)
    print('tokens', tokens)
    '''
    for (v1,v2) in itertools.combinations(tokens, 2):
        dist = vec_semantic_sim(v1, v2, method)
        print('v1, v2',v1, v2, dist)
        distances.append(dist)
    
    print('distances', distances)
    '''
    for v1 in tokens:
        d= []
        for v2 in tokens:
            dist = vec_semantic_sim(v1, v2, method)
            print('v1, v2',v1, v2, dist)
            d.append(dist)
        distances.append(d)
    print('distances', distances)
    return distances

# calculate the distance matrix based on bow, 2-3 grams, semantics
def kitchen_sink(sentences):
    distances = []
    tokens = preprocess(inputs=sentences)
    tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english',ngram_range=(1,3))
    tdif_feat = tfidf.fit_transform(tokens)
    print('tdif feat',tdif_feat.toarray())
    for i in range(len(sentences)):
        for j in range (i,len(sentences)):
            if i == j: 
                continue
            distance = 0.0
            # bow, ngrams
            # numpy.concatenate((tdif_feat[i].toarray(), tdif_feat[j].toarray())))
            # print('two to compare', numpy.concatenate((tdif_feat[i].toarray(), tdif_feat[j].toarray())))
            lex_sim = float(pdist(numpy.concatenate((tdif_feat[i].toarray(), tdif_feat[j].toarray()))))
            # print('lex sim', lex_sim)
            # semantic similarities
            sem_sim = 1.0 - vec_semantic_sim(tokens[i], tokens[j])
            # print('sem sim', sem_sim)
            distances.append((lex_sim + sem_sim)/2.0)
            
    print('distances',distances)
    linkd = linkage(y=numpy.array(distances))
    # print('linkd', linkd)
    return fcluster(Z=linkd,t=0.5)
            

def feature_extraction(inputs,extraction_method="tfidf"):
    # preprocess- no punctuation, all lowercase, listified
    tokens = preprocess(inputs=inputs)

    #create the feature matrix
    if extraction_method == 'tfidf':
        # tokenize
        tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')
        x = tfidf.fit_transform(tokens)
        return x
    elif extraction_method == 'tfidf-ngrams':
        # tokenize
        tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english',\
                                ngram_range=(1,3))
        x = tfidf.fit_transform(tokens)
        return x
    else:
        return "error"
    return "error"


# hierarchical agglomerative classification algorithm
def group_up(sentences, classfn='hac', feat_dist='bow'):
    thresh = 0.5
    eps = 0.7
    damping = 0.5
    # bag of words
    # bag of words and n-grams
    # bag of words, n-grams, wn
    # wordnet
    # conceptnet
    #
    # -- not here
    # affinity propagation
    # dbscan
    
    # figure out the classification
    if feat_dist == 'bow':
        f_mat = feature_extraction(inputs=sentences,\
                                   extraction_method='tfidf')
        if classfn == 'hac':
            return fclusterdata(X=f_mat.toarray(),t=thresh) 
        elif classfn == 'dbscan':
            return DBSCAN(min_samples=1, eps=eps).fit_predict(f_mat.toarray())
        elif classfn == 'affprop':
            return AffinityPropagation(eps=0.7).fit_predict(g_mat.toarray())
        else:
            return "error"

    #bag of words and n-grams, euclidean
    elif dist_func == 'bow-ngram':
        f_mat = feature_extraction(inputs=sentences,\
                                   extraction_method='tfidf-ngrams')

        if classfn == 'hac':
            return fclusterdata(X=f_mat.toarray(),t=thresh) 
        elif classfn == 'dbscan':
            return DBSCAN(min_samples=1, eps=eps).fit_predict(f_mat.toarray())
        elif classfn == 'affprop':
            return AffinityPropagation(eps=0.7).fit_predict(g_mat.toarray())
        else:
            return "error"

    elif dist_func == 'ks':
        # in this case the f_mat is just the sentences
        distances = kitchen_sink(sentences)
        linkd = linkage(y=numpy.array(distances))
        return fcluster(Z=linked,t=thresh)

    elif dist_func == 'wn':
        distances = semantic_distance_matrix(sentences, 'wn')
        linkd = linkage(y=numpy.array(distances))
        return fcluster(Z=linked,t=thresh)
        
    elif dist_func == 'cn':
        distances = semantic_distance_matrix(sentences, 'cn')
        linkd = linkage(y=numpy.array(distances))
        return fcluster(Z=linked,t=thresh)

    # error
    else:
        return "error"

def dbscan(fmat,thresh=0.7):
    f_mat = feature_extraction(inputs=sentences,\
                               extraction_method='tfidf')
    groups = DBSCAN(eps=thresh,min_samples=1).fit_predict(fmat.toarray())
    return groups

def ap(fmat):
    f_mat = feature_extraction(inputs=sentences,\
                               extraction_method='tfidf')
    groups = AffinityPropagation().fit_predict(fmat.toarray())
    return groups

def filter_inputs(inputs):
    feature_mat = feature_extraction(inputs=inputs)
    # print('feature matrix',feature_mat)
    groupings = group_up(f_mat=feature_mat)
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
    # fmat1 = feature_extraction(inputs=inputs1)
    # print(fmat1.toarray())
    # groups = hac(f_mat=fmat1)
    # groups = DBSCAN(eps=0.7,min_samples=1).fit_predict(fmat1.toarray())
    # groups = AffinityPropagation().fit(fmat1.toarray()).fit_predict(fmat1.toarray())
    # groups = kitchen_sink(inputs2)
    # distances = semantic_distance_matrix(inputs1)
    # groups = AffinityPropagation(affinity='precomputed').fit(numpy.asarray(distances)).labels_
    # groups = DBSCAN(metric='precomputed').fit(numpy.asarray(distances)).labels_
    
    print('groups',group_up(inputs1, classfn='hac',feat_dist='bow'))
    print('groups',group_up(inputs1, classfn='dbscan',feat_dist='bow'))
    # print(filter_inputs(inputs2))
    
              

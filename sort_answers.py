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
from nltk.corpus import webtext
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import string
from word_similarity import vec_semantic_sim
import itertools
import time


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


def semantic_distance_matrix(sentences,method='wn', format='array'):
    distances = []
    tokens = preprocess(inputs=sentences)
    
    if format == 'array':
        for i in range(len(tokens)):
            for j in range(i,len(tokens)):
                if i == j:
                    continue
                dist = vec_semantic_sim(v1=tokens[i], v2=tokens[j], method=method, corpus=tokens)
                # print('v1, v2',tokens[i], tokens[j], dist)
                distances.append(dist)
         

    else:
        for v1 in tokens:
            d= []
            for v2 in tokens:
                dist = vec_semantic_sim(v1=v1, v2=v2, method=method, corpus=tokens)
                # print('v1, v2',v1, v2, dist)
                d.append(dist)
            distances.append(d)
    # print('distances', distances)
    return distances

# calculate the distance matrix based on bow, 2-3 grams, semantics
def kitchen_sink(sentences,format='array'):
    alpha = 0.8
    distances = []
    tokens = preprocess(inputs=sentences)
    tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english',ngram_range=(1,3))
    tdif_feat = tfidf.fit_transform(tokens)

    if format == 'array':
        for i in range(len(sentences)):
            for j in range (i,len(sentences)):
                if i == j: 
                    continue
                distance = 0.0
                # bow, ngrams
                lex_sim = float(pdist(numpy.concatenate((tdif_feat[i].toarray(), tdif_feat[j].toarray()))))
                # print('sentences',tokens[i],tokens[j])
                # print('lex sim', lex_sim)
                # semantic similarities
                sem_sim = 1.0 - vec_semantic_sim(v1=tokens[i], v2=tokens[j], corpus=tokens)
                # print('sem sim', sem_sim)
                distances.append((lex_sim + sem_sim)/2.0)
            
    else:
        for i in range(len(sentences)):
            row = []
            for j in range (0,len(sentences)):
                distance = 0.0
                # bow, ngrams
                lex_sim = float(pdist(numpy.concatenate((tdif_feat[i].toarray(), tdif_feat[j].toarray()))))
                # print('lex sim', lex_sim)
                # semantic similarities
                sem_sim = 1.0 - vec_semantic_sim(v1=tokens[i], v2=tokens[j],corpus=tokens)
                # print('sem sim', sem_sim)
                row.append((1-alpha*lex_sim) + ((alpha)*sem_sim))
            distances.append(row) 

    # print('distances',distances)
    return distances

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

    if feat_dist == 'bow':
        f_mat = feature_extraction(inputs=sentences,\
                                   extraction_method='tfidf')
        if classfn == 'hac':
            return fclusterdata(X=f_mat.toarray(),t=thresh) 
        elif classfn == 'dbscan':
            return DBSCAN(min_samples=1, eps=eps).fit_predict(f_mat.toarray())
        elif classfn == 'affprop':
            return AffinityPropagation(damping=damping).fit_predict(f_mat.toarray())
        else:
            return "error"

    #bag of words and n-grams, euclidean
    elif feat_dist == 'bow-ngram':
        f_mat = feature_extraction(inputs=sentences,\
                                   extraction_method='tfidf-ngrams')

        if classfn == 'hac':
            return fclusterdata(X=f_mat.toarray(),t=thresh) 
        elif classfn == 'dbscan':
            return DBSCAN(min_samples=1, eps=eps).fit_predict(f_mat.toarray())
        elif classfn == 'affprop':
            return AffinityPropagation(damping=damping).fit_predict(f_mat.toarray())
        else:
            return "error"

    elif feat_dist == 'ks':
        if classfn == 'hac':
            distances = kitchen_sink(sentences,format='array')
            linkd = linkage(y=numpy.array(distances))
            return fcluster(Z=linkd,t=thresh)
        elif classfn == 'dbscan':
            distances = kitchen_sink(sentences,format='matrix')
            return DBSCAN(min_samples=1, eps=eps, metric='precomputed').fit(numpy.asarray(distances)).labels_
        elif classfn == 'affprop':
            distances = kitchen_sink(sentences,format='matrix')
            return AffinityPropagation(damping=damping, affinity='precomputed').fit(numpy.asarray(distances)).labels_
        else:
            return "error"

    elif feat_dist in ['wn','cn']:
        if classfn == 'hac':
            distances = semantic_distance_matrix(sentences, feat_dist,format='array')
            linkd = linkage(y=numpy.array(distances))
            return fcluster(Z=linkd,t=thresh)
        elif classfn == 'dbscan':
            distances = semantic_distance_matrix(sentences, feat_dist,format='matrix')
            return DBSCAN(min_samples=1, eps=eps, metric='precomputed').fit(numpy.asarray(distances)).labels_
        elif classfn == 'affprop':
            distances = semantic_distance_matrix(sentences, feat_dist,format='matrix')
            return AffinityPropagation(damping=damping, affinity='precomputed').fit(numpy.asarray(distances)).labels_
        else:
            return "error"
        
    # error
    else:
        return "error"


def filter_inputs(inputs,classfn,feat_dist):
    feature_mat = feature_extraction(inputs=inputs)
    # print('feature matrix',feature_mat)
    groupings = group_up(inputs,classfn=classfn, feat_dist=feat_dist)
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

    # runtime tests
    ff = webtext.fileids()[0]
    #the sentences we want to sample from
    ffs = webtext.raw(ff).split('.')
    for size in[5,10,50,100]:
        for method in ['bow','ks']:
            start = time.time()
            inputs = random.sample(ffs,size)
            filtered = filter_inputs(inputs,classfn=method,feat_dist='hac')
            elapsed = time.time() - start 
            print(size,method,elapsed)
    

    ''' for testing
    with open('observations-formatted-shuffle.txt','r') as r, open('filtered_votes.txt','w') as w:
        # format the input tests into lists
        r = r.read()
        r = r.split('\n#\n')
        r = [x.split('\n') for x in r]
        
        hold = ''
        '''
        for (i,c,d) in itertools.product(r,\
                                         ['hac', 'dbscan', 'affprop'],\
                                         ['bow', 'bow-ngram','ks', 'wn','cn']):
        '''
        for (i,c,d) in itertools.product(r,\
                                         ['hac'],\
                                         ['ks']):
            start = time.time()
            filtered = filter_inputs(i,classfn=c,feat_dist=d)
            elapsed = time.time() - start
            if i != hold:
                w.write('\n###\n')
                hold = i
            w.write(c+','+d+','+str(elapsed)+'\n'+'\n'.join(filtered)+'\n\n')
    # print(filter_inputs(inputs2))
    '''
    
              

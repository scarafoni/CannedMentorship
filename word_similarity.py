# code from
# http://sujitpal.blogspot.com/2013/02/checking-for-word-equivalence-using.html
from __future__ import division
import requests
from nltk.corpus import wordnet as wn
from nltk import word_tokenize, pos_tag
import itertools as it
import sys

    
# similarity between two vectors as comparing
# all non-stop words, normalized to be between 0 and 1
# input is two vector tokens w/o stopwords
# for each word takes most similar word in other sentence
# only compares same part of speech
# normalized for total comarisons
def vec_semantic_sim(v1,v2,method='wn'):
    print('sim v1, v2',v1,v2)
    sim_acc = 0.0
    compares = 0 
    v1_pos = pos_tag(word_tokenize(v1))
    v2_pos = pos_tag(word_tokenize(v2))

    t_sim = 0.0
    for w1 in v1_pos:
        max_sim = 0.0
        for w2 in v2_pos:
            if method == 'wn':
                if w1[1] == w2[1]:
                    sim = wordnet_similarity(w1[0], w2[0])
                    if sim > max_sim:
                        max_sim = sim
            
            else:
                if w1[1] == w2[1]:
                    sim = cn_similarity(w1[0], w2[0])
                    if sim > max_sim:
                        max_sim = sim
        t_sim += max_sim

    for w1 in v1_pos:
        max_sim = 0.0
        for w2 in v2_pos:
            if method == 'wn':
                if w1[1] == w2[1]:
                    sim = wordnet_similarity(w1[0], w2[0])
                    if sim > max_sim:
                        max_sim = sim
            
            else:
                if w1[1] == w2[1]:
                    sim = cn_similarity(w1[0], w2[0])
                    if sim > max_sim:
                        max_sim = sim
        t_sim += max_sim
    print('t_sim',t_sim / float(len(v1) + len(v2)))
    return t_sim / float(len(v1) + len(v2))
     
    '''
    for (w1, w2) in it.product(v1, v2):
        if method == 'wn':
            sim_acc += wordnet_similarity(w1,w2)
        else:
            sim_acc += cn_similarity(w1,w2)
        compares += 1
    print('raw sim',sim_acc)
    '''
    return sim_acc/ float(compares)
         
    
def wordnet_similarity(w1, w2, sim=wn.path_similarity):
  synsets1 = wn.synsets(w1)
  synsets2 = wn.synsets(w2)
  sim_scores = []
  for synset1 in synsets1:
    for synset2 in synsets2:
      sim_scores.append(sim(synset1, synset2))
  if len(sim_scores) == 0:
    return 0
  else:
    return max(sim_scores)

def cn_similarity(w1, w2):
    req = requests.get('http://conceptnet5.media.mit.edu/data/5.2/assoc/c/en/'+w1+'?filter=/c/en/'+w2+'&limit=1')
    return req.json()['similar'].split(',')[1]

def main():
    (word1, word2) = ("large", "big")
    print(similarity(word1, word2))

if __name__ == "__main__":
  main()

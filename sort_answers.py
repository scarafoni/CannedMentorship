'''
meant to group similar answers received from the website
'''



if __name__== '__main':
    inputs1 = [\
               'spread the peanut butter',\
               'spread the peanut butter with the knife',\
               'spread the peanut butter on the bread',\
               'get two slices of bread',\
               'get a knife'\
               ]
    f_mat1 = get_features(inputs1)
    groups = cluster(f_mat1)
    print(groups)
    
              

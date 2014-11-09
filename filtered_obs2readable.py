with open('filtered_votes.txt','r') as r, open('readable_filtered.txt','w') as w:
    votes = r.read()
    votes = votes.split('\n\n\n###\n')
    # line split
    votes = [x.split('\n') for x in votes]
    #change the first line
    for i in range(len(votes)):
        first_line = votes[i][0].split(',')
        # remove the time, replace with 
        first_line[-1] = 'Rating: _______'
        # add the algorithm number
        first_line.insert('Algorithm '+str(i))
        # join all the arlgotithms by newline
        first_line = ', '.join(first_line)
        votes[i] = '\n'.join(votes)
    

      

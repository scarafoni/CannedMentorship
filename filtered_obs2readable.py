with open('filtered_votes.txt','r') as r, open('readable_filtered.txt','w') as w:
    votes = r.read()
    votes = votes.split('\n###\n')
    # line split
    votes = [x.split('\n') for x in votes]
    #change the first line
    for i in range(len(votes)):
        k =1
        for j in range(len(votes[i])):
            if len(votes[i][j].split(',')) > 2:
                first_line = votes[i][j].split(',')
                # remove the time, replace with 
                first_line[-1] = 'Rating: _______'
                # add the algorithm number
                first_line.insert(0, 'Algorithm '+str(k))
                k += 1
                # join all the arlgotithms by newline
                first_line = ', '.join(first_line)
                votes[i][j] = first_line
        votes[i] = '\n'.join(votes[i])
        w.write(votes[i])
    
    

      

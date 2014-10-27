CannedMentorship
================

master's thesis project

Dependencies
============
    -flask 0.10.0
    -redis, redis server
    -nltk
    -scipy
    scikit-learn

flow
========
  -login
    -increment totaly players
    -for i form 0 to tp
        assign if i not in ids
    -register in id list
  
  -logout
    decrement tp
    remove id from list
        -find
               -starting state
               -leader can propose instruct, then goes to write
               -sent- instructions, state, leader
        -write
                -users can write then send instructions
                -changes to vote when all user's input received
                -sent: instructions, state, leader
        -vote  
               -users vote on instructions
               -goes to find when all votes are in
               -sent- instructions, state, leader vote options
        -vote_finish
                -accessed from find
                -ends when all users input is in
                -goes to find on fail, on suceed finish
                sent- instructions, state, leader
        -finish
                -stuck once in this state
                -sent- instructions, state, leader
switches
    find -> write
        -nothing
        -func: propose_instruct()
    write -> vote
        -run ai on inputs, send to choices
        -wipe inputs, input_ids
        -func- get_inst_text()
    vote -> find
        -run vote, push to instructions
        -wipe inputs, input_ids
        -wipe choices
        -func- send_my_vote()
    find -> vote_finish
        -nothig todo
        -func: receive_finish()
    vote_finish -> finish
        -delete input, input ids
        -nothing todo
        -func- vote_finish()
    vote_finish -> find
        -delete input, input_ids
        
vars
    -next-id: the next available id
    -registered_ids
        -ids in use
    -choices- choices to vote for
    -state
    -inputs- input so far
    -input_ids- ids of the above
    -total_players
    -leader
    -instructions- list of instructions


        
                
        
AI part
    -helper functions
        -preprocess
            -lower case
            -punctuation
            -to dict
        -return tokendict
        
    -feature extraction
      -tfidf   
        -uses tokenize
        *idea*
        -use another corpus to augment and remove after 
        -hybrid bow/ngrams 
        
        
    -clustering
        -hac
            -default clustering: takes data, uses hac w/ dist = eucledian
            *below not implemented*
            -distance=something with semantic distance
        -affinity propagation
            -scikitlearn

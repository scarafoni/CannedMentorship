CannedMentorship
================

master's thesis project

Dependencies
============
    -flask 0.10.0
    -redis, redis server

flow
========
        -find
               -starting state
               -leader can propose instruct, then goes to write
               -sent- instructions, state
        -write
                -users can write then send instructions
                -changes to vote when all user's input received
                -sent: instructions, state
        -vote  
               -users vote on instructions
               -goes to find when all votes are in
               -sent- instructions, state, vote options
        -vote_finish
                -accessed from find
                -ends when all users input is in
                -goes to find on fail, on suceed finish
        -finish
                -stuck once in this state
switches
    find -> write
        -nothing
    write -> vote
        -run ai on inputs, send to choices
        -wipe inputs, input_ids
    vote -> find
        -wipe inputs, input_ids
        -wipe choices
    find -> vote_finish
        -nothig todo
    vote_finish -> finish
        -nothing todo
        
vars
    -choices- choices to vote for
    -state
    -inputs- input so far
    -input_ids- ids of the above
    -total_players
    -leader


        
                
        

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
    -choices- choices to vote for
    -state
    -inputs- input so far
    -input_ids- ids of the above
    -total_players
    -leader
    -instructions- list of instructions


        
                
        

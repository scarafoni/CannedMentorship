/* 
 * contains all the code for updating the app as the game goes on
 */

//activate, deactivate button color
function activateBtn(btn) {
    $('#'+btn).removeClass('btn-default');
    $('#'+btn).addClass('btn-primary');
}

function deactivateBtn(btn) {
    $('#'+btn).addClass('btn-default');
    $('#'+btn).removeClass('btn-primary');
}

//update the voting choices
function updateChoices(data) {
    if(data.choices) {
        var d = data.choices;
        console.log(data.choices);
        var votes = '';
        for(var i in d) { 
            votes += '<tr ><td id='+i+'><a href="#" class="list-group-item active" >'+d[i]+'</a></td></tr>';
        }
        $('#voteTable tbody').html(votes); 

        //send vote 
        $(function() { 
            $('#voteTable td').bind('click', function() {
                u_choice: $(this).attr('id'),
                u_id: String(id)
                ws.send('{ "u_choice" : "'+u_choice+'", "u_id" : "'+u_id+'"}')
                }, function(data) {
                    alert(data.result);
                });
            });
        });
    } else {
        $('#voteTable tbody').html(''); 
    }
}

//am i leader?
function updateLeader(data) {
    if(data.leader) {
        leader = true;
        $('#amILeadDiv').html('You are leader'); 
    } else {
        leader = false;
        $('#amILeadDiv').html('You are not leader (don\'t worry about what this means, it\'s not important'); 
    }
}

//updates the state and the interface accordingly
function updateState(data) {
    updateVoteFinishArea(data.state);
}

//update the voteFinish area if it's the right part of the game
function updateVoteFinishArea(state) {
	if(state == 'vote_finish') {
	  $('#voteFinish').html('<button id="yesfinish" type="button" class="btn btn-primary">finish</button><button id="nofinish" type="button" class="btn btn-primary">don\'t finish</button>');
		//vote yes or no to finish
		$(function() {
			$('#yesfinish').bind('click', function() {
				$.getJSON('/vote_finish', {
					u_id: String(id),
					u_vote: 'yes'
			}, function(data) {
				alert('thank you, vote received');
			   });
			return false;
			});
		});

		$(function() {
			$('#nofinish').bind('click', function() {
				$.getJSON('/vote_finish', {
					u_id: String(id),
					u_vote: 'no'
			}, function(data) {
				alert('thank you, vote received');
			   });
			return false;
			});
		});
	} else {
		$('#voteFinish').html('');
	}
}

// update the directions for the player
function updateUserDirections(data) {
    switch(data.state) {
        case 'find':
            activateBtn('finishButton');
            if(data.leader) {
                curr_inst = 'propose a new instruction!';
                activateBtn('proposeInstructButton');
            }
            else {
                curr_inst = 'wait for the leader to propose a new instruction!';
            }
            break;
        case 'write':
            curr_inst = '';
            if(!data.gotMyInput)
                curr_inst = 'write the instruction for this step';
            else
                curr_inst = "your input received! please wait for the others";
            curr_inst += " "+data.inputs_so_far+'/'+data.total_players+' have proposed so far';

            activateBtn('sendProp');
            break;
        case 'vote':
            curr_inst = '';
            if(!data.gotMyInput)
                curr_inst = 'vote on which step you think is best';
            else
                curr_inst = "your input received! please wait for the others";
            curr_inst += " "+data.inputs_so_far+'/'+data.total_players+' have voted so far';
    ;
            break;
        case 'vote_finish':
            curr_inst = '';
            if(!data.gotMyInput)
                curr_inst = 'someone believes the instructions are finished, do you agree?';
            else
                curr_inst = "your vote is received! please wait for the others";
            curr_inst += " "+data.inputs_so_far+'/'+data.total_players+' have voted so far';

            break;
        case 'finish':
            curr_inst = 'the instructions are finished, thank you for your input!';
            break;
        default:
            curr_inst = 'error';
            break;
    }
    console.log(curr_inst);
    $("#currDirections").html(curr_inst);
}

import cm_backend
import sort_answers
from collections import Counter
import gevent
from flask.ext.mail import Mail, Message
import time
import json
import unicodedata

class cmBackend(object):
    """the backend for cm: coordinates all the info"""

    def __init__(self):
        self.clients = []
        self.state = 'find'
        self.previous_state = 'find'
        self.instructions = []
        self.leader = None
        # proposed instructions this round
        self.proposals = []
        # voting on propositions info
        self.proposal_votes = []
        # votes on whether to stop
        self.finish_votes = []
        self.start_time = time.time()

    def list_from_str(self, str):
        """gets the specified list from the string"""
        if str == 'proposals':
            return self.proposals
        elif str == 'proposal_votes':
            return self.proposal_votes
        elif str == 'finish_votes':
            return self.finish_votes
        else:
            return 'error'

    def curr_time(self,):
        '''gets the current time (difference from start)'''
        return time.time() - self.start_time

    def client_in_input(self, client, input_list):
        '''returns if the client is in the input list'''
        return client in [x.user for x in input_list]

    def register(self, client):
        '''registers a user'''
        if len(self.clients) == 0:
            self.leader = client
        self.clients.append(client)

    def unregister(self, client):
        '''unregisters a user'''
        self.clients.remove(client)

    def run_ai(self, props):
        '''run the ai sorter on the propositions'''
        vals = [x.val for x in props]
        print('raw votes', vals)

        # sort them
        sorted = sort_answers.filter_inputs([ \
                                                unicodedata.normalize('NFKD', x).encode('ascii','ignore') \
                                                for x in vals ])
        uni_sorted = [unicode(x) for x in sorted]
        print('uni sorted', uni_sorted)
        toret = []
        added = []
        for i in props:
            if i.val in uni_sorted and i.val not in added:
                added.append(i.val)
                toret.append(i)
                # print('toret is now {}'.format(toret)

        # mail the results to myself
        msg = Message(
                'raw votes',
                sender = 'cannedMentorship@gmail.com',
                recipients= ['dan@scarafoni.com'])
        msg.body = '\n'.join(vals)
        with app.app_context():
            mail.send(msg)
        return toret


    def count_votes(self, vote_list, votes):
        '''count a list of votes, return the most popular'''
        # print('count_votes',votes,vote_list)
        votes_v = [x.val for x in votes]
        vote_list_v = [x.val for x in vote_list]
        print("votes: {}, vote_list: {}".format(votes_v, vote_list_v))
        counts = [0] * len(votes_v)

        for choice in votes_v:
            counts[int(choice)] += 1
        i = counts.index(max(counts))
        most_popular = vote_list[i]
        return most_popular

    def add_input(self, user, input, list):
        '''adds user input to the database'''
        list_input = self.list_from_str(list)
        print('listinput', list_input)
        # print "try to add {} to list {}".format(input, list)

        # add to the list of proposals
        if self.state == 'write' and list == 'proposals' and not self.client_in_input(client=user,input_list=list_input):
            self.proposals.append(Input(user, input, self.curr_time()))

        # add to the list of votes for proposals
        elif self.state == 'vote' and list == 'proposal_votes' and not self.client_in_input(client=user,input_list=list_input):
            self.proposal_votes.append(Input(user, input, self.curr_time()))

        # add to the list of votes to finish
        elif self.state == 'vote_finish' and list == 'finish_votes' and not self.client_in_input(client=user,input_list=list_input):
            self.finish_votes.append(Input(user, input, self.curr_time()))

        else:
            print('cant add to list {} in state {}'.format(list, self.state))


    def send(self, client, data):
        '''send data to a client'''

        client.send(data)

    def update_backend(self):
        '''updates the backend state as needed'''

        # print "update state: {} #props: {}".format(self.state, len(self.proposal_votes))
        # change write -> vote if the props are in
        if self.state == 'write' and \
                        len(self.proposals) == len(self.clients):
            self.proposals = self.run_ai(self.proposals)
            self.state = 'vote'

        # change vote -> find if all the votes are in
        elif self.state == 'vote' and \
                        len(self.proposal_votes) == len(self.clients):
            self.instructions.append(self.count_votes(self.proposals, \
                                                      self.proposal_votes))
            self.proposals = []
            self.proposal_votes = []
            self.state = 'find'

        # change vote_finish -> finish / write if votes are in
        elif self.state == 'vote_finish' and \
                        len(self.finish_votes) == len(self.clients):
            finish_vals = [x.val for x in self.finish_votes]
            counter = Counter(finish_vals)
            winner = counter.most_common()[0][0]
            print('and the winner is: {}'.format(winner))
            self.state = 'find' if winner == 'no' else 'finish'
            self.finish_votes = []

            # send the message as a mail
            if self.state == 'finish':
                msg = Message(
                        'final instructions',
                        sender = 'cannedMentorship@gmail.com',
                        recipients= ['dan@scarafoni.com'])
                inst = [x.val for x in cmbe.instructions]
                msg.body = '\n'.join(inst)
                with app.app_context():
                    mail.send(msg)



    def run(self):
        '''send updates to the clients'''
        while True:
            self.update_backend()
            for client in self.clients:
                to_send = {}

                if self.state == 'write':
                    to_send['got_my_input'] = \
                        self.client_in_input(client, self.proposals)
                    to_send['inputs_so_far'] = len(self.proposals)


                elif self.state == 'vote':
                    to_send['got_my_input'] = \
                        self.client_in_input(client, self.proposal_votes)
                    to_send['inputs_so_far'] = len(self.proposals)
                    to_send['choices'] = \
                        [x.val for x in self.proposals]
                    to_send['inputs_so_far'] = len(self.proposal_votes)

                elif self.state == 'vote_finish':
                    to_send['inputs_so_far'] = len(self.finish_votes)
                    to_send['got_my_input'] = \
                        self.client_in_input(client, self.finish_votes)

                to_send['instructions'] = \
                    [x.val for x in self.instructions]
                to_send['total_players'] = len(self.clients)
                to_send['state'] = self.state
                to_send['leader'] = client == self.leader
                # convert to_send to json
                to_send = json.dumps(to_send)

                gevent.spawn(self.send, client, to_send)
            gevent.sleep(seconds=1)

    def start(self):
        print('starting server')
        gevent.spawn(self.run)

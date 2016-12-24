from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse
from .views import CreateGameView, JoinGameView, PlayCardsView, DeckListView, PlayListView, GameStateView, HandView, PickWinnerView
from .models import _load_decks
from rest_framework.test import APIRequestFactory, force_authenticate
import json
# Create your tests here.

class APITest(TestCase):
    rf = APIRequestFactory()

    def request_list_decks(self):
        request = self.rf.get(reverse('list-decks'))
        return DeckListView.as_view()(request)

    def request_create_game(self, data):
        request = self.rf.post(reverse('create-game'), data)
        return CreateGameView.as_view()(request)

    def request_join_game(self,join_id, data):
        request = self.rf.post(reverse('join-game', kwargs={'join_id':join_id}),data)
        return JoinGameView.as_view()(request, join_id)

    def request_get_hand(self,auth, join_id):
        request = self.rf.get(reverse('hand', kwargs={'join_id':join_id}))
        request.META['Authorization'] = "token %s"%auth
        return HandView.as_view()(request, join_id)

    def request_play_cards(self,auth, join_id, data):
        url = reverse('play-cards', kwargs={'join_id':join_id})
        request = self.rf.post(url, data)
        request.META['Authorization'] = "token %s"%auth
        return PlayCardsView.as_view()(request, join_id)

    def request_list_plays(self, join_id):
        request = self.rf.get(reverse('list-plays', kwargs={'join_id':join_id}))
        return PlayListView.as_view()(request)

    def request_game_state(self, join_id):
        request = self.rf.get( reverse('game-state', kwargs={'join_id':join_id}) )
        return GameStateView.as_view()(request, join_id)

    def request_pick_winner(self, auth, join_id, data):
        request = self.rf.post( reverse('pick-winner', kwargs={'join_id':join_id,} ), data)
        request.META['Authorization'] = "token %s"%auth
        return PickWinnerView.as_view()(request, join_id)

    def render_response(self, response):
        response.render()
        return response

    def get_json(self, response):
        response.render()
        return json.loads(response.content)

    def setUp(self):
        _load_decks()

    def xtest_create_game(self):
        valid_data = {
            'name': "George",
            'num_players': 3,
            'num_points': 7,
            'decks[]':[0,1,2,3,4,5,6]
        }
        invalid_data = {
            'num_players': 3,
            'num_points': 7,
            'decks[]':[0,1,2,3,4,5,6]
        }

        response = self.request_create_game(invalid_data)
        response.render()
        self.assertEqual(response.status_code, 400, "CreateGameView accepted an invalid set of params")

        response = self.request_create_game(valid_data)
        response.render()
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200, "CreateGameView returned an incorrect status code")

        return content

    def xtest_join_game(self):
        create_game_output = self.test_create_game()
        george_player = create_game_output['player']
        join_id = create_game_output['game']['join_id']

        leo_data = {'name':'leo'}
        roopa_data = {'name':'roopa'}
        josh_data = {'name':'josh'}

        leo_response = self.request_join_game(join_id, leo_data)
        roopa_response = self.request_join_game(join_id, roopa_data)
        josh_response =  self.request_join_game(join_id, josh_data)


        leo_response.render()
        self.assertEqual(leo_response.status_code, 200, "JoinGameView returned an incorrect status code")
        roopa_response.render()
        self.assertEqual(roopa_response.status_code, 200, "JoinGameView returned an incorrect status code")
        josh_response.render()
        self.assertEqual(josh_response.status_code, 400, "JoinGameView returned an incorrect status code")

        return [create_game_output], map(json.loads, (leo_response.content, roopa_response.content,))

    def test_whole_game(self):
        #  Need to break this up into independant tests
        #  The goal of this mega test is to roughly test all api views, as well as working out the models
        game_data = {
            'name': "George",
            'num_players': 3,
            'num_points': 2,
            'decks[]':[1,2,3,4,5]
        }
        response = self.request_create_game(game_data)
        response.render()
        create_game_output = json.loads(response.content)

        join_id = create_game_output['game']['join_id']

        other_players = ['leo', 'roopa']
        leo_data, roopa_data = map(lambda name: {'name':name}, other_players)
        leo_response, roopa_response = map(lambda data: self.request_join_game(join_id, data), [leo_data, roopa_data])
        map(lambda response:response.render(), [leo_response, roopa_response])
        leo_content, roopa_content = map(lambda response:json.loads(response.content), [leo_response, roopa_response])
        george_auth_token = create_game_output['player']['auth_token']
        george_auth_token, leo_auth_token, roopa_auth_token = map(
            lambda content:content['player']['auth_token'],
            [create_game_output, leo_content, roopa_content]
        )
        game = self.get_json( self.request_game_state(join_id) )
        george_hand, leo_hand, roopa_hand = map(self.get_json, map(lambda auth:self.request_get_hand(auth, join_id), [george_auth_token,leo_auth_token,roopa_auth_token]))

        # George and Roopa Play
        num_picks = game['game']['current_black_card']['picks']
        george_picks, roopa_picks = map(lambda a:a[:num_picks],[george_hand, roopa_hand])
        george_pick_ids, roopa_pick_ids = map(lambda b: map(lambda a: a['id'], b), [george_picks, roopa_picks])
        print self.get_json(self.request_play_cards(george_auth_token, join_id, {'cards[]':george_pick_ids}))
        print self.get_json(self.request_play_cards(roopa_auth_token, join_id, {'cards[]':roopa_pick_ids}))
        # George tries to cheat by voting for Roopa out-of-turn
        response = self.request_pick_winner(george_auth_token, join_id, {'player':roopa_content['player']['id']})
        self.assertNotEqual(response.status_code, 200, "PickWinnerView allowed out-of-turn voting")
        # Leo Votes for George
        response = self.get_json(
            self.request_pick_winner(
                leo_auth_token, join_id, {'player':create_game_output['player']['id']}))
        #  New round started. Roopa is card czar. George and Leo Play
        game = self.get_json( self.request_game_state(join_id) )
        george_hand, leo_hand, roopa_hand = map(self.get_json, map(lambda auth:self.request_get_hand(auth, join_id), [george_auth_token,leo_auth_token,roopa_auth_token]))
        num_picks = game['game']['current_black_card']['picks']
        george_picks, leo_picks = map(lambda a:a[:num_picks],[george_hand, leo_hand])
        george_pick_ids, leo_pick_ids = map(lambda b: map(lambda a: a['id'], b), [george_picks, leo_picks])
        print self.get_json(self.request_play_cards(george_auth_token, join_id, {'cards[]':george_pick_ids}))
        print self.get_json(self.request_play_cards(leo_auth_token, join_id, {'cards[]':leo_pick_ids}))
        # Roopa Votes for Roopa, in clear violation of the rules.
        response = self.request_pick_winner(roopa_auth_token, join_id, {'player':roopa_content['player']['id']})
        self.assertNotEqual(response.status_code, 200, "PickWinnerView allowed self voting")
        # Unsuccessful, she votes for George to end the game in protest
        response = self.get_json(
            self.request_pick_winner(
                roopa_auth_token, join_id, {'player':create_game_output['player']['id']}))
        #  The game is now over
        game = self.get_json( self.request_game_state(join_id) )
        self.assertEqual(game['game']['game_state'], "game_over", "PickWinnerView did not change state to game_over")

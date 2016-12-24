from django.shortcuts import render
from .models import Card, Deck, Game, Player, PlayCard
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import ValidationError, NotFound, NotAcceptable, AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
# Create your views here.


class NullAuthentication(BaseAuthentication):
    def authenticate(self, request):
        return (AnonymousUser(), None)


#  Lazy home-baked Auth. Should replace with oauth
class PlayerAuthentication(BaseAuthentication):
    def authenticate(self, request):
        try:
            token = request.META['Authorization']
        except KeyError:
            raise NotAcceptable()
        token = token.split()
        if token[0] != "token":
            raise NotAcceptable()
        try:
            player = Player.objects.get(auth_token=token[1])
        except Player.DoesNotExist:
            return None

        user = AnonymousUser()
        user.player = player
        return (user, None)


def enforce_required_params(required_params, data):
    has_required_params = all(((param in data.keys()) for param in required_params))
    if not has_required_params:
        missing_params = filter(lambda p: p not in data.keys(), required_params)
        raise ValidationError({'error': "Missing Required Params",
                                   'value': missing_params},400)


class DeckListView(APIView):
    authentication_classes = [NullAuthentication]

    def get(self, request):
        return Response(map(lambda deck: deck.get_dict(), Deck.objects.all()))


# create game
class CreateGameView(APIView):
    """
    Creates a new game, and player, returns both
    num_players - The number of players (Integer between 3 and 8 inclusive)
    num_points - The number of points to play to until game is won (Integer greater than 3  q)

    """
    authentication_classes = [NullAuthentication]

    def post(self, request):
        data = request.data
        enforce_required_params(['num_players', 'num_points', 'name', 'decks[]'], data)
        game=Game.objects.create(num_players=data['num_players'], win_points=data['num_points'])
        player=Player.objects.create(name=data['name'], game=game)
        game.host = player
        decks = Deck.objects.filter(id__in=data.getlist('decks[]'))
        game.decks.add(*decks)
        game.card_czar = player
        game.save()
        # build response
        return Response({
            'player':player.get_dict(show_private=True),
            'game':game.get_dict()})


class JoinGameView(APIView):
    authentication_classes = [NullAuthentication]

    def post(self, request, join_id):
        try:
            game = Game.objects.get(join_id=join_id)
        except Game.DoesNotExist:
            raise NotFound("Invalid join_id",404)

        if game.game_state != 'starting':
            raise ValidationError("You can no longer join this game")

        data = request.data
        enforce_required_params(['name'],data)
        player = Player.objects.create(name=data['name'], game=game)
        if game.num_players == game.players.count():
            game.game_state = 'pick_wc'
            game.save()
            game.start_new_round()

        return Response({
            'player':player.get_dict(show_private=True),
            'game':game.get_dict()})


class GameStateView(APIView):
    authentication_classes = [NullAuthentication]

    def get(self, request, join_id):
        #import pdb; pdb.set_trace()
        try:
            game = Game.objects.get(join_id=join_id)
        except Game.DoesNotExist:
            raise NotFound("Invalid join_id",404)

        return Response({'game':game.get_dict()})

# get hand
  # check player auth_token
  # return player hand


class HandView(APIView):
    authentication_classes = [PlayerAuthentication]

    def get(self, request, join_id):
        player = request.user.player
        cards = map(lambda card: card.get_dict(), player.hand.all())
        return Response(cards)

# play cards
  # check gamestate is pick_wc and player not card_czar
  # check if num cards played == current_black_card.pick
  # create PlayCards for round
  # check if all players have played, if so, update gamestate


class PlayCardsView(APIView):
    authentication_classes = [PlayerAuthentication]

    def post(self, request, join_id):
        data = request.data
        enforce_required_params(['cards[]'], data)
        player = request.user.player
        cards = data.getlist('cards[]')
        game = request.user.player.game
        if game.game_state != "pick_wc":
            raise ValidationError({'error':"Unable to play cards at this moment"},400)
        if game.current_black_card.pick != len(cards):
            raise ValidationError({'error':"incorrect number of decks", 'value':cards},400)
        playcards = map(lambda card:PlayCard(player=player, card_id=card), cards)
        PlayCard.objects.bulk_create(playcards)
        if game.players_played_count() == game.num_players - 1: #  if everyone except the cardczar has played, state change
            game.game_state = "pick_win"
            game.save()
        return Response({'status':"success"})


# pick winner
class PickWinnerView(APIView):
    authentication_classes = [PlayerAuthentication]

    def post(self, request, join_id):
        data = request.data
        enforce_required_params(["player"], data)
        player = request.user.player
        game = player.game
        if game.game_state != "pick_win":
            raise ValidationError({'error':"Unable to pick winner at this moment"},400)
        game.save() # can be deleted if this method has atomic transactions
        if game.card_czar != player:
            raise ValidationError({'error':"YOU ARE NOT MY SUPERVISOR! Er, Card Czar"}, 400)
        try:
            winner = game.players.get(id=data['player'])
        except Player.DoesNotExist:
            raise ValidationError({'error': "Player does not exist"}, 400)
        if player == winner:
            raise ValidationError({'error':"Self Voting is ILLEGAL!"})
        winner.awesome_points += 1
        winner.save()
        game.last_round_winner = winner
        if winner.awesome_points == game.win_points:
            game.game_state = "game_over"
        else:
            game.game_state = "pick_wc"
        game.save()
        game.start_new_round()
        return Response({'status':"success"})

class PlayListView(APIView):
    authentication_classes = [PlayerAuthentication]

    def get(self, request, join_id):
        game = request.player.game
        players_who_played = game.players.exclude
        plays = (
            (player.as_dict(), map(lambda card: card.as_dict(), player.current_play.all()))  #  (player, [{card1}...{card-n}])
            for player in players_who_played)
        return Response({
            'ready': True if game.game_state == "pick_win" else False,
            'plays': plays
        })

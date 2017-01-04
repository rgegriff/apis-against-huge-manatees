from __future__ import unicode_literals
import uuid, random

from django.db import models

import positions

# Create your models here.

CARDS_IN_HAND = 7


class Deck(models.Model):
    name = models.CharField(max_length=255)
    official = models.BooleanField()
    icon = models.CharField(max_length=255, blank=True, null=True)

    def get_dict(self):
        return {'id':self.pk, 'name':self.name,'official':self.official, 'icon':self.icon}

    def __unicode__(self):
        return self.name


class Card(models.Model):
    deck = models.ForeignKey("cah.Deck")
    whitecard = models.BooleanField()
    pick = models.IntegerField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)

    def get_dict(self):
        as_dict = {'id':self.pk,
                  'text':self.text,
                  'deck':self.deck_id}
        if not self.whitecard:
            as_dict['picks'] = self.pick

        return as_dict

    def __unicode__(self):
        return self.text


class PlayCard(models.Model):
    player = models.ForeignKey("cah.Player")
    position = positions.PositionField()
    card = models.ForeignKey("cah.Card")


class Player(models.Model):
    class Meta:
        ordering = ("position",)

    auth_token = models.UUIDField(default=uuid.uuid4) # we will assign this on join, and check on player actions
    game = models.ForeignKey("cah.Game", related_name="players")
    position = positions.PositionField(collection="game")
    name = models.CharField(max_length=60)
    hand = models.ManyToManyField("cah.Card")
    last_action_at = models.DateTimeField(auto_now=True)
    awesome_points = models.IntegerField(default=0)
    current_play = models.ManyToManyField("cah.Card", through=PlayCard, related_name="_player_play")

    def fill_hand(self):
        '''
        draws cards randomly from deck until hand full
        Returns: Eventually
        '''
        num_cards_to_draw = CARDS_IN_HAND - self.hand.count()
        self.hand.add(*self.game.draw(num_cards_to_draw))


    def __unicode__(self):
        return "[%d]%s"%(self.game_id, self.name)

    def get_dict(self, show_private=False):
        as_dict = {
            'id': self.id,
            'name': self.name,
            'awesome_points': self.awesome_points
        }
        if show_private:
            as_dict['auth_token'] = self.auth_token

        return as_dict


class Game(models.Model):
    GAME_STATES = (("starting", "Starting"),
                   ("pick_wc", "Waiting for Players To Pick White Cards"),
                   ("pick_win", "Waiting for Card Czar to Pick Winner"),
                   ("game_over", "Game Over"))

    join_id = models.UUIDField(default=uuid.uuid4)
    last_round_winner = models.ForeignKey("cah.Player", related_name="_game_last_round_winner", null=True)
    num_players = models.IntegerField(default=3)
    win_points = models.IntegerField(default=7)
    has_started = models.BooleanField(default=False)
    game_state = models.CharField(max_length=3, default="starting", choices=GAME_STATES)
    current_black_card = models.ForeignKey(Card, null=True, blank=True, related_name="_current_black_card_games")
    host = models.ForeignKey(Player, related_name="_game_host", null=True)
    discarded = models.ManyToManyField("cah.Card")
    card_czar = models.ForeignKey("cah.Player", related_name="_card_czar_game", null=True, blank=True)
    decks = models.ManyToManyField("cah.Deck")

    def get_dict(self, show_private=True):
        as_dict = {
            'game_id': self.pk,
            'join_id': self.join_id,
            'last_round_winner': None if self.last_round_winner is None else self.last_round_winner.get_dict(),
            'num_players': self.num_players,
            'win_points': self.win_points,
            'has_started': self.has_started,
            'game_state': self.game_state,
            'players': map(lambda player: player.get_dict(), self.players.all()),
            'card_czar': self.card_czar.get_dict(),
            'decks': map(lambda d: d.get_dict(), self.decks.all())
        }
        if self.current_black_card is not None:
            as_dict['current_black_card'] = self.current_black_card.get_dict()
        else:
            as_dict['current_black_card'] = None
        return as_dict

    def players_played_count(self):
        return self.players.exclude(current_play=None).count()

    def draw(self, num_cards_to_draw):
        cards = Card.objects.filter(deck__in=self.decks.all(), whitecard=True)\
                            .exclude(id__in=self.discarded.all()).order_by("?")[:num_cards_to_draw]

        self.discarded.add(*cards)
        return cards

    def pick_new_black_card(self):
        if self.current_black_card is not None:
            self.discarded.add(self.current_black_card)
        return Card.objects.filter(deck__in=self.decks.all(), whitecard=False)\
                                              .exclude(id__in=self.discarded.all()).order_by("?")[0]


    def start_new_round(self):
        self.card_czar.position = -1
        self.card_czar.save()
        players = self.players.all()
        # select new card_czar
        self.card_czar = self.players.first()
        # this loop is dumb.
        for player in players:
            player.current_play.clear()
            player.fill_hand()

        self.current_black_card = self.pick_new_black_card()
        self.save()


def _load_decks():
    """
    Convenience procedure for loading in the json data from http://www.crhallberg.com/cah/json
    It's shitty because you run it once. {excuses, excuses}
    Returns: NOTHING !!!!!
    """
    import os
    import json

    is_official = lambda deck_dict: deck_dict['name'][0] == "["  # We can use this to test if a deck is official

    app_dir = os.path.dirname(__file__)
    card_db = json.loads(file(os.path.join(app_dir, "card_db.json"), 'r').read())
    deck_keys = card_db['order']
    for deck_key in deck_keys:
        deck_dict = card_db[deck_key] # Deck Dict. Deck Dict. Deck Dict.
        icon = deck_dict.get('icon', None) # Some decks don't have an icon
        deck = Deck(name=deck_dict['name'],
                    official=is_official(deck_dict),
                    icon=icon)
        deck.save()
        cards = []
        # at this point, deck isn't a real word to me.
        for white_card_idx in deck_dict['white']:
            cards.append(Card(deck=deck,
                        whitecard=True,
                        text=card_db['whiteCards'][white_card_idx]))

        for black_card_idx in deck_dict['black']:
            card_dict = card_db['blackCards'][black_card_idx]
            cards.append(Card(deck=deck,
                        whitecard=False,
                        pick=card_dict['pick'],
                        text=card_dict['text']))

        Card.objects.bulk_create(cards)

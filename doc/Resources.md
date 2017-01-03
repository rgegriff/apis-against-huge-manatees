#Resources
This document contains all of the individual resources that comprise the game.

##Whitecard

###Example:
    {
      "id" : 52,
      "text" : "My 1337 JS skillz",
      "deck" : 1
    }

###Fields

-  `id` - The id of the card
-  `text` - The text displayed on the front of the card
-  `deck` - the id of the deck this card belongs to



##Blackcard

###Example:
    {
      "id" : 89,
      "text" : "__? That's always going to put people off.",
      "deck" : 1,
      "picks" : 1
    }

###Fields

-  `id` - The id of the card
-  `text` - The text displayed on the front of the card
-  `deck` - the id of the deck this card belongs to
-  `picks` - the number of white cards to submit for this black card.


##Deck

###Example:
    {
      "id":1,
      "name": "Base Deck",
      "official": true,
      "icon": None
    }
    
###Fields

-  `id` - The id of this deck
-  `name` - The name of this deck
-  `official` - A boolean representing if this is an official CAH expansion
-  `icon` - a number, or the name of a font-awesome icon, as chosen by [this guy](http://www.crhallberg.com/cah/json).


##Player

###Examples:
    {
      "id": 1,
      "name": "George",
      "awesome_points": 3,
      "auth_token": "179118de-dccb-4e7a-8285-7de484f098e8"
    }
    
    {
      "id": 9,
      "name": "Leo",
      "awesome_points": 6
    }
    
###Fields
-  `id` - The id of the player
-  `name` - The player's chosen name
-  `awesome_points` - The number of points the player has won
-  `auth_token` - The token to send in the Authorization header in order to perform actions as this player. n.b. This field is only sent by the server once on player join, or new game creation.


##Game

###Example:
    {
      "game_id": 1,
      "join_id": "179118de-dccb-4e7a-8285-7de484f098e8",
      "last_round_winner": {Player},
      "num_players": 3,
      "win_points": 7,
      "has_started": true,
      "game_state": "pick_wc",
      "players": [{Player}, {Player}, {Player}],
      "card_czar": {Player},
      "decks": [{Deck},{Deck},{Deck},{Deck}],
      "current_black_card": {Card}
    }
    
###Fields
-  `game_id `- *integer*, id of the game
-  `join_id` - *uuid*, identifies the game. Passed in the url.
-  `last_round_winner` - *None* or *Player* object, the player who won the last round
-  `num_players` - *integer*, the number of players playing this game
-  `win_points` - *integer*, the number of points required to win the game
-  `has_started` - *boolean*, true if the game has started
-  `game_state` - *string*, the current state of the game. See the [Game State](GameState.md) documentation for more details
-  `players` - list of *Player* objects, players playing this game
-  `card_czar` - The player who is the current card czar
-  `decks` - list of *Deck* objects, decks being used for this game
-  `current_black_card` - *Card* object, The black card for the round
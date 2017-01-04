from channels import Group
from channels.sessions import channel_session
from .models import Game

@channel_session
def ws_connect(message):
    try:
      join_id = message['path'].split('/')
      game = Game.objects.get(join_id=join_id)
    except:
        message['reply']
    Group('game-' + join_id).add(message.reply_channel)
    message.channel_session['game'] = game_id

@channel_session
def ws_receive(message):
    join_id = message.channel_session['game']


@channel_session
def ws_disconnect(message):
    label = message.channel_session['room']
    Group('game-'+label).discard(message.reply_channel)

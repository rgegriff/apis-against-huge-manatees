# APIS AGAINST HUGE MANATEES
## A [Cards Against Humanity](https://www.cardsagainsthumanity.com/)-clone server.
![A huge manatee with a circle and slash around it.](doc/manatee.jpg)

# What the hell is this?
I went through all the fun of building out a working, HTTP accessable multiplayer server for playing games like Apples to Apples and Cards Against Humanity, so that you could enjoy the pain of building a client for it.

# That sounds gr... Wait, what the fuck?
That's what *I'm* asking myself. Another way I have tried to explain it is that I want to offer a client-agnostic api for playing remote games in the style of Apples to Apples and Cards Against Humanity. This means that anyone with a few spare cycles can build a client for the server in their framework/engine/microcontroller of choice. I see this as a great way to learn new tools, and have something worth showing off to friends when you are done.

# Eww, so this is supposed to be educational?
Yep. 'Fraid so.

# Well, how can I get started?
Well, if you are reading this, we (meaning, at the moment, I) are (am) a ways away from officially launching. Eventually, I will be creating and maintaining a list of known working clients. Once we (I, again) actually get around to launching, pull-requests will be accepted for the server as well.

# So reading this is just a waste of my time right now?
Wow, you are getting good at this.

# Will there at least be an example client?
Yes, actually! Along with the version 1 api release, I will be including a menu-driven command-line based client.

# Is there a running server that I can build against?
Not currently. This repo will eventually contain instructions for running a server instance on Heroku, and with the version 1 launch, I want to also provide a running instance.

# Well, shit. Is there any way for me to just play with what exists now?
If you REALLY want to try playing with things as they exist now, good luck! What documentation there is (not much) lives in the doc/ folder. The code as it exists now is in a working state. You can send API requests to it and play a game, however the API is still kind of a mess and the websocket event notification system hasn't been implemented yet. The test passes tho.

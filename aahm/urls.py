"""aahm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from cah.views import CreateGameView, DeckListView, JoinGameView,\
    GameStateView, HandView, PlayCardsView, PlayListView, PickWinnerView

urlpatterns = [
    url(r'^create/', CreateGameView.as_view(), name="create-game"),
    url(r'^decks/', DeckListView.as_view(), name='list-decks'),
    url(r'^(?P<join_id>[^/]+)/join/', JoinGameView.as_view(), name='join-game'),
    url(r'^(?P<join_id>[^/]+)/gameState/', GameStateView.as_view(), name='game-state'),
    url(r'^(?P<join_id>[^/]+)/hand/', HandView.as_view(), name='hand'),
    url(r'^(?P<join_id>[^/]+)/playCards/', PlayCardsView.as_view(), name='play-cards'),
    url(r'^(?P<join_id>[^/]+)/listPlays', PlayListView.as_view(), name="list-plays"),
    url(r'^(?P<join_id>[^/]+)/pickWinner/', PickWinnerView.as_view(), name='pick-winner'),
    url(r'^admin/', include(admin.site.urls)),
]

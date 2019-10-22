import json
from shlex import quote

from django.http import HttpRequest
from django.shortcuts import render
from django.utils.safestring import mark_safe


def index(request: HttpRequest):
    return render(request, 'chat/index.html', {})


def room(request: HttpRequest, room_name: str):
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(quote(room_name)))
    })

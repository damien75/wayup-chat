import json
from shlex import quote

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.safestring import mark_safe


@login_required
def index(request: HttpRequest):
    return render(request, 'chat/index.html', {})


@login_required
def room(request: HttpRequest, room_name: str):
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(quote(room_name)))
    })

import json

from routes import route, Method, redirect_to
from render import render_template
from auth import *
from helper import find_first, save_photo
from error import *
from db import create_user, find_user


# @route('auth/json/chat/users')
# def myauth(request, **kwargs):
#     kwargs.setdefault('message', '')
#     request.response.code = 400
#     return my_error(request)
import requests
from .MyPickle import *
from io import *

SERVER = 'http://localhost:8888'
FAIL_ERROR = 'Authorised Failed!'
#TODO(): Only For Test
TOKEN = '40bd001563085fc35165329ea1ff5c5ecbdbbeef'


def select(what, where, predicate="",token = TOKEN):
    # initialize the parameters
    payload = {}
    payload['content'] = what
    payload['table'] = where
    payload['token'] = token
    if predicate is not "":
        payload['predicate'] = predicate

    # send http requests
    r = requests.get('{}/select'.format(SERVER), params=payload)
    # retore the tuple object
    return read_from_stream(BytesIO(r.content))


def insert(where, values, which="",token = TOKEN):
    payload = {}
    payload['table'] = where
    payload['token'] = token
    if which is not "":
        payload['column'] = which
    r = requests.post('{}/insert'.format(SERVER), params = payload,data = values)
    return r.text


def update(where, attributes, values, predicate="",token = TOKEN):
    """Update table Set the attributes in the values where predicate is True.

    Cautions:
        No space was allowed beside comma!

    Args:
        attributes: a string of the attributes seperated by ','.
        values: a string of values you wanna assign them into the attributes, also seperated by comma. 

    """
    payload = {}
    payload['table'] = where
    payload['keys'] = attributes
    payload['values'] = values
    payload['token'] = token
    if predicate is not "":
        payload['predicate'] = predicate
    r = requests.post('{}/update'.format(SERVER),params = payload)
    return r.text
    

def delete(where, predicate="",token = TOKEN):
    payload = {}
    payload['table'] = where
    payload['token'] = token
    r = requests.post('{}/delete'.format(SERVER), params = payload,data = predicate)
    return r.text


def log_in(account,password):
    payload = {}
    payload['account'] = account
    r = requests.post('{}/login'.format(SERVER), params = payload,data = password)
    return r.text


def sign_up(account,password):
    payload = {}
    payload['account'] = account
    r = requests.post('{}/signup'.format(SERVER), params = payload,data = password)
    return r.text







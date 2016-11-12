"""
System tests for grouper, to be run with a test runner like `pytest`.

These tests assume a running server.
"""

from uuid import uuid4
import requests
from grouper import API_URL


URL_BASE = 'http://localhost:5000'
URL = URL_BASE + API_URL


def random_name(prefix='user'):
    return prefix + uuid4().hex

def random_email():
    return uuid4().hex + '@' + uuid4().hex + '.com'


def test_get_users():
    r = requests.get('/'.join((URL, 'users')))
    assert r.status_code == 200
    assert 'users' in set(r.json().keys())


def test_add_update_delete_user():
    name = random_name()
    email = random_email()
    data = dict(name=name,
                email=email,
                groups=[])
    updated_data = dict(name=name,
                        email='foo@bar.com',
                        groups=[])

    r = requests.post('/'.join((URL, 'users')), json=data)
    uid = r.json()['user']['id']
    uid = str(uid)
    assert r.status_code == 201

    r = requests.get('/'.join((URL, 'users', uid)))
    assert r.status_code == 200
    result = r.json()
    del result['user']['id']
    assert result['user'] == data

    r = requests.put('/'.join((URL, 'users', uid)),
                     json=dict(email='foo@bar.com'))
    assert r.status_code == 200

    r = requests.get('/'.join((URL, 'users', uid)))
    assert r.status_code == 200
    result = r.json()
    del result['user']['id']
    assert result['user'] == updated_data

    r = requests.delete('/'.join((URL, 'users', uid)))
    assert r.status_code == 200

    r = requests.get('/'.join((URL, 'users', uid)))
    assert r.status_code == 404


def test_get_groups():
    r = requests.get('/'.join((URL, 'groups')))
    assert r.status_code == 200
    assert 'groups' in set(r.json().keys())


def test_add_update_delete_group():
    name = random_name()
    data = dict(name=name,
                users=[])
    updated_data = dict(name='foo',
                        users=[])

    r = requests.post('/'.join((URL, 'groups')), json=data)
    uid = r.json()['group']['id']
    uid = str(uid)
    assert r.status_code == 201

    r = requests.get('/'.join((URL, 'groups', uid)))
    assert r.status_code == 200
    result = r.json()
    del result['group']['id']
    assert result['group'] == data

    r = requests.put('/'.join((URL, 'groups', uid)),
                     json=dict(name='foo'))
    assert r.status_code == 200

    r = requests.get('/'.join((URL, 'groups', uid)))
    assert r.status_code == 200
    result = r.json()
    del result['group']['id']
    assert result['group'] == updated_data

    r = requests.delete('/'.join((URL, 'groups', uid)))
    assert r.status_code == 200

    r = requests.get('/'.join((URL, 'groups', uid)))
    assert r.status_code == 404

from uuid import uuid4
import requests


URL_BASE = 'http://localhost:5000'
API_URL = 'grouper/api/v1'
URL = '/'.join((URL_BASE, API_URL))


users = {
    'alice':
        {'username': 'alice',
         'email': 'alice@q.bio',
         'groups': ['wheel', 'developers'],
         },
    'bob':
        {'username': 'bob',
         'email': 'bob@q.bio',
         'groups': ['developers'],
         },
    'charlie':
        {'username': 'charlie',
         'email': 'charlie@q.bio',
         'groups': ['marketing'],
         },
    }

groups = {
    'wheel':
        {'groupname': 'wheel',
         'users': ['alice'],
         },
    'developers':
        {'groupname': 'developers',
         'users': ['alice', 'bob'],
         },
    'marketing':
        {'groupname': 'marketing',
         'users': ['charlie'],
         },
    'www':
        {'groupname': 'www',
         'users': [],
         },
    }


def random_name(prefix='user'):
    return prefix + uuid4().hex

def random_email():
    return uuid4().hex + '@' + uuid4().hex + '.com'


def test_get_users():
    r = requests.get('/'.join((URL, 'users')))
    assert r.status_code == 200
    assert list(r.json().keys())[0] == 'users'


def test_add_update_delete_user():
    username = random_name()
    email = random_email()
    data = dict(username=username,
                email=email,
                groups=[])
    updated_data = dict(username=username,
                        email='foo@bar.com',
                        groups=[])

    r = requests.post('/'.join((URL, 'users')), json=data)
    assert r.status_code == 201

    r = requests.get('/'.join((URL, 'users', username)))
    assert r.status_code == 200
    assert r.json() == {'user': data}

    r = requests.put('/'.join((URL, 'users', username)),
                     json=dict(email='foo@bar.com'))
    assert r.status_code == 200

    r = requests.get('/'.join((URL, 'users', username)))
    assert r.status_code == 200
    assert r.json() == {'user': updated_data}

    r = requests.delete('/'.join((URL, 'users', username)))
    assert r.status_code == 200

    r = requests.get('/'.join((URL, 'users', username)))
    assert r.status_code == 404


def test_get_groups():
    r = requests.get('/'.join((URL, 'groups')))
    assert r.status_code == 200
    assert list(r.json().keys())[0] == 'groups'


def test_add_update_delete_group():
    groupname = random_name('group')
    data = dict(groupname=groupname,
                users=[])
    updated_data = dict(groupname=groupname,
                        users=['foo', 'bar'])


    r = requests.post('/'.join((URL, 'groups')), json=data)
    assert r.status_code == 201

    r = requests.get('/'.join((URL, 'groups', groupname)))
    assert r.status_code == 200
    assert r.json() == {'group': data}

    r = requests.put('/'.join((URL, 'groups', groupname)),
                     json=dict(users=['foo', 'bar']))
    assert r.status_code == 200

    r = requests.get('/'.join((URL, 'groups', groupname)))
    assert r.status_code == 200
    assert r.json() == {'group': updated_data}

    r = requests.delete('/'.join((URL, 'groups', groupname)))
    assert r.status_code == 200

    r = requests.get('/'.join((URL, 'groups', groupname)))
    assert r.status_code == 404


def test_error():
    r = requests.get('/'.join((URL, 'asdfasdf')))
    assert r.status_code == 404
    assert r.json() == dict(error="Not found")

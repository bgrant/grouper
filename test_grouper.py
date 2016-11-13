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


def test_add_and_delete_users_with_groups():

    # Create groups

    group0 = dict(name=random_name())
    group1 = dict(name=random_name())

    r = requests.post('/'.join((URL, 'groups')), json=group0)
    group0_id = r.json()['group']['id']
    assert r.status_code == 201

    r = requests.post('/'.join((URL, 'groups')), json=group1)
    group1_id = r.json()['group']['id']
    assert r.status_code == 201

    # Create users

    user0 = dict(name=random_name(),
                 email=random_email(),
                 groups=[group0_id])

    user1 = dict(name=random_name(),
                 email=random_email(),
                 groups=[group0_id, group1_id])

    r = requests.post('/'.join((URL, 'users')), json=user0)
    user0_id = r.json()['user']['id']
    assert r.status_code == 201

    r = requests.post('/'.join((URL, 'users')), json=user1)
    user1_id = r.json()['user']['id']
    assert r.status_code == 201

    # Check creations

    r = requests.get('/'.join((URL, 'users', str(user0_id))), json=user0)
    assert r.status_code == 200
    assert r.json()['user']['name'] == user0['name']
    assert r.json()['user']['email'] == user0['email']
    assert set(r.json()['user']['groups']) == set(user0['groups'])

    r = requests.get('/'.join((URL, 'users', str(user1_id))), json=user1)
    assert r.status_code == 200
    assert r.json()['user']['name'] == user1['name']
    assert r.json()['user']['email'] == user1['email']
    assert set(r.json()['user']['groups']) == set(user1['groups'])

    # Delete everything, checking intermediate results

    r = requests.delete('/'.join((URL, 'groups', str(group0_id))))
    assert r.status_code == 200

    r = requests.get('/'.join((URL, 'users', str(user0_id))), json=user0)
    assert r.status_code == 200
    assert r.json()['user']['groups'] == []

    r = requests.get('/'.join((URL, 'users', str(user1_id))), json=user1)
    assert r.status_code == 200
    assert r.json()['user']['groups'] == [group1_id]

    r = requests.delete('/'.join((URL, 'users', str(user0_id))))
    assert r.status_code == 200

    r = requests.get('/'.join((URL, 'groups', str(group0_id))))
    assert r.status_code == 404

    r = requests.get('/'.join((URL, 'groups', str(group1_id))))
    assert r.status_code == 200
    assert r.json()['group']['users'] == [user1_id]

    r = requests.delete('/'.join((URL, 'users', str(user1_id))))
    assert r.status_code == 200

    r = requests.delete('/'.join((URL, 'groups', str(group1_id))))
    assert r.status_code == 200


def test_modify_user_groups():

    # setup
    group0 = dict(name=random_name())
    group1 = dict(name=random_name())

    user0 = dict(name=random_name(),
                 email=random_email(),
                 groups=[])

    r = requests.post('/'.join((URL, 'users')), json=user0)
    user0_id = r.json()['user']['id']
    assert r.status_code == 201
    assert r.json()['user']['name'] == user0['name']
    assert r.json()['user']['email'] == user0['email']
    assert r.json()['user']['groups'] == user0['groups']

    r = requests.post('/'.join((URL, 'groups')), json=group0)
    assert r.status_code == 201
    group0_id = r.json()['group']['id']

    r = requests.post('/'.join((URL, 'groups')), json=group1)
    assert r.status_code == 201
    group1_id = r.json()['group']['id']

    # change name
    new_random_name = random_name()
    r = requests.put('/'.join((URL, 'users', str(user0_id))),
                     json=dict(name=new_random_name))
    assert r.status_code == 200
    assert r.json()['user']['name'] == new_random_name

    # change email
    new_random_email = random_email()
    r = requests.put('/'.join((URL, 'users', str(user0_id))),
                     json=dict(email=new_random_email))
    assert r.status_code == 200
    assert r.json()['user']['email'] == new_random_email

    # change groups
    r = requests.put('/'.join((URL, 'users', str(user0_id))),
                     json=dict(groups=[group0_id]))
    assert r.status_code == 200
    assert set(r.json()['user']['groups']) == {group0_id}

    # change groups
    r = requests.put('/'.join((URL, 'users', str(user0_id))),
                     json=dict(groups=[group0_id, group1_id]))
    assert r.status_code == 200
    assert set(r.json()['user']['groups']) == {group0_id, group1_id}

    # delete
    r = requests.delete('/'.join((URL, 'users', str(user0_id))))
    assert r.status_code == 200


# Test error conditions


def test_double_add_user():
    user0 = dict(name=random_name(),
                 email=random_email(),
                 groups=[])

    r = requests.post('/'.join((URL, 'users')), json=user0)
    user0_id = r.json()['user']['id']
    assert r.status_code == 201

    r = requests.post('/'.join((URL, 'users')), json=user0)
    assert r.status_code == 409

    r = requests.delete('/'.join((URL, 'users', str(user0_id))))
    assert r.status_code == 200


def test_double_add_group():
    group0 = dict(name=random_name(),
                  users=[])

    r = requests.post('/'.join((URL, 'groups')), json=group0)
    group0_id = r.json()['group']['id']
    assert r.status_code == 201

    r = requests.post('/'.join((URL, 'groups')), json=group0)
    assert r.status_code == 409

    r = requests.delete('/'.join((URL, 'groups', str(group0_id))))
    assert r.status_code == 200

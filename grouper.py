"""
Grouper is a Python web service for managing users and groups.

It exposes a JSON/REST API and stores the user and group info in a database.
See README.md for more details.
"""

import os
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from marshmallow import Schema, fields, ValidationError


# Config

API_URL = '/grouper/api/v1'

BASEDIR = os.path.abspath(os.path.dirname(__file__))
FALLBACK_DB = 'sqlite:///' + os.path.join(BASEDIR, 'data.sqlite')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL') or
                                         FALLBACK_DB)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
manager = Manager(app)


# Models

user_groups = db.Table('user_groups',
        db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
        db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
        )


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    groups = db.relationship('Group',
                             secondary=user_groups,
                             backref=db.backref('users', lazy='dynamic'),
                             lazy='dynamic')

    def __repr__(self):
        rep = ("User(id={id!r}, name={name!r}, "
               "email={email!r}, groups={groups!r})")
        return rep.format(id=self.id, name=self.name, email=self.email,
                          groups=[g.id for g in self.groups])


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __repr__(self):
        rep = "Group(id={id!r}, name={name!r}, users={users!r})"
        return rep.format(id=self.id, name=self.name,
                          users=[u.id for u in self.users])


# Schemas

def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=must_not_be_blank)
    email = fields.Str(required=True, validate=must_not_be_blank)
    groups = fields.Nested('GroupSchema', many=True, only='id')


class GroupSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=must_not_be_blank)
    users = fields.Nested('UserSchema', many=True, only='id')


user_schema = UserSchema()
users_schema = UserSchema(many=True)
group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)


# API


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'message': 'Not found'}), 404)


## User Resources


@app.route(API_URL + '/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = users_schema.dump(users)
    return jsonify({'users': result.data}), 200

@app.route(API_URL + '/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "User could not be found."}), 404
    else:
        user_result = user_schema.dump(user)
        return jsonify({'user': user_result.data}), 200

@app.route(API_URL + '/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "User could not be found."}), 404
    else:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted.'}), 200

@app.route(API_URL + '/users', methods=['POST'])
def add_user():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': "No input data provided."}), 400

    # Validate and deserialize input
    data, errors = user_schema.load(json_data)
    if errors:
        return jsonify(errors), 422

    name = data['name']
    if User.query.filter_by(name=name).count() != 0:
        return jsonify({'message': "User exists."}), 409

    email = data['email']
    groups = data['groups']

    # Create a new User
    user = User(name=name, email=email, groups=groups)
    db.session.add(user)
    db.session.commit()

    # Return
    result = user_schema.dump(User.query.get(user.id))
    return jsonify({'message': 'User added.',
                    'user': result.data}), 201

@app.route(API_URL + '/users/<int:user_id>', methods=['PUT'])
def modify_user(user_id):
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': "No input data provided."}), 400

    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "User could not be found."}), 400

    # Validate and deserialize input
    name = json_data.get('name', user.name)
    email = json_data.get('email', user.email)
    groups = json_data.get('groups', user.groups).all()

    data, errors = user_schema.load(
            dict(name=name, email=email, groups=groups))
    if errors:
        return jsonify(errors), 422

    # Modify the user
    user.name = data['name']
    user.email = data['email']
    user.groups = data['groups']

    db.session.add(user)
    db.session.commit()

    # Return
    result = user_schema.dump(User.query.get(user.id))
    return jsonify({'message': 'User added.',
                    'user': result.data}), 200


## Group Resources


@app.route(API_URL + '/groups', methods=['GET'])
def get_groups():
    groups = Group.query.all()
    result = groups_schema.dump(groups)
    return jsonify({'groups': result.data}), 200

@app.route(API_URL + '/groups/<int:group_id>', methods=['GET'])
def get_group(group_id):
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"message": "Group could not be found."}), 404
    else:
        group_result = group_schema.dump(group)
        return jsonify({'group': group_result.data}), 200

@app.route(API_URL + '/groups/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"message": "Group could not be found."}), 404
    else:
        db.session.delete(group)
        db.session.commit()
        return jsonify({'message': 'Group deleted.'}), 200

@app.route(API_URL + '/groups', methods=['POST'])
def add_group():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': "No input data provided."}), 400

    # Validate and deserialize input
    data, errors = group_schema.load(json_data)
    if errors:
        return jsonify(errors), 422

    name = data['name']
    if Group.query.filter_by(name=name).count() != 0:
        return jsonify({'message': "Group exists."}), 409

    users = data['users']

    # Create a new Group
    group = Group(name=name, users=users)
    db.session.add(group)
    db.session.commit()

    # Return
    result = group_schema.dump(Group.query.get(group.id))
    return jsonify({'message': 'Group added.',
                    'group': result.data}), 201

@app.route(API_URL + '/groups/<int:group_id>', methods=['PUT'])
def modify_group(group_id):
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': "No input data provided."}), 400

    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"message": "Group could not be found."}), 400

    # Validate and deserialize input
    name = json_data.get('name', group.name)
    users = json_data.get('users', group.users).all()

    data, errors = group_schema.load(
            dict(name=name, users=users))
    if errors:
        return jsonify(errors), 422

    # Modify the group
    group.name = data['name']
    group.users = data['users']

    db.session.add(group)
    db.session.commit()

    # Return
    result = group_schema.dump(Group.query.get(group.id))
    return jsonify({'message': 'Group added.',
                    'group': result.data}), 200


if __name__ == '__main__':
    db.create_all()
    manager.run()

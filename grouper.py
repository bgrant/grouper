"""
Grouper is a Flask-based web service for managing users and groups.

It exposes a JSON/REST API and stores the user and group info in a database.
See README.md for more details.
"""

import os
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from marshmallow import Schema, fields, validate, ValidationError


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

SQL_MAXINT = int(2**63 - 1)


# Database Models


user_groups = db.Table('user_groups',
        db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
        db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
        )


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
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
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        rep = "Group(id={id!r}, name={name!r}, users={users!r})"
        return rep.format(id=self.id, name=self.name,
                          users=[u.id for u in self.users])


# Marshmallow schemas for (de)serialization and validation


def must_not_be_blank(data):
    """Raise validation error if data is Falsey."""
    if not data:
        raise ValidationError('Data not provided.')


def validate_id(id_):
    """Raise validation error if data id_ is outside SQL id range."""
    if id_ < 1 or id_ > SQL_MAXINT:
        raise ValidationError('ID does not exist.')


class UserGroups(fields.Field):
    """(De)serialization for a user's groups."""

    def _serialize(self, value, attr, obj):
        return [v.id for v in value]

    def _deserialize(self, value, attr, obj):
        if len(value) > 0:
            result = Group.query.filter(Group.id.in_(value)).all()
            if len(result) != len(value):
                raise ValidationError('Not all supplied groups exist')
            return result
        else:
            return []


class UserSchema(Schema):
    """Schema to validate and (de)serialize Users."""
    id = fields.Int(dump_only=True, validate=validate_id)
    name = fields.Str(required=True, validate=must_not_be_blank)
    email = fields.Email(required=True)
    groups = UserGroups()


class GroupUsers(fields.Field):
    """(De)serialization for a group's users."""
    def _serialize(self, value, attr, obj):
        return [v.id for v in value]

    def _deserialize(self, value, attr, obj):
        if len(value) > 0:
            result = User.query.filter(User.id.in_(value)).all()
            if len(result) != len(value):
                raise ValidationError('Not all supplied users exist')
            return result
        else:
            return []


class GroupSchema(Schema):
    """Schema to validate and (de)serialize Groups."""
    id = fields.Int(dump_only=True,
                    validate=validate.Range(min=1, max=SQL_MAXINT))
    name = fields.Str(required=True, validate=must_not_be_blank)
    users = GroupUsers()


user_schema = UserSchema()
users_schema = UserSchema(many=True)
group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)


# API (Flask views)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'message': 'Not found'}), 404)


## User Resource


@app.route(API_URL + '/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = users_schema.dump(users)
    return jsonify({'users': result.data}), 200

@app.route(API_URL + '/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        validate_id(user_id)
    except ValidationError:
        return jsonify({"message": "User could not be found."}), 404

    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "User could not be found."}), 404
    else:
        user_result = user_schema.dump(user)
        return jsonify({'user': user_result.data}), 200

@app.route(API_URL + '/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        validate_id(user_id)
    except ValidationError:
        return jsonify({"message": "User could not be found."}), 404

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
    groups = data.get('groups', [])

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

    try:
        validate_id(user_id)
    except ValidationError:
        return jsonify({"message": "User could not be found."}), 404

    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "User could not be found."}), 400

    # Validate and deserialize input
    name = json_data.get('name', user.name)
    email = json_data.get('email', user.email)
    groups = json_data.get('groups', user.groups.all())

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


## Group Resource


@app.route(API_URL + '/groups', methods=['GET'])
def get_groups():
    groups = Group.query.all()
    result = groups_schema.dump(groups)
    return jsonify({'groups': result.data}), 200

@app.route(API_URL + '/groups/<int:group_id>', methods=['GET'])
def get_group(group_id):
    try:
        validate_id(group_id)
    except ValidationError:
        return jsonify({"message": "Group could not be found."}), 404

    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"message": "Group could not be found."}), 404
    else:
        group_result = group_schema.dump(group)
        return jsonify({'group': group_result.data}), 200

@app.route(API_URL + '/groups/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    try:
        validate_id(group_id)
    except ValidationError:
        return jsonify({"message": "Group could not be found."}), 404

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

    users = data.get('users', [])

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

    try:
        validate_id(group_id)
    except ValidationError:
        return jsonify({"message": "Group could not be found."}), 404

    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"message": "Group could not be found."}), 400

    # Validate and deserialize input
    name = json_data.get('name', group.name)
    users = json_data.get('users', group.users.all())

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

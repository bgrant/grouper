from flask import Flask, jsonify


app = Flask(__name__)

BASE_URI = '/grouper/api/v1.0'


users = [
        {'username': 'alice',
         'email': 'alice@q.bio',
         'groups': ['wheel', 'developers'],
         },
        {'username': 'bob',
         'email': 'bob@q.bio',
         'groups': ['developers'],
         },
        {'username': 'charlie',
         'email': 'charlie@q.bio',
         'groups': ['marketing'],
         },
    ]

groups = [
        {'groupname': 'wheel',
         'users': ['alice'],
         },
        {'groupname': 'developers',
         'users': ['alice', 'bob'],
         },
        {'groupname': 'marketing',
         'users': ['charlie'],
         },
        {'groupname': 'www',
         'users': [],
         },
    ]


@app.route('/'.join((BASE_URI, 'users')),
           methods=['GET'])
def get_users():
    return jsonify({'users': users})


@app.route('/'.join((BASE_URI, 'groups')),
           methods=['GET'])
def get_groups():
    return jsonify({'groups': groups})


if __name__ == '__main__':
    app.run(debug=True)

import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# ----------------------------------------------------------------------------
# ROUTES
# ----------------------------------------------------------------------------
'''
GET /db_create: Initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE called on first run to set up database
'''


@app.route('/db_create', methods=['GET'])
def db_create():
    db_drop_and_create_all()
    return jsonify({
        'success': True,
        'message': 'Database successfuly created'
    }), 200


'''
GET /drinks
returns status code 200 and json {"success": True, "drinks": drinks}
where drinks is the list of drinks or appropriate status code
indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.order_by(Drink.title).all()

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        'succes': True,
        'drinks': [d.short() for d in drinks]
    })


'''
GET /drinks-detail
require the 'get:drinks-detail' permission

returns status code 200 and json {"success": True, "drinks": drinks}
where drinks is the list of drinks or appropriate status code indicating
reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.order_by(Drink.title).all()

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': [d.long() for d in drinks]
    }), 200


'''
POST /drinks
requires the 'post:drinks' permission

json input data structure
    [{
        "color": string,
        "name": string,
        "parts": number
    }]

returns status code 200 and json {"success": True, "drinks": drink}
where drink an array containing only the newly created drink or
appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    title = request.json.get('title', None)
    data = json.dumps(request.json.get('recipe', None))

    if (title is None) or (data is None):
        abort(404)

    try:
        d = Drink(title=title, recipe=data)
        d.insert()
    except:
        abort(422)

    return jsonify({
        'success': True,
        'drinks': d.long()
    }), 200


'''
PATCH /drinks/<id>
requires 'patch:drinks' permission

where <id> is the existing model id and update the corresponding row
for <id>

respond with a 404 error if <id> is not found

json input data structure
    [{
        "color": string,
        "name": string,
        "parts": number
    }]

returns status code 200 and json {"success": True, "drinks": drink}
where drink an array containing only the updated drink or appropriate
status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink_by_id(payload, drink_id):
    title = request.json.get('title', None)
    data = request.json.get('recipe', None)

    if (title is None) or (data is None):
        abort(404)

    try:
        d = Drink.query.get_or_404(drink_id)
        d.title = title
        d.recipe = json.dumps(data)
        d.update()

    except:
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [d.title, d.recipe]
    }), 200


'''
DELETE /drinks/<id>
it should require the 'delete:drinks' permission

where <id> is the existing model id and will delete the
corresponding row for <id>

respond with a 404 error if <id> is not found

returns status code 200 and json {"success": True, "delete": id}
where id is the id of the deleted recordor appropriate status code
indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def udelete_dirnk(payload, drink_id):

    try:
        d = Drink.query.get_or_404(drink_id)
        d.delete()

    except:
        abort(500)

    return jsonify({
        'success': True,
        'delete': d.id
    }), 200

# ----------------------------------------------------------------------------
# Error Handling
# ----------------------------------------------------------------------------


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(405)
def umethod_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


@app.errorhandler(AuthError)
def authentication_failed(e):
    return jsonify({
        "success": False,
        "error": e.status_code,
        "message": e.error['code']
    }), e.status_code

from flask import Flask, jsonify, request, make_response
from flask_jsonschema_validator import jsonschemavalidator
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
import mvc.controllers.user_controller
import logging
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = b'cts-cde'  # TO DO - read from config file


# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            # return 401 if token is not passed
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'])
            userinfo = mvc.controllers.user_controller.User.get_user_details('username', data['name'])
            user = userinfo.get('data')[0]
            if user['user_id'] != kwargs['user_id']:
                return jsonify({
                    'message': 'Token is invalid for this user!!'
                 }), 401

        except:
            return jsonify({
                'message': 'Token is invalid !!'
            }), 401
        # returns the current logged in users context to the routes
        return f(user, *args, **kwargs)

    return decorated


@app.route('/user/<int:user_id>', methods=['GET'])
@token_required
def get_user_detail(user,user_id):
    logging.info('get user details method')
    return mvc.controllers.user_controller.User.get_user_details('user_id', user_id)


@app.route('/register', methods=["POST"])
def register_user():
    data = request.json
    logging.info('register user details method with payload' + str(data))
    return mvc.controllers.user_controller.User.add_user(data)


@app.route('/update/<int:user_id>', methods=['PUT'])
@token_required
def update_user_detail(user, user_id):
    data = request.json
    updated_response = mvc.controllers.user_controller.User.update_user(user_id, data)
    return updated_response


@app.route('/user/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user, user_id):
    delete_response = mvc.controllers.user_controller.User.delete_user(user_id)
    if int(delete_response) == 0:
        return make_response('Could not delete: User not found', 203)
    elif int(delete_response):
        return make_response('User is Deleted', 200)


@app.route('/login', methods=['POST'])
def login():
    authentication = request.json
    if not authentication or not authentication.get('username') or not authentication.get('password'):
        return make_response(
            'Could not verify user',
            401,
            {'Custom-Error': 'Login required!'}
        )
    user = mvc.controllers.user_controller.User.get_user_details('username', authentication.get('username'))
    if not user.get('data') == []:
        userInfo = user.get('data')[0]
    else:
        userInfo = None

    if not userInfo:
        return make_response(
            'Could not verify the credentials',
            403,
            {'Custom-Error': 'Invalid credentials!'}
        )

    if check_password_hash(userInfo.get('password'), authentication.get('password')):
        token = jwt.encode({
            'name': userInfo.get('username'),
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY']).decode('ascii')

        return make_response(jsonify({'token': token}), 201)
    else:
        return make_response(
            'Could not verify the credentials',
            403,
            {'WWW-Authenticate': 'Invalid credentials!'}
        )


@app.route('/loan/<int:user_id>', methods=['POST'])
@token_required
def add_loan_details(user,user_id):
    data = request.json
    return mvc.controllers.user_controller.Loan.add_loan(data)


@app.route('/loan/<int:loan_id>/<int:user_id>', methods=['GET'])
@token_required
def get_loan_details(user,loan_id, user_id):
    return mvc.controllers.user_controller.Loan.get_loan_details(loan_id)


@app.route('/loan/<int:loan_id>/<int:user_id>', methods=['DELETE'])
@token_required
def delete_loan(user,loan_id, user_id):
    delete_response = mvc.controllers.user_controller.Loan.delete_loan(loan_id)
    if int(delete_response) == 0:
        return make_response('Could not delete: Loan details not found', 404)
    elif int(delete_response):
        return make_response('Deleted the loan details', 200)


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, jsonify, request, make_response
from flask_jsonschema_validator import jsonschemavalidator
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
import mvc.controllers.user_controller
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = b'cts-cde'  # TO DO - read from config file


@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_detail(user_id):
    logging.info('get user details method')
    return mvc.controllers.user_controller.User.get_user_details('user_id', user_id)


@app.route('/register', methods=["POST"])
def register_user():
    data = request.json
    logging.info('register user details method with payload' + data)
    return mvc.controllers.user_controller.User.add_user(data)


@app.route('/update/<int:user_id>', methods=['PUT'])
def update_user_detail(user_id):
    data = request.json
    update_reponse = mvc.controllers.user_controller.User.update_user(user_id, data)
    return update_reponse


@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    delete_response = mvc.controllers.user_controller.User.delete_user(user_id)
    if int(delete_response) == 0:
        return make_response('Could not delete: User not found', 203)
    elif int(delete_response):
        return make_response('Deleted', 200)


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


@app.route('/loan', methods=['POST'])
def add_loan_details():
    data = request.json
    return mvc.controllers.user_controller.Loan.add_loan(data)


@app.route('/loan/<loanid>', methods=['GET'])
def get_loan_details(loanid):
    return mvc.controllers.user_controller.Loan.get_loan_details(loanid)


@app.route('/loan/<loanid>', methods=['DELETE'])
def delete_loan(loanid):
    delete_response = mvc.controllers.user_controller.Loan.delete_loan(loanid)
    if int(delete_response) == 0:
        return make_response('Could not delete: User not found', 404)
    elif int(delete_response):
        return make_response('Deleted', 200)


if __name__ == '__main__':
    app.run(debug=True)

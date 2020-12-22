from flask import make_response, jsonify
import mvc.model.mongoclient
from werkzeug.security import generate_password_hash
import logging


class User:

    @classmethod
    def get_user_details(cls, search_condition, customer_identifier):
        try:
            if customer_identifier is None:
                return make_response(jsonify({"message": "Invalid/Search criteria!"}), 400)
            else:
                data = mvc.model.mongoclient.MongoModel.get_record(search_condition, customer_identifier)
                if len(data) > 0:
                    return data
                return make_response(jsonify({"message": "No records found!"}), 200)
        except Exception as e:
            logging.error(e)
            raise e

    @classmethod
    def delete_user(cls, user_id):
        return mvc.model.mongoclient.MongoModel.delete_record('user_id', user_id)

    @classmethod
    def update_user(cls, user_id, data):
        return mvc.model.mongoclient.MongoModel.update_record(user_id, data)

    @classmethod
    def add_user(cls, request_data):
        _id = None
        try:
            request_data["user_id"] = mvc.model.mongoclient.MongoModel.get_document_number("user_id") + 1
            request_data["password"] = generate_password_hash(request_data["password"])
            _id = mvc.model.mongoclient.MongoModel.add_record(request_data)
            if _id:
                user_id = request_data["user_id"]
                response = make_response(jsonify({"user_id": user_id}), 200)
                response.headers["trace_id"] = _id
            else:
                response = make_response(jsonify({"Warning": "Customer creation failed.."}), 500)
        except Exception as ex:
            response = make_response(jsonify({"Error": "Error occurred on Customer creation."} + ex), 500)
        return response


class Loan:
    @classmethod
    def add_loan(cls, request_data):
        _id = None
        try:
            request_data["loan_id"] = mvc.model.mongoclient.MongoModel.get_document_number("loan_id", "Loan") + 1
            _id = mvc.model.mongoclient.MongoModel.add_record(request_data, "Loan")
            if _id:
                loan_id = request_data["loan_id"]
                response = make_response(jsonify({"loan_id": loan_id}), 200)
                response.headers["trace_id"] = _id
            else:
                response = make_response(jsonify({"Warning": "Loan creation failed."}), 500)
        except Exception as ex:
            response = make_response(jsonify({"Error": "Error occurred on Loan creation."} + ex), 500)
        return response

    @classmethod
    def get_loan_details(cls, loan_id):
        try:
            if loan_id is None:
                return make_response(jsonify({"message": "Invalid/Search criteria!"}), 400)
            else:
                data = mvc.model.mongoclient.MongoModel.get_record('loan_id', loan_id, 'Loan')
                if len(data) > 0:
                    return data
                return make_response(jsonify({"message": "No records found!"}), 200)
        except Exception as e:
            raise e

    @classmethod
    def delete_loan(cls, loan_id):
        return mvc.model.mongoclient.MongoModel.delete_record('loanId', loan_id, 'Loan')

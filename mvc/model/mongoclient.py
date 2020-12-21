import pymongo
from pymongo import MongoClient
import logging


class MongoModel:
    mc = MongoClient("mongodb://localhost:27017")
    db = mc["Bank"]
    collection_name = db["Users"]

    @classmethod
    def get_document_number(cls, doc_id, collection_name=None):
        try:
            if collection_name:
                cls.collection_name = cls.db[collection_name]
            doc_id = cls.collection_name.find().sort(doc_id, pymongo.DESCENDING).limit(1)[0][doc_id]
        except BaseException as ex:
            doc_id = 0
            logging.error(ex)
        return doc_id

    @classmethod
    def get_record(cls, identifier, identifier_value=None, collection_name=None):
        if collection_name:
            cls.collection_name = cls.db[collection_name]
        if identifier_value:
            data = cls.collection_name.find({identifier: identifier_value}, {"_id": 0})
        else:
            data = cls.collection_name.find({}, {"_id": 0})
        records = dict(data=[])
        for item in data:
            records["data"].append(item)
        return records

    @classmethod
    def delete_record(cls, identifier, identifier_value=None, collection_name=None):
        if collection_name:
            cls.collection_name = cls.db[collection_name]
        response = cls.collection_name.delete_one({identifier: identifier_value})
        return str(response.deleted_count)

    @classmethod
    def add_record(cls, request_data, collection_name=None):
        if collection_name:
            cls.collection_name = cls.db[collection_name]
        response = cls.collection_name.insert_one(request_data)
        return response.inserted_id

    @classmethod
    def update_record(cls, request_data, collection_name=None, statement=None):
        if collection_name:
            cls.collection = cls.db[collection_name]
            response = cls.collection.update_one(statement, {"$set": request_data})
        return response

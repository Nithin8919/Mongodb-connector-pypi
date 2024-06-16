from typing import Any, Optional
import os
import pandas as pd
from pymongo.mongo_client import MongoClient
import json
from ensure import ensure_annotations


class MongoOperation:
    __collection = None  # private/protected variable
    __database = None
    
    def __init__(self, client_url: str, database_name: str, collection_name: Optional[str] = None):
        self.client_url = client_url
        self.database_name = database_name
        self.collection_name = collection_name
       
    def create_mongo_client(self) -> MongoClient:
        return MongoClient(self.client_url)
    
    def create_database(self) -> Any:
        if MongoOperation.__database is None:
            client = self.create_mongo_client()
            MongoOperation.__database = client[self.database_name]
        return MongoOperation.__database
    
    def create_collection(self, collection_name: Optional[str] = None) -> Any:
        if collection_name is None:
            collection_name = self.collection_name
        
        if MongoOperation.__collection is None or MongoOperation.__collection != collection_name:
            database = self.create_database()
            MongoOperation.__collection = database[collection_name]
        
        return MongoOperation.__collection
    
    def insert_record(self, record: Any, collection_name: str) -> None:
        if isinstance(record, list):
            for data in record:
                if not isinstance(data, dict):
                    raise TypeError("Each record in the list must be a dictionary")
            collection = self.create_collection(collection_name)
            collection.insert_many(record)
        elif isinstance(record, dict):
            collection = self.create_collection(collection_name)
            collection.insert_one(record)
        else:
            raise TypeError("Record must be a dictionary or a list of dictionaries")
    
    def bulk_insert(self, datafile: str, collection_name: Optional[str] = None) -> None:
        if datafile.endswith('.csv'):
            dataframe = pd.read_csv(datafile, encoding='utf-8')
        elif datafile.endswith(".xlsx"):
            dataframe = pd.read_excel(datafile, encoding='utf-8')
        else:
            raise ValueError("Unsupported file type. Use .csv or .xlsx files.")
        
        data_json = json.loads(dataframe.to_json(orient='records'))
        collection = self.create_collection(collection_name)
        collection.insert_many(data_json)

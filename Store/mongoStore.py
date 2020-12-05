import pymongo
import time

class MongoStore(object):
    def __init__(self,database):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.context = self.client[database]

    def insert(self, coll, objs):
        for obj in objs:
            try:
                self.context[coll].insert_one(obj)
                time.sleep(2)
            except:
                continue
        # self.context[coll].insert_many(objs, ordered=False)
    
    def find(self, coll, query):
        return self.context[coll].find(query)

    def distinct(self, coll, key):
        for item in self.context[coll].distinct(key):
            repeating = self.context[coll].find_one({key: item})
            result = self.context[coll].delete_many({key: item})
            self.context[coll].insert_one(repeating)


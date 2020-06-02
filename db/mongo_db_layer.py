from db.base_db_layer import BaseDBLayer
import pymongo
from bson import ObjectId


class MongoDBLayer(BaseDBLayer):

    def __connect(self):
        self.__client = pymongo.MongoClient('localhost', 27017)
        self.__db = self.__client["horse_race"]

    def shutdown(self):
        self.__client.close()

    def __init__(self, cache):
        super(MongoDBLayer, self).__init__(cache)
        self.__connect()

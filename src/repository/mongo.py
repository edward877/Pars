from pymongo import MongoClient

class MongoRepository(object):
    def __init__(self, connectionString: str, database: str, collection):
        self.connection = MongoClient(connectionString)
        self.collection = self.connection[database][collection]

    def save_to_db(self, tender):
        doc = {"_id": tender['Номер'] + " " + str(tender['Лот']['Номер лота']),
               "number_redaction": tender['Номер редакции извещения']}
        self.collection.insert(doc)

    def exist_in_db(self, tender):
        test = self.collection.find_one({"_id": tender['Номер'] + " " + str(tender['Лот']['Номер лота'])},
                                {'number_redaction': tender['Номер редакции извещения']})
        return test
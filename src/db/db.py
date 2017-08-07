from pymongo import MongoClient

class DB(object):
    def __init__(self):
        self.base_url = 'https://223.rts-tender.ru/supplier/auction/Trade/'
        self.url_search = self.base_url + 'Search.aspx?jqGridID=BaseMainContent_MainContent_jqgTrade&rows=10&sidx=PublicationDate&sord=desc&page={}'
        self.url_view = self.base_url + 'View.aspx?Id={}'

    def connect(self):
        connection = MongoClient('localhost', 27017)
        db = connection.test
        collect = db.test
        return collect

    def save_to_db(self, collect, tender):
        doc = {"номер": tender['Номер'], "номер лота": tender['Лот']['Номер лота'],
               "номер редакции": tender['Номер редакции извещения']}
        collect.save(doc)

    def exist_in_db(self, collect, tender):
        test = collect.find_one({"номер": tender['Номер']},{'номер редакции':tender['Номер редакции извещения']})
        return test
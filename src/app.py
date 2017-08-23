import json, os
from pathlib import PurePath
path = str(PurePath(os.path.abspath(__file__)).parent)

from src.bll.http_worker import HttpWorker
from src.repository.mongo import MongoRepository
from src.repository.rabbitmq import RabbitMq

class Main(object):
    def __init__(self):
        self.config_path = os.path.join(path, "config.json")
        self.http_worker = HttpWorker()
        self.config = self.get_config(self.config_path)
        self.mongo_settings = self.config["mongodb"]
        self.rabbit_settings = self.config["rabbitmq"]
        self.mongo_connection = MongoRepository(self.mongo_settings["connectionString"],
                                                self.mongo_settings["database"],
                                                self.mongo_settings["collection"])
        self.rabbitmq = RabbitMq(self.rabbit_settings["host"], self.rabbit_settings["port"],
                                 self.rabbit_settings["user"], self.rabbit_settings["password"], "/", "utf-8")
        self.queue_name = self.rabbit_settings["queue"]
        self.base_url = 'https://223.rts-tender.ru/supplier/auction/Trade/'
        self.url_search = self.base_url + 'Search.aspx?jqGridID=BaseMainContent_MainContent_jqgTrade&rows=10&sidx=PublicationDate&sord=desc&page={}'
        self.url_view = self.base_url + 'View.aspx?Id={}'


    def run(self):
        response_json = self.http_worker.get_json(self.url_search.format(1))
        page_count = self.http_worker.get_page_info(response_json)
        page = 1
        while page <= page_count:
            try:
                if page != 1:
                    response_json = self.http_worker.get_json(self.url_search.format(page))
                list_tender_id = self.http_worker.parse_json_pages(response_json)
                for tender_id in list_tender_id:
                    html = self.http_worker.get_html(self.url_view.format(tender_id))
                    tenders = self.http_worker.parse_html(html, tender_id)
                    for tender in tenders:
                        exist = self.mongo_connection.exist_in_db(tender)
                        if not exist:
                            self.mongo_connection.save_to_db(tender)
                            model = self.http_worker.map.create_model(tender)
                            self.rabbitmq.publish_data(model, self.queue_name)
                            print(model)
                        else:
                            print("Document already exists")
                page += 1
                if page == page_count:
                    page = 1
                    page_count = self.http_worker.get_page_info(response_json)
            except Exception as ex:
                print(ex)


    def get_config(self, path):
        with open(path, encoding="utf-8") as file:
            json_object = json.loads(file.read())
        return json_object

if __name__ == '__main__':
    main = Main()
    main.run()
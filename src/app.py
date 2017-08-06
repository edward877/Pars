from src.bll.http_worker import HttpWorker
import configparser
from configparser import ConfigParser

class Main(object):
    def __init__(self):
        # self.config = self.get_config('./config.ini')
        #
        # print(self.config['Default']['base_url'])

        self.http_worker = HttpWorker()

    def start(self):
        self.http_worker.parse_tender()

    def get_config(self, path):
        config = ConfigParser()
        config.read(path)
        return config

if __name__ == '__main__':
    run = Main()
    run.start()
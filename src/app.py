from src.bll.http_worker import HttpWorker
import configparser
from configparser import ConfigParser

class Main(object):
    def __init__(self):
<<<<<<< HEAD
        # self.config = self.get_config('./config.ini')
        #
        # print(self.config['Default']['base_url'])

        self.http_worker = HttpWorker()
=======
        self.config = self.get_config('./config.ini')

        print(self.config['Default']['base_url'])

        self.http_worker = HttpWorker(self.config)
>>>>>>> 2b51de88fe8a4a5426a70b46373ebd0d0631b0a1

    def start(self):
        self.http_worker.parse_tender()

    def get_config(self, path):
        config = ConfigParser()
        config.read(path)
        return config

if __name__ == '__main__':
    run = Main()
    run.start()
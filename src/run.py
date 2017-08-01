from src.bll.http_worker import HttpWorker


class Run(object):
    def main(self):
        self.http_worker = HttpWorker()
        self.http_worker.do_work()

if __name__ == '__main__':
    run = Run()
    run.main()

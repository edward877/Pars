import unittest
from src.bll.http_worker import HttpWorker

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)
    def setUp(self):
        self.http_worker = HttpWorker()

    def test_parsing(self):
        get = self.http_worker.get_html('86982')
        json = self.http_worker.parse_html(get)
        result = '0'
        field = 'Количество участников, занявших места ниже первого, с которыми возможно заключение договора по результатам процедуры'
        self.assertEqual(result, json.get(field))


if __name__ == '__main__':
    unittest.main()
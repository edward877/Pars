import unittest
from src.bll.http_worker import HttpWorker

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)
    def setUp(self):
        self.http_worker = HttpWorker()

    def test_parsing(self):
        tender_id = '88313'
        url = 'https://223.rts-tender.ru/supplier/auction/Trade/View.aspx?Id=' + tender_id
        get = self.http_worker.get_html(url)
        json = self.http_worker.parse_html(get, tender_id)
        result = '1'
        field = 'Количество участников, занявших места ниже первого, с которыми возможно заключение договора по результатам процедуры'
        self.assertEqual(result, json.get(field))


if __name__ == '__main__':
    unittest.main()
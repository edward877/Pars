from urllib import request
import urllib, json

class HttpWorker(object):
    def __init__(self):
        self.base_url = 'https://223.rts-tender.ru/supplier/auction/Trade/'
        self.url_search = self.base_url + 'Search.aspx?jqGridID=BaseMainContent_MainContent_jqgTrade&rows=10&sidx=PublicationDate&sord=desc&page={}'
        self.url_view = self.base_url + 'View.aspx?Id={}'

    def reqest_page(self, page_number):
        response = urllib.request.urlopen(self.url_search.format(page_number))
        json_bytes = response.read()
        response_json = json.loads(json_bytes.decode('utf-8'))
        return response_json

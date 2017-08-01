import urllib.request
import requests
import json
import re

from bs4 import BeautifulSoup

BASE_URL = 'https://223.rts-tender.ru/supplier/auction/Trade/'
elements = []


class HttpWorker(object):
    def do_work(self):
        page_request = 'Search.aspx?jqGridID=BaseMainContent_MainContent_jqgTrade&rows=10&sidx=PublicationDate&sord=desc&page='
        response = self.get_json(BASE_URL + page_request + "1")
        total, num_last_elements = self.get_page_info(response)
        page = 1
        element = 10
        while page <= total:
            if page == total:
                element = int(num_last_elements)
            if page != 1:
                response = self.get_json(BASE_URL + page_request + str(page))
            self.parse_json(response, element)
            page += 1

    def get_json(self, url):
        response = urllib.request.urlopen(url)
        return response.read()

    def get_page_info(self, json_bytes):
        parsed_string = json.loads(str(json_bytes, 'utf-8'))
        total = parsed_string["total"]
        records = str(parsed_string["records"])
        return total, records[-1]

    def parse_json(self, json_bytes, element):
        parsed_string = json.loads(str(json_bytes, 'utf-8'))
        i = 0
        while i < element:
            page_id = parsed_string["rows"][i]['cell'][1]
            i += 1
            if page_id in elements:
                continue
            elements.append(page_id)
            print(page_id)
            self.get_html(page_id)
            self.parse_html(self.get_html(page_id))

    def get_html(self, page_id):
        id_request = 'View.aspx?Id='
        response = requests.post(BASE_URL + id_request + page_id)
        return response.text

    def parse_html(self, html):
        soup = BeautifulSoup(html, "lxml")
        tender = soup.find_all('fieldset', class_="openPart")
        my_dict = {}
        for i in tender:
            label = i.select('label')[0].get_text().strip()
            span = i.select('span')[0].get_text().strip()
            if label in my_dict:
                label = self.set_new_label(label, my_dict)
            my_dict[re.sub(r'\s+', ' ', label)] = re.sub(r'\s+', ' ', span)
        my_dict["Заказчик"] = self.parse_customer(soup)
        # print(my_dict)
        return my_dict

    def set_new_label(self, label, my_dict):
        index = 2
        while 1:
            if label + str(index) in my_dict:
                index += 1
            else:
                label += str(index)
                my_dict["Количество лотов"] = index
                return label

    def parse_customer(self, soup):
        tender = soup.find('div', class_="js-customerInfo").find_all('fieldset', class_="")
        customer = {}
        for i in tender:
            label = i.select('label')[0].get_text().strip()
            span = i.select('span')[1].get_text().strip()
            customer[re.sub(r'\s+', ' ', label)] = re.sub(r'\s+', ' ', span)
        return customer

if __name__ == '__main__':
    http_worker = HttpWorker()
    http_worker.main()
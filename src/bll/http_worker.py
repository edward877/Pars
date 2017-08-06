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
        json = self.get_json(BASE_URL + page_request + "1")
        total, num_last_elements = self.get_page_info(json)
        page = 3
        num_element = 10
        while page <= total:
            if page == total:
                num_element = int(num_last_elements)
            if page != 1:
                json = self.get_json(BASE_URL + page_request + str(page))
            list_page_id = self.parse_json_pages(json, num_element)
            for page_id in list_page_id:
                self.parse_html(self.get_html(BASE_URL + 'View.aspx?Id=' + page_id), page_id)
            page += 1

    def get_json(self, url):
        response = urllib.request.urlopen(url)
        return response.read()

    def get_page_info(self, json_bytes):
        parsed_string = json.loads(str(json_bytes, 'utf-8'))
        total = parsed_string["total"]
        records = str(parsed_string["records"])
        return total, records[-1]

    def parse_json_pages(self, json_bytes, num_element):
        parsed_string = json.loads(str(json_bytes, 'utf-8'))
        i = 0
        list_page_id = []
        while i < num_element:
            page_id = parsed_string["rows"][i]['cell'][1]
            i += 1
            list_page_id.append(page_id)
        return list_page_id

    def get_html(self, url):
        response = requests.post(url)
        return response.text

    def parse_html(self, html, page_id):
        soup = BeautifulSoup(html, "lxml")
        my_dict = self.parse_common(soup)
        my_dict["Номер"] = page_id
        my_dict["Заказчик"] = self.parse_customer(soup)
        my_dict["Документы"] = self.parse_attachments(soup, page_id)
        my_dict['Лоты'] = self.parse_lots(soup)
        print(my_dict)
        return my_dict

    def parse_common(self, soup):
        tender = soup.find('div', class_='top-section form_block form_inline').find_all('fieldset', class_="openPart")
        common = {}
        for i in tender:
            label = i.select('label')[0].get_text().strip()
            span = i.select('span')[0].get_text().strip()
            common[self.remove_meny_spaces(label)] = self.remove_meny_spaces(span)
        return common

    def parse_customer(self, soup):
        tender = soup.find('div', class_="js-customerInfo").find('fieldset', class_="")
        url = tender.select('a')[0].attrs["href"]
        html = self.get_html(url)
        soup = BeautifulSoup(html, "lxml")
        tender = soup.find('div', id="BaseMainContent_MainContent_divOrganisationInfo").find_all('fieldset')
        customer = {}
        for i in tender:
            label = i.select('label')[0].get_text().strip()
            span = i.select('span')[0].get_text().strip()
            customer[self.remove_meny_spaces(label)] = self.remove_meny_spaces(span)
        return customer

    def parse_attachments(self, soup, page_id):
        attachments = {}
        str_href = "https://223.rts-tender.ru/files/FileDownloadHandler.ashx?FileGuid="
        json_bytes = self.get_json(BASE_URL + '/View.aspx?Id=' + page_id + '&jqGridID=BaseMainContent_MainContent_jqgTradeDocs&rows=100&page=1')
        parsed_string = json.loads(str(json_bytes, 'utf-8'))
        if parsed_string == []:
            return parsed_string
        page = 1
        index = 1
        while 1:
            for row in parsed_string['rows']:
                attachments[index] = {'href' : str_href + row['id'], 'name' : row['cell'][1]}
                index += 1
            if page < parsed_string['total']:
                page += 1
                json_bytes = self.get_json(BASE_URL + '/View.aspx?Id=' + page_id + '&jqGridID=BaseMainContent_MainContent_jqgTradeDocs&rows=100&page=' + page)
                parsed_string = json.loads(str(json_bytes, 'utf-8'))
            else:
                break
        return attachments

    def parse_lots(self, soup):
        tender = soup.find('div', id="tradeLotsList").find_all('div', class_='tradeLotInfo labelminwidth')
        lots = {}
        index = 1
        lots['Количество лотов'] = len(tender)
        for lot in tender:
            fieldsets = lot.find_all('fieldset', class_="openPart")
            one ={}
            for fieldset in fieldsets:
                label = fieldset.select('label')[0].get_text().strip()
                span = fieldset.select('span')[0].get_text().strip()
                one[self.remove_meny_spaces(label)] = self.remove_meny_spaces(span)
            lots[index] = one
            index +=1
        return lots

    def remove_meny_spaces(self, text):
        return re.sub(r'\s+', ' ', text)

if __name__ == '__main__':
    http_worker = HttpWorker()
    http_worker.main()
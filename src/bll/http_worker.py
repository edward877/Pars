import urllib.request, requests, json, re, time, configparser

from bs4 import BeautifulSoup

# BASE_URL = 'https://223.rts-tender.ru/supplier/auction/Trade/'


class HttpWorker(object):
    def __init__(self):
        self.base_url = 'https://223.rts-tender.ru/supplier/auction/Trade/'
        self.url_search = self.base_url + '''Search.aspx?jqGridID=BaseMainContent_MainContent_jqgTrade&rows=10&sidx=
                                            PublicationDate&sord=desc&page={}'''
        self.url_view = self.base_url + 'View.aspx?Id={}'

    def parse_tender(self):
        json = self.get_json(self.url_search.format(1))
        pages_count, num_last_elements = self.get_page_info(json)
        page = 1
        num_element = 10
        while page <= pages_count:
            try:
                if page == pages_count:
                    num_element = int(num_last_elements)
                if page != 1:
                    json = self.get_json(self.url_search.format(page))
                list_page_id = self.parse_json_pages(json, num_element)
                for page_id in list_page_id:
                    html = self.get_html(self.url_view.format(page_id))
                    self.parse_html(html, page_id)
                page += 1
            except Exception as ex:
                print(ex)

    def get_json(self, url) -> dict:
        response = urllib.request.urlopen(url)
        attempts = 0
        while response.status != 200:
            if attempts < 5:
                time.sleep(3)
                response = urllib.request.urlopen(url)
                attempts += 1
            else:
                raise ConnectionAbortedError('Can`t get response from page')
        json_bytes = response.read()
        response_json = json.loads(json_bytes.decode('utf-8'))
        return response_json

    def get_page_info(self, json) -> [int, str]:
        parsed_string = json
        pages_count = parsed_string["total"]
        records = str(parsed_string["records"])
        return pages_count, records[-1]

    def parse_json_pages(self, json, num_element) -> list:
        parsed_string = json
        i = 0
        list_page_id = []
        while i < num_element:
            page_id = parsed_string["rows"][i]['cell'][1]
            i += 1
            list_page_id.append(page_id)
        return list_page_id

    def get_html(self, url) -> str:
        response = requests.post(url)
        return response.text

    def parse_html(self, html, page_id) -> dict:
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
            label, span = self.get_key_value(i)
            common[label] = re.sub(r'\s+', ' ', span)
        return common

    def parse_customer(self, soup):
        tender = soup.find('div', class_="js-customerInfo").find('fieldset', class_="")
        url = tender.select('a')[0].attrs["href"]
        html = self.get_html(url)
        soup = BeautifulSoup(html, "lxml")
        tender = soup.find('div', id="BaseMainContent_MainContent_divOrganisationInfo").find_all('fieldset')
        customer = {}
        for i in tender:
            label, span = self.get_key_value(i)
            customer[re.sub(r'\s+', ' ', label)] = re.sub(r'\s+', ' ', span)
        return customer

    def parse_attachments(self, soup, page_id):
        attachments = {}
        str_href = "https://223.rts-tender.ru/files/FileDownloadHandler.ashx?FileGuid="
        parsed_string = self.get_json(self.url_view.format(page_id) + '&jqGridID=BaseMainContent_MainContent_jqgTradeDocs&rows=100&page=1')
        page = 1
        index = 1
        while True:
            for row in parsed_string['rows']:
                attachments[index] = {'href' : str_href + row['id'], 'name' : row['cell'][1]}
                index += 1
            if page < parsed_string['total']:
                page += 1
                parsed_string = self.get_json(self.url_view.format(page_id) + '&jqGridID=BaseMainContent_MainContent_jqgTradeDocs&rows=100&page=' + page)
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
                label, span = self.get_key_value(fieldset)
                key = self.remove_many_spaces(label)
                value = self.remove_many_spaces(span)
                one[key] = value
            lots[index] = one
            index +=1
        return lots

    def get_key_value(self, node):
        label = node.select('label')[0].get_text().strip()
        span = node.select('span')[0].get_text().strip()
        return label, span

    def remove_many_spaces(self, text):
        return re.sub(r'\s+', ' ', text)

if __name__ == '__main__':
    http_worker = HttpWorker()
    http_worker.parse_tender()
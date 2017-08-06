import urllib.request, requests, json, re, time, configparser

from bs4 import BeautifulSoup


class HttpWorker(object):
    def __init__(self):
        self.base_url = 'https://223.rts-tender.ru/supplier/auction/Trade/'
        self.url_search = self.base_url + 'Search.aspx?jqGridID=BaseMainContent_MainContent_jqgTrade&rows=10&sidx=PublicationDate&sord=desc&page={}'
        self.url_view = self.base_url + 'View.aspx?Id={}'

    def parse_tender(self):
        response_json = self.get_json(self.url_search.format(1))
        page_count = self.get_page_info(response_json)
        page = 2
        while page <= page_count:
            try:
                if page != 1:
                    response_json = self.get_json(self.url_search.format(page))
                list_tender_id = self.parse_json_pages(response_json)
                for tender_id in list_tender_id:
                    html = self.get_html(self.url_view.format(tender_id))
                    tenders = self.parse_html(html, tender_id)
                    for tender in tenders:
                        print(tender)
                page += 1
                if page == page_count:
                    page=1
                    page_count = self.get_page_info(response_json)
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

    def get_page_info(self, json) -> int:
        pages_count = json["total"]
        return pages_count

    def parse_json_pages(self, json) -> list:
        parsed_string = json
        list_tender_id = []
        for i in parsed_string["rows"]:
            page_id = i['cell'][1]
            list_tender_id.append(page_id)
        return list_tender_id

    def get_html(self, url) -> str:
        response = requests.post(url)
        return response.text

    def parse_html(self, html, page_id) -> dict:
        soup = BeautifulSoup(html, "lxml")
        my_dict = self.parse_common(soup)
        my_dict["Номер"] = page_id
        my_dict["Документы"] = self.parse_attachments(page_id)
        my_dict["Сведения о контактном лице"] = self.parse_contacts(soup)
        for lot in self.parse_lots(soup).values():
            my_dict['Лот'] = lot
            yield my_dict

    def parse_common(self, soup):
        tender = soup.find('div', class_='top-section form_block form_inline').find_all('fieldset', class_="openPart")
        common = {}
        for fieldset in tender:
            key, value = self.get_key_value(fieldset)
            common[key] = value
        return common

    def parse_contacts(self, soup):
        tender = soup.find('div', class_='transactions form_block for_inline_block').find_all('fieldset', class_="openPart")
        contact = {}
        for fieldset in tender:
            key, value = self.get_key_value(fieldset)
            contact[key] = value
        return contact


    def parse_attachments(self, page_id):
        attachments = {}
        str_href = "https://223.rts-tender.ru/files/FileDownloadHandler.ashx?FileGuid="
        response_json = self.get_json(self.url_view.format(page_id)
                                      + '&jqGridID=BaseMainContent_MainContent_jqgTradeDocs&rows=100&page=1')
        if not response_json: return response_json
        page = 1
        index = 1
        while True:
            for row in response_json['rows']:
                attachments[index] = {'href': str_href + row['id'], 'name': row['cell'][1]}
                index += 1
            if page < response_json['total']:
                page += 1
                response_json = self.get_json(self.url_view.format(
                    page_id) + '&jqGridID=BaseMainContent_MainContent_jqgTradeDocs&rows=100&page=' + page)
            else:
                break
        return attachments

    def parse_lots(self, soup):
        list_lots = soup.find('div', id="tradeLotsList").find_all('div', class_='tradeLotInfo labelminwidth')
        lots = {}
        index = 1
        for lot in list_lots:
            fieldsets = lot.find_all('fieldset', class_="openPart")
            one ={}
            one['Заказчик']  = self.parse_customer(lot)
            one['Документы'] = self.parse_attachments_lot(lot)
            for fieldset in fieldsets:
                key, value = self.get_key_value(fieldset)
                one[key] = value
            lots[index] = one
            index +=1
        return lots

    def parse_customer(self, soup):
        response_json = soup.find('div', class_="js-customerInfo").find_all('fieldset', class_="")
        customer = {}
        for fieldset in response_json:
            key = self.get_key_value(fieldset)[0]
            value = fieldset.select('span')[1].get_text().strip()
            customer[key] = value
        url = response_json[0].select('a')[0].attrs["href"]
        html = self.get_html(url)
        soup = BeautifulSoup(html, "lxml")
        response_json = soup.find('div', id="BaseMainContent_MainContent_divOrganisationInfo").find_all('fieldset')
        for fieldset in response_json:
            key, value = self.get_key_value(fieldset)
            customer[key] = value
        return customer

    def parse_attachments_lot(self, soup):
        attachments = {}
        table = soup.find('div',
                    id="BaseMainContent_MainContent_ucTradeLotViewList_rptLots_ucTradeLotView_0_dvLotDocuments_0")
        if not table:
            return {}
        table = table.find_all('tr')
        i = 1
        for tr in table:
            if len(tr.select('td')) == 0: continue
            one = {}
            one['name'] = tr.select('td')[0].get_text().strip()
            one['href'] = tr.select('a')[0].attrs["href"]
            attachments[i] = one
            i += 1
        return attachments

    def get_key_value(self, node):
        key = node.select('label')[0].get_text().strip()
        key = re.sub(r'\s+', ' ', key)
        value = node.select('span')[0].get_text().strip()
        value = re.sub(r'\s+', ' ', value)
        return key, value

if __name__ == '__main__':
    http_worker = HttpWorker()
    http_worker.parse_tender()
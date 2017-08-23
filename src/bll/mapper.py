
class Map(object):
    def create_model(self, tender):
        model = {}
        model['id'] =  tender['Номер'] + " " + str(tender['Лот']['Номер лота'])
        model['attachments'] = self.attachments_model(tender['Документы'])
        model['customers'] = self.customers_model(tender['Лот']['Заказчик'])
        model['organisationsSearch'] = self.organisations_model(tender['Лот']['Заказчик'])
        model['platform'] = self.platform_model()
        model['multilot'] = tender['Лот']['Количество лотов']
        model['href'] = 'https://223.rts-tender.ru/supplier/auction/Trade/View.aspx?Id=' + tender['Номер']
        model['maxPrice'] = tender['Лот']['Начальная (максимальная) цена']
        model['number'] = tender['Номер']
        model['orderName'] = tender['Наименование закупки']
        model['region'] = tender['Лот']['Заказчик']['Регион']
        model['version'] = tender['Номер редакции извещения']

        model['json'] = tender
        model['okdp'] = None
        model['okpd'] = None
        model['okpd2'] = None
        model['publicationDateTime'] = None
        model['timestamp'] = None
        model['organisationsSearch'] = None
        model['guaranteeApp'] = None
        return model

    def attachments_model(self, attachments):
        array = []
        if attachments != []:
            i = 1
            while i <= len(attachments):
                attachment = attachments[i]
                i+=1
                realname = attachment['name']
                array.append({
                    "displayName": realname[:realname.rfind('.')],
                    "href": attachment['href'],
                    "realName": realname,
                    "publicationDateTime": None,
                    "size": None
                })
        return array

    def customers_model(self, customer):
        array = []
        array.append({
            "guid": None,
            "name": customer['Полное наименование'],
            "region": customer['Регион'],
        })
        return array

    def platform_model(self):
        array = []
        array.append({
            "href": 'https://223.rts-tender.ru',
            "name": None
        })
        return array

    def organisations_model(self, customer):
        organisations_search = customer['ИНН'] + " " + customer['КПП'] + " " + customer['Полное наименование'] + " " + customer['Регион']
        return organisations_search
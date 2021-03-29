import requests 
import json

from pprint import pprint

from datetime import datetime

import random


class iikoInterface:
    def __init__(self):
        self.user_id = ''
        self.user_secret = ''
        self.token_access = ''
        self.companyID = ''
        self.customer  = {}
        self.order = {}
        self.time_now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        self.order_dict = {}
        self.home_page = 'https://card.iiko.co.uk/api/'
        self.deliveryTerminal = ''


    def get_token_access(self, login, password):
        self.user_id = login
        self.user_secret = password
        link = "{}/0/auth/access_token?user_id={}&user_secret={}".format(self.home_page, self.user_id, self.user_secret)
        r = requests.get(link)
        self.token_access = r.text[1:-1]
        return self.token_access

    def get_token(self):
        return self.token_access

    def get_company_id(self):
        link = "{}0/organization/list?access_token={}&request_timeout=00%3A02%3A00".format(self.home_page, self.token_access)
        r = requests.get(link)
        self.companyID = r.text
        print(link)
        compid = json.loads(self.companyID)
        self.companyID = compid[0]['id']
        return self.companyID

    def complect_items(self, data_json):
        def check_id(db, code_item):
            for x in db:
                if x['code'] == code_item:
                    return x['id']
                    
        def check_delivery(value):
            if value.lower() == 'самовывоз':
                return True
            else:
                return False
                
        def edit_address_list(value):
            if value.lower() == 'улица' or value.lower() == 'проспект':
                return value[:2] + "."
            elif value.lower().lower() == 'переулок': 
                return value[:3].lower() + '.'
            elif value.lower() == 'бульвар':
                return value[:5].lower() + '.'
            elif value.lower() == 'въезд':
                return value.lower()
            else: return value.lower()
        
        def check_phone(phone):
            phone = phone.replace('(','').replace(')','').replace('-','').replace(' ', '')
            if phone[:3] != '+38':
                return "+380" + phone
            elif phone[0] == '8':
                return '+3' + phone
            else: return phone
            
            
                
        db = self.get_items_show(key='p') 
        order_dict = {}
        try:
            data = json.load(data_json)
        except:
            data = json.loads(data_json)
        #data = data_json
        #pprint(data)
        print("***"*110)
        print(data)
        print(data.values())
        print(data.keys())
        print(type(data))
        
        order_dict['organization'] = self.companyID
        order_dict['customer'] = {"id":'',
                                    "name":data['user_order'],
                                    "phone":check_phone(data['order_phone']),
                                    }
        order_dict['order'] = {"id":"",
                                    "date":self.time_now,
                                    "phone": check_phone(data['order_phone']),
                                    "isSelfService": check_delivery(data['order_delivery']['delivery']) ,
                                    "items":[],
                                    }
        for p in data['order_delivery']['products']:
            
            order_dict['order']['items'].append({"id": check_id(db, p['sku']),
                                                "name": p['name'],
                                                "amount": p['quantity'],
                                                "code":p['sku'],
                                                "sum":p['price'],
                                                "modifiers":[],
                                                })
            if 'пицца' in p['name']:
                order_dict['order']['items'].append({"modifiers": [{"id": "518e7bef-6db0-411b-a91b-3626f6b5b101",
                                                                    "name": "СОУС ДЛЯ ПИЦЦЫ",
                                                                    "amount": 1,
                }]})
                
                #if 'options' in data['payment']['products'][count]:
                #   order_dict['order']['items'] = [{"id": check_id(db, p['sku']),
        order_dict['order']["address"] = {
                                        "city": "Харьков",
                                        "street":data['order_street'] + " "+ edit_address_list(data['order_address_list']), #
                                        "home": data['order_home'],
                                        "housing": data['order_housing'],
                                        "apartment": data['order_apartment'],
                                        "entrance": data['order_entrance'],
                                        "floor": data['order_floor'],
                                        "comment": data['order_comment'], 
                                    }                           

        #print(order_dict)
        #f = open('newjson.json', 'w')
        #f.write(json.dumps(order_dict))
        
        print("ARRAAAY^::::::::::::::::::" , order_dict)
        self.order_dict = order_dict
        return order_dict


    def create_order(self,timeout = 1000, **list_order):
        headers = {'Content-type':'application/json'}
        link = "{}0/orders/add?access_token={}&request_timeout={}".format(self.home_page, str(self.token_access), str(timeout))
        
        self.companyID = self.companyID
        self.customer = set_customer()
        self.order = set_items()


        try:
            data_order = pre_create_order(**list_order)
            req = requests.post(link, data=json.dumps(data_order).replace("'", ''), headers=headers)
            response = req.json()
            return {'status':'ok',"response":response}
        except Exception as error:
            print('Возникла ошибка -- надо разибираться')
    
    def test_check_order(self, data,timeout='00%3A02%3A00'):
        headers = {'Content-type':'application/json', 'Accept':'*/*'}
        link_create_order = "{}0/orders/add?access_token={}&request_timeout={}".format(self.home_page, self.token_access,str(timeout))
        r = requests.post(link_create_order, json.dumps(data), headers=headers)
        return {"TYPE": "SEND ORDER","status": r.status_code, "Traceback:": r.text,"BODY": json.loads(r.request.body)}

    def check_order(self, order_dict, timeout='00%3A02%3A00'):
        headers = {'Content-type':'application/json', 'Accept':'*/*'}
        link_create_order = "{}0/orders/add?access_token={}&request_timeout={}".format(self.home_page, self.token_access,str(timeout))
        link_check_order = "{}0/orders/checkAddress?access_token={}&request_timeout={}&organizationId={}".format(self.home_page,self.token_access,str(timeout), self.companyID)
        
        data = self.complect_items(order_dict)

        
        r = requests.post(link_create_order, json.dumps(self.order_dict), headers=headers)
        print(link_create_order)
        print(r.text)
        print(r.content)
        print(r.status_code)
        print(r.request.body)

        return {"TYPE": "SEND ORDER","status": r.status_code, "Traceback:": r.text,"BODY": json.loads(r.request.body)}
        
    @staticmethod                                                                                                                                                                                                                                                                                                                                                
    def generator_id():
        example = '88529d26-efa5-48e2-af5e-96c245f62d26'
        array = 'stuvEFGabcdefghijklmno2345pqrHIJKL78MNOPQRSTUVwxyzABCDWXYZ169'
        l = str()
        for x in range(len(example)):
            #print('WARNING:', l)
            if x == 8 or x == 13 or x == 18 or x == 23:
                l+= '-'

            else:
                l += array[random.randint(0, 20)]

        return str(l)

    def type_order(self):
        link = "{}0/rmsSettings/getOrderTypes?organisation={}&access_token={}".format(self.home_page, self.companyID, self.token_access)
        r = requests.get(link)

        print(link)

    

    def get_items_show(self, key=''):
        """
        press 'g' for groups, 
        '1' for productCatefories 
        'p' for show products, 
        'r' see to reveision, 
        'u' for watch last upload date of products 
        or None if want to show all data"""

        link = "{}0/nomenclature/{}?access_token={}".format(self.home_page, self.companyID, self.token_access)
        r = requests.get(link)
        data_items = r.text
        data = json.loads(data_items)
        print(link)

        if key == 'g':
            for x in data['groups']:
                print('Группа товаров: ', x['name'], ' -- '  , x['id'], end='\n')
            
            data = data['groups']
        elif key == 'c':
            for x in data['productCategories']:
                print('Категории товаров: ', x['name'], ' -- ' , x['id'], end='\n')
            
            data = data['productCategories']
        elif key == 'p':
            for x in data['products']:
                print('Список товаров: ', x['code'], ' -- '  , x['name'], ' -- ', x['price'], ' -- ', x['id'], end='\n')

            data = data['products']
        elif key == 'r':
            print(data['reveision'])
        elif key == 'u':
            print('Последняя дата обновления: ', data['uploadDate'])
        else: 

            return data 
        return data 

    def list_delivery(self):
        link = "{}0/deliverySettings/getDeliveryTerminals?access_token={}&organization={}".format(self.home_page,self.token_access, self.companyID)
        r = requests.get(link)
        list_delvr = r.text
        return list_delvr

    def list_delivery_by_time(self, deliveryStatus ='DELIVERED', dateFrom="2020-12-08",dateTo="2020-12-13"):
        """ delivery_status: NEW, WAITING, ON_WAY, CLOSED, CANCELLED, DELIVERED, UNCONFIRMED """
        link = "{}0/orders/deliveryOrders?access_token={}&organization={}&dateFrom={}&dateTo={}&deliveryStatus={}&deliveryTerminalId={}&request_timeout=00%3A02%3A00'".format(self.home_page, self.token_access,self.companyID,dateFrom,dateTo,deliveryStatus,self.deliveryTerminal)
        r = requests.get(link)
        list_deliver_time = r.text
        print(link)

        return {"List of delivery time: ", r.content}


    def delivery_points(self):
        data = json.loads(self.list_delivery())
        self.deliveryTerminal = data['deliveryTerminals'][0]['deliveryTerminalId']
        return self.deliveryTerminal

    def get_list_cities_street(self):
        link = "{}0/cities/cities?access_token={}&organization={}".format(self.home_page, self.token_access, self.companyID)
        print(link)
        r = requests.get(link)

        return {"LIST OF CITY & STREET":"",'status': r.status_code, }


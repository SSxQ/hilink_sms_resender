import requests
import xmltodict

class Hilink(object):
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.headers = None

    def get_session_key(self):
        r = self.session.get(self.base_url + '/api/webserver/SesTokInfo')
        if r.status_code == 200:
            _dict = xmltodict.parse(r.text).get('response', None)
            self.headers = {
                'Content-Type': 'text/xml;charset=UTF-8',
                'Cookie': _dict['SesInfo'],
                '__RequestVerificationToken': _dict['TokInfo']
            }
        else:
            raise Exception
        

    def get_sms_list(self, count):
        post_data = '<?xml version = "1.0" encoding = "utf-8"?>\n'
        post_data += '<request><PageIndex>1</PageIndex><ReadCount>'+str(count)+'</ReadCount><BoxType>1</BoxType><SortType>0</SortType><Ascending>0</Ascending><UnreadPreferred>0</UnreadPreferred></request>\n'
        
        r = self.session.post(
            f'{self.base_url}/api/sms/sms-list',
            data = post_data,
            headers = self.headers
        )
        r.encoding = 'utf-8'
        
        return xmltodict.parse(r.text).get('response', None)


    def get_device_info(self):
        r = self.session.get(f'{self.base_url}/api/device/information', headers=self.headers)
        r.encoding = 'utf-8'

        return xmltodict.parse(r.text).get('response', None)


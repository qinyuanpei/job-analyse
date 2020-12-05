import requests
from bs4 import BeautifulSoup
import os
import json
import fake_useragent

class IpProxy(object):

    def __init__(self, baseUrl):
        self.baseUrl = baseUrl
    
    def getIpList(self, maxPage=10):
        if (os.path.exists('ipList.json')):
            with open('ipList.json','rt',encoding='utf-8') as fp:
                return json.load(fp)
        else:
            ipList = []
            page = 1
            while (page <= maxPage):
                response = requests.get(self.baseUrl.format(page=page))
                response.raise_for_status()
                soup = BeautifulSoup(response.text)
                trs = soup.find(name='table').find_all(name='tr')
                for tr in trs[1:]:
                    tds = tr.find_all(name='td')
                    ip = tds[0].text + ':' + tds[1].text
                    # if (self.validateProxy(ip)):
                    ipList.append(ip)
                page+=1
            with open('ipList.json','wt',encoding='utf-8') as fp:
                json.dump(ipList, fp)
            return ipList;

    def validateProxy(self, ip):
        try:
            ua = fake_useragent.UserAgent(verify_ssl=False)
            headers = {'User-Agent':ua.random}
            proxies = {
                'http': ip,
                'https': ip
            }
            response = requests.get('https://www.ipip.net/', timeout=5, headers=headers, proxies=proxies, verify=False)
            response.raise_for_status()
            return response.status_code == 200
        except:
            return False

if (__name__ == '__main__'):
    proxy = IpProxy('https://www.kuaidaili.com/free/inha/{page}')
    ipList = proxy.getIpList(2)
    
import requests
import json
import fake_useragent
from bs4 import BeautifulSoup
import os
import sys
sys.path.append('d:\\Projects\\Python\\job-analyse\\')
import Proxy.ipProxy
import random
import Store.mongoStore
import uuid

class BossSpider(object):

    def __init__(self):
        self.cityUrl = 'https://www.zhipin.com/wapi/zpCommon/data/city.json'
        self.proxyUrl = 'https://www.kuaidaili.com/free/'
        self.session = requests.session()

    def extractCity(self, cityName=None):
        if (os.path.exists('bossCity.json') and cityName != None):
            with open('bossCity.json', 'rt', encoding='utf-8') as fp:
                cityList = json.load(fp)
                for city in cityList:
                    if (city['name'] == cityName):
                        return city['code']
        else:
            response = requests.get(self.cityUrl)
            response.raise_for_status()
            json_data = response.json();
            if (json_data['code'] == 0 and json_data['zpData'] != None):
                cityList = []
                for level in json_data['zpData']['cityList']:
                    cityList.extend(self.unfoldLevel(level))
                with open('bossCity.json', 'wt', encoding='utf-8') as fp:
                    json.dump(cityList, fp)
                if (cityName != None):
                    for city in cityList:
                        if (city['name'] == cityName):
                            return city['code']
                else:
                    return json_data['zpData']['locationCity']['code']

    def unfoldLevel(self, level):
        result = []
        result.append({'name':level['name'], 'code':level['code']})
        if (level['subLevelModelList'] == None):
            return result
        else:
            for subLevel in level['subLevelModelList']:
                result.extend(self.unfoldLevel(subLevel))
        return result
        
    def extractCompany(self, soup):
        companyItem = {}
        
        # CompanyId
        ele = soup.find('div',attrs={'class':'company-text'})
        ele = ele.find(name='h3',attrs={'class':'name'})
        if (ele != None):
            companyItem['cId'] = ele.a['href'].replace('/gongsi/','').replace('.html','')
            companyItem['title'] = ele.a.text

        # 行业、经营状态、规模
        companyItem['industry'] = ''
        companyItem['finance'] = ''
        companyItem['size'] = ''
        ele = soup.find('div',attrs={'class':'company-text'})
        if (ele != None):
            companyItem['industry'] = ele.p.contents[0].text
            if (len(ele.p.contents) >= 3):
                companyItem['finance'] = ele.p.contents[2]
            if (len(ele.p.contents) >= 5):
                companyItem['size'] = ele.p.contents[4]

        # 标签
        companyItem['tags'] = []
        ele = soup.find(name='div',attrs={'class':'info-desc'})
        if (ele != None):
            companyItem['tags'] = ele.text.split('，')
        companyItem['href'] = 'https://www.zhipin.com/gongsi/{cId}.html'.format(cId=companyItem['cId'])
        return companyItem
    
    def extractJob(self, soup):
        jobItem = {}
        
        # JobId
        jobItem['jId'] = ''
        ele = soup.find(name='div',attrs={'class':'primary-box'})
        if (ele != None):
            jobItem['jId'] = ele['data-jid']
            jobItem['href'] = 'https://www.zhipin.com/job_detail/{jId}.html'.format(jId=jobItem['jId'])
            
        # 工作名称
        jobItem['title'] = ''
        ele = soup.find(name='span',attrs={'class':'job-name'})
        if (ele != None):
            jobItem['title'] = ele.a.text;
            
        # 工作区域
        jobItem['area'] = ''
        ele = soup.find(name='span',attrs={'class':'job-area'})
        if (ele != None):
            jobItem['area'] = ele.text
            
        # 工资、经验、学历
        jobItem['salary'] = ''
        jobItem['exps'] = ''
        jobItem['eduInfo'] = ''
        ele = soup.find(name='div',attrs={'class':'job-limit clearfix'})
        if (ele != None):
            jobItem['salary'] = ele.contents[1].text
            jobItem['exps'] = ele.contents[3].contents[0]
            jobItem['eduInfo'] = ele.contents[3].contents[2]

        # 标签
        ele = soup.find(name='div',attrs={'class':'tags'})
        jobItem['tags'] = []
        if (ele != None):
            tagItems = ele.find_all(name='span',attrs={'class':'tag-item'})
            tags = list(map(lambda x:x.text, tagItems))
            jobItem['tags'] = tags
        # 描述
        jobItem['desc'] = ''
        ele = soup.find(name='div',attrs={'class':'info-detail'}).find(name='div',attrs={'class':'detail-bottom'})
        if (ele != None):
            ele = ele.find(name='div',attrs={'class':'detail-bottom-text'})
            if (ele != None):
                jobItem['desc'] = ele.text
        return jobItem

    def makeRequest(self, url):
        try:
            ua = fake_useragent.UserAgent(verify_ssl=False)
            headers = {
                'User-Agent':ua.random,
                'TE':'Trailers',
                'Referer':url,
                'Cookie':'lastCity=101110100; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1606568014,1606654755,1606656178,1606835603; _bl_uid=wekCse4as0ImhFj6qj0aq194n5d5; __zp_stoken__=5553bGnN1XjBbAR5qGG0RXSQZPAh4PHhPOAA6PDFqDDJfDx4VVkAWMTlTX197VxlzAkcJd2U1TzpdZRcdCT8eaWgpPWA7LVERT2V7bi4gQWp2Ung6N3ccRk58aS9KRG8IBBYDZFdOHFs3bwl%2BdA%3D%3D; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1606837761; __g=-; __fid=3bd57571fa6cc97a6142b2770be6f858; ___gtid=-433946833; __c=1606835608; __a=23739502.1599489086.1606654759.1606835608.197.9.13.17'
            }
            proxy = Proxy.ipProxy.IpProxy(self.proxyUrl)
            ipList = proxy.getIpList()
            ip = random.choice(ipList)
            proxies = {
                'http': ip,
            }
            response = self.session.get(url, timeout=30, headers=headers, proxies=proxies, verify=False)
            response.raise_for_status()
            return response.text
        except Exception as ex:
            print(ex)
            return None

    def searchJobs(self, cityName, query, page=1):
        cityCode = self.extractCity(cityName)
        if (cityCode   != None):
            searchUrl = 'https://www.zhipin.com/job_detail/?query={query}&city={cityCode}&industry=&position=&page={page}'.format(cityCode=cityCode, query=query, page=str(page))
            html = self.makeRequest(searchUrl)
            soup = BeautifulSoup(html)
            details = soup.find_all(name='div',attrs={'class','job-primary'})
            jobItems = []
            companyItems = []
            for detail in details:
                jobItem = self.extractJob(detail)
                if (jobItem == None):
                    continue
                else:
                    jobItems.append(jobItem)
                companyItem = self.extractCompany(detail)
                if (companyItem == None):
                    continue
                else:
                    jobItem['company'] = companyItem['title']
                    jobItem['industry'] = companyItem['industry']
                    companyItems.append(companyItem)
            return (jobItems,companyItems)

if __name__ == '__main__':
    spider = BossSpider();

    # spider.extractCity('西宁')
    # spider.extractCity()
    # spider.extractJob('https://www.zhipin.com/job_detail/a046e72a1336b3820nd-0t6-EFc~.html')
    page = 2
    result = spider.searchJobs('西安','',page)
    while(len(result[0]) > 0 and len(result[1]) > 0):
        store = Store.mongoStore.MongoStore('default')
        page += 1
        print('正在抓取第' + str(page) + '页')
        store.insert('job',result[0])
        store.insert('company',result[1])


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

class ZhiLianSpider(object):

    def __init__(self):
        self.session = requests.session()
        self.proxyUrl = 'https://www.kuaidaili.com/free/'

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
        ele = soup.find('div',attrs={'class':'company-text'})
        if (ele != None):
            companyItem['industry'] = ele.p.contents[0].text
            companyItem['finance'] = ele.p.contents[2]
            companyItem['size'] = ele.p.contents[4]
        # 标签
        ele = soup.find(name='div',attrs={'class':'info-desc'})
        if (ele != None):
            companyItem['tags'] = ele.text.split('，')
        return companyItem
    
    def extractJob(self, soup):
        jobItem = {}
        # JobId
        ele = soup.find(name='div',attrs={'class':'primary-box'})
        if (ele != None):
            jobItem['jId'] = ele['data-jid']
        # 工作名称
        ele = soup.find(name='span',attrs={'class':'contentpile__content__wrapper__item__info__box__jobname__title'})
        if (ele != None):
            jobItem['title'] = ele.text;
        # 工作区域
        ele = soup.find(name='ul',attrs={'class':'job-contentpile__content__wrapper__item__info__box__job__demand'})
        if (ele != None):
            jobItem['area'] = ele.contents[0].text
            jobItem['exps'] = ele.contents[1].text
            jobItem['eduInfo'] = ele.contents[2].text

        # 工资、经验、学历
        ele = soup.find(name='p',attrs={'class':'contentpile__content__wrapper__item__info__box__job__saray'})
        if (ele != None):
            jobItem['salary'] = ele.text
        # 标签
        ele = soup.find(name='div',attrs={'class':'contentpile__content__wrapper__item__info__box__welfare job_welfare'})
        if (ele != None):
            tagItems = ele.find_all(name='div',attrs={'class':'contentpile__content__wrapper__item__info__box__welfare__item'})
            tags = list(map(lambda x:x.text, tagItems))
            jobItem['tags'] = tags
        # 描述
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
                # 'Referer':url,
                'Cookie':'x-zp-client-id=604da560-b85b-4bb9-8490-ff855a04d300; sts_deviceid=1760f31d861fa-0efc091273c9f28-4c3f2779-1049088-1760f31d863ff; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22662040894%22%2C%22first_id%22%3A%221760f31d87d9-04919f4ca1beeb8-4c3f2779-1049088-1760f31d8804f%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_refe…rt=84a950e77e054854b4d2f9d90826d063; acw_tc=2760826a16065748843918699e79278d6f3843d7bbcabf231429e46fa643ac; ssxmod_itna=eqjxBDcDuQ0=IRDl4iuiFD0ii=eiIhX5PENoeD/KAmDnqD=GFDK40ooO3wQoGC80oTwWYRW8G44ebPn03pQolhEjvF2Yx0aDbqGk3tc4ii9DCeDIDWeDiDG4Gml4GtDpxG=yDm4i3jxGeDe2IODY5DhxDC00PDwx0CjEiKWRFGCa71=tv4xt0DjxG1N40HWi3AoFSEq0H3Ix0k040Oya5kRcYDU74PElrd1gPDmxdDyPE=DiPkqmhUOD0tjoQxWQ=DBO6eZmr3ZAiiQixPeWR5T/rK/ih43BTFZCrKDDcl7YD===; ssxmod_itna2=eqjxBDcDuQ0=IRDl4iuiFD0ii=eiIhX5PENG9t5DRO1DGNewQGaKKjk5txKdMP08DedwD==='
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
        cityCode = cityName
        if (cityCode   != None):
            searchUrl = 'https://sou.zhaopin.com/?p={page}&jl={cityCode}&kw={query}'.format(cityCode=cityCode, query=query, page=str(page))
            html = self.makeRequest(searchUrl)
            soup = BeautifulSoup(html)
            details = soup.find_all(name='div',attrs={'class','contentpile__content__wrapper clearfix'})
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
                    companyItems.append(companyItem)
            return (jobItems,companyItems)

if __name__ == '__main__':
    spider = ZhiLianSpider();
    # spider.extractCity('西宁')
    # spider.extractCity()
    # spider.extractJob('https://www.zhipin.com/job_detail/a046e72a1336b3820nd-0t6-EFc~.html')
    result = spider.searchJobs('854','',1)
    store = Store.mongoStore.MongoStore('default')
    store.insert('job',result[0])
    store.insert('company',result[1])

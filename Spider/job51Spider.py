import requests
import json
import re
import fake_useragent
from bs4 import BeautifulSoup
import os
import sys
sys.path.append('d:\\Projects\\Python\\job-analyse\\')
import Proxy.ipProxy
import random
import Store.mongoStore

class Job51Spider(object):

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
        
    def extractCompany(self, detail):
        companyItem = {}
        # CompanyId
        companyItem['cId'] = detail['coid']
        companyItem['title'] = detail['company_name']
        # 行业、经营状态、规模
        companyItem['industry'] = detail['companyind_text']
        companyItem['finance'] = detail['companytype_text']
        companyItem['size'] = detail['companysize_text']
        # 标签
        companyItem['tags'] = detail['jobwelf_list']
        companyItem['href'] = detail['company_href']
        return companyItem
    
    def extractJob(self, detail):
        jobItem = {}
        # JobId
        jobItem['jId'] = detail['jobid']
        # 工作名称
        jobItem['title'] = detail['job_title'];
        # 工作区域
        jobItem['area'] = detail['workarea_text']
        for attr in detail['attribute_text']:
            if (attr in ['不限','经验不限'] or '年' in attr):
                jobItem['exps'] = attr
            if (attr in ['不限','高中','大专','硕士','本科','博士']):
                jobItem['eduInfo'] = attr
        # 工资、经验、学历
        jobItem['salary'] = detail['providesalary_text']
        # 标签
        jobItem['tags'] = detail['tags']
        if (len(jobItem['tags']) <= 0):
            jobItem['tags'] = detail['jobwelf_list']
        # 描述
        jobItem['desc'] = ''
        jobItem['href'] = detail['job_href']
        jobItem['industry'] = detail['companyind_text']
        jobItem['company'] = detail['company_name']
        return jobItem

    def makeRequest(self, url):
        try:
            ua = fake_useragent.UserAgent(verify_ssl=False)
            headers = {
                'User-Agent':ua.random,
                'TE':'Trailers',
            }
            proxy = Proxy.ipProxy.IpProxy(self.proxyUrl)
            ipList = proxy.getIpList()
            ip = random.choice(ipList)
            proxies = {
                'http': ip,
            }
            response = self.session.get(url, timeout=30, headers=headers, proxies=proxies, verify=False)
            response.raise_for_status()
            return response.content.decode("gbk")
        except Exception as ex:
            print(ex)
            return None

    def searchJobs(self, cityName, query, page=1):
        cityCode = cityName
        if (cityCode   != None):
            searchUrl = 'https://search.51job.com/list/200200,000000,0000,00,9,99,+,2,{page}.html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare='.format(page=str(page))
            html = self.makeRequest(searchUrl)
            data = re.findall('window.__SEARCH_RESULT__ =(.+)}</script>', str(html))[0] + "}"
            details = json.loads(data)['engine_search_result']
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
    spider = Job51Spider();
    store = Store.mongoStore.MongoStore('default')
    # spider.extractCity('西宁')
    # spider.extractCity()
    # spider.extractJob('https://www.zhipin.com/job_detail/a046e72a1336b3820nd-0t6-EFc~.html')
    page = 1;
    result = spider.searchJobs('854','',page)
    while(len(result[0]) > 0 and len(result[1]) > 0):
        page += 1
        print('正在抓取第' + str(page) + '页')
        result = spider.searchJobs('854','',page)
        store.insert('job',result[0])
        store.insert('company',result[1])

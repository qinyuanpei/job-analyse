import Store.mongoStore
from collections import Counter
from itertools import chain
from pyecharts.charts import Bar
from decimal import *
import re
from pyecharts import options as opts
from pyecharts.charts import Pie
from pyecharts.faker import Faker
import pyecharts.options as opts
from pyecharts.charts import WordCloud

# 加载岗位与公司信息
store = Store.mongoStore.MongoStore('default')
jobs = list(store.find('job',{}))
companies = list(store.find('company',{}))

# 提取岗位关键字
job_tags = []
for item in map(lambda x:x['tags'], jobs):
    if (item != None):
        job_tags.extend(item)

# 提取公司关键字
company_tags = []
for item in map(lambda x:x['tags'], companies):
    if (item != None):
        company_tags.extend(item)

# 行业构成分析
def analyse_industry():
    industries = list(map(lambda x:x['industry'],companies))
    counter = Counter(industries)
    counter = sorted(counter.items(),key = lambda x:x[1],reverse = True)[0:15]
    counter = dict(counter)
    c = (
        Pie()
        .add("",[list(z) for z in zip(counter.keys(), counter.values())])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="西安市求职招聘行业结构分析(Top15)",pos_left=325),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="left", orient="vertical"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        .render("西安市求职招聘行业结构分析(Top15).html")
    )

# 学历分布分析
def analyse_education():
    eduInfos = list(map(lambda x:x['eduInfo'], jobs))
    counter = Counter(eduInfos)
    counter = sorted(counter.items(),key = lambda x:x[1],reverse = True)
    counter = dict(counter)
    c = (
        Pie()
        .add("",[list(z) for z in zip(counter.keys(), counter.values())])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="西安市求职招聘学历结构分析",pos_left=325),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="left", orient="vertical"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        .render("./Reports/西安市求职招聘学历结构分析.html")
    )

# 工资分布分析
def analyse_salary():
    salaries = list(map(lambda x:x['avgSalary'], list(filter(lambda x:x['avgSalary'] != 0, jobs))))
    counter = Counter(salaries)
    counter = sorted(counter.items(),key = lambda x:x[1],reverse = True)
    records = {'3000元以下':0, '3000元-5000元':0, '5000元-8000元':0, '8000元-12000元':0, '12000元-15000元':0, '15000元以上':0}
    for (k,v) in counter:
        if (k < 3000):
            records['3000元以下'] += v
        if (k >= 3000 and k < 5000):
            records['3000元-5000元'] += v
        if (k >= 5000 and k < 8000):
            records['5000元-8000元'] += v
        if (k >= 8000 and k < 12000):
            records['8000元-12000元'] += v
        if (k >= 12000 and k < 15000):
            records['12000元-15000元'] += v
        if (k >= 15000):
            records['15000元以上'] += v
    counter = dict(records)
    c = (
        Pie()
        .add("",[list(z) for z in zip(counter.keys(), counter.values())])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="西安市求职招聘平均工资分析",pos_left=325),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="left", orient="vertical"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        .render("./Reports/西安市求职招聘平均工资分析.html")
    )

# 行业工资
def analyse_industry_salary():
    filtered = list(filter(lambda x:x['avgSalary'] != 0, jobs))
    salaries = {}
    for job in filtered:
        if (job['industry'] == ''):
            continue
        if salaries.get(job['industry']) == None:
            salaries[job['industry']] = [job['avgSalary']]
        else:
            salaries[job['industry']].append(job['avgSalary'])
    counter = {}
    for (industry, data) in salaries.items():
        counter[industry] = int(sum(data) / len(data))
    counter = sorted(counter.items(),key = lambda x:x[1],reverse = True)[0:15]
    counter = dict(counter)
    c = (
        Bar()
        .add_xaxis(list(counter.keys()))
        .add_yaxis("平均工资", list(counter.values()))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="西安市求职招聘行业工资分析(Top15)", pos_left=325),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="left", orient="vertical"),
        )
        .render("./Reports/西安市求职招聘行业工资分析(Top15).html")
    )

# 经验与工资关系
def analyse_exps_salary(industry=None):
    filtered = list(filter(lambda x:x['avgSalary'] != 0, jobs))
    if (industry != None):
        filtered = list(filter(lambda x:x['industry'] == industry, filtered))
    salaries = {}
    for job in filtered:
        if (job['exps'] == ''):
            continue
        exps = job['exps']
        exps = exps.replace('经验','')
        if (exps in ['1年','1年以内','2年','1-3年']):
            exps = '1-3年'
        if (exps in ['不限','经验不限']):
            exps = '经验不限'
        if (exps in ['3到4年','3到5年','3-4年','3-5年']):
            exps = '3-5年'
        if (exps in ['8到9年','5到10年','5到7年','8-9年','5-10年','5-7年']):
            exps = '5-10年'
        if salaries.get(exps) == None:
            salaries[exps] = [job['avgSalary']]
        else:
            salaries[exps].append(job['avgSalary'])
    counter = {}
    for (industry, data) in salaries.items():
        counter[industry] = int(sum(data) / len(data))
    c = (
        Bar()
        .add_xaxis(list(counter.keys()))
        .add_yaxis("平均工资", list(counter.values()))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="西安市求职招聘工作经验分析", pos_left=325),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="left", orient="vertical"),
        )
        .render("./Reports/西安市求职招聘行业工作经验分析.html")
    )

# 学历与工资关系
def analyse_eduInfo_salary(industry=None):
    filtered = list(filter(lambda x:x['avgSalary'] != 0, jobs))
    if (industry != None):
        filtered = list(filter(lambda x:x['industry'] == industry, filtered))
    salaries = {}
    for job in filtered:
        if (job['eduInfo'] == ''):
            continue
        eduInfo = job['eduInfo']
        if (eduInfo in ['学历不限','不限']):
            eduInfo = '学历不限'
        if salaries.get(eduInfo) == None:
            salaries[eduInfo] = [job['avgSalary']]
        else:
            salaries[eduInfo].append(job['avgSalary'])
    counter = {}
    for (eduInfo, data) in salaries.items():
        counter[eduInfo] = int(sum(data) / len(data))
    c = (
        Bar()
        .add_xaxis(list(counter.keys()))
        .add_yaxis("平均工资", list(counter.values()))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="西安市求职招聘学历与薪资关系分析", pos_left=325),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="left", orient="vertical"),
        )
        .render("./Reports/西安市求职招聘学历与薪资关系分析.html")
    )

# 平均工资前top的公司
def analyse_best_company(predicate, title, top=10):
    filtered = list(filter(lambda x:x['avgSalary'] != 0, jobs))
    if (predicate != None):
        filtered = list(filter(predicate, filtered))
    filtered = sorted(filtered, key=lambda x: x['avgSalary'], reverse=True)
    output = list(map(lambda x : (x['company'],int(x['avgSalary'])), filtered))[:top]
    bar=(
        Bar()
        .add_xaxis(list(map(lambda x:x[0], output)))
        .add_yaxis('平均工资',list(map(lambda x:x[1], output)))
        .set_series_opts(label_opts=opts.LabelOpts(position="top"))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-20)),
        )
        .render('.\Reports\{title}.html'.format(title=title)) 
    )

# 公司规模分析
def analyse_company_size(predicate, title):
    filtered = list(filter(lambda x:x['size'] != '' and x['size'] != None ,companies))
    if (predicate != None):
        filtered = list(filter(predicate, companies))
    filtered = list(map(lambda x:x['size'],filtered))
    counter = Counter(filtered)
    counter = sorted(counter.items(),key = lambda x:x[1],reverse = True)
    counter = filter(lambda x:x[0] != '', counter)
    counter = dict(counter)
    c = (
        Pie()
        .add("",[list(z) for z in zip(counter.keys(), counter.values())])
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title,pos_left=325),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="left", orient="vertical"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        .render('.\Reports\{title}.html'.format(title=title))
    )

# 公司财务分析
def analyse_company_finance(predicate, title):
    filtered = list(filter(lambda x:x['finance'] != '' and x['finance'] != None ,companies))
    if (predicate != None):
        filtered = list(filter(predicate, companies))
    filtered = list(map(lambda x:x['finance'],filtered))
    counter = Counter(filtered)
    counter = sorted(counter.items(),key = lambda x:x[1],reverse = True)
    counter = filter(lambda x:x[0] != '', counter)
    counter = dict(counter)
    c = (
        Pie()
        .add("",[list(z) for z in zip(counter.keys(), counter.values())])
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title,pos_left=325),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="left", orient="vertical"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        .render('.\Reports\{title}.html'.format(title=title))
    )

# 公司/职位词云分析
def analyse_extract_tags(words,title):
    words = list(filter(lambda x:x!='', words))
    data = Counter(words)
    c= (
        WordCloud()
        .add(series_name="热门词汇", data_pair=data.items(), word_size_range=[6, 66])
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title, title_textstyle_opts=opts.TextStyleOpts(font_size=23)
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True),
        )
        .render('.\Reports\{title}.html'.format(title=title))
    )

# 数据预处理
def pre_handling():
    for job in jobs:
        if not 'eduInfo' in job.keys():
            job['eduInfo'] = '不限'
        if not 'exps' in job.keys():
            job['exps'] = '不限'
        if '招' in job['eduInfo']:
            job['eduInfo'] = '不限'
        if job['salary'] != '':
            nums = re.findall('([1-9]\d*\.?\d*)|(0\.\d*[1-9])', job['salary'])
            if len(nums) > 1:
                nums = list(filter(lambda x : x != '', list(nums[0]) + list(nums[1])))
            else:
                nums = list(filter(lambda x : x != '', list(nums[0])))
            rate = 1
            if (('k' in job['salary']) or ('千' in job['salary'] or ('K' in job['salary']))):
                rate = 1000
            if (('万' in job['salary'])):
                rate = 10000
            if len(nums) > 1:
                job['minSalary'] = Decimal(nums[0]) * rate
                job['maxSalary'] = Decimal(nums[1]) * rate
            else:
                job['minSalary'] = Decimal(nums[0]) * rate
                job['maxSalary'] = Decimal(nums[0]) * rate
            if (('天' in job['salary']) or ('日' in job['salary'])):
                job['minSalary'] = job['minSalary'] * 30
                job['maxSalary'] = job['maxSalary'] * 30
            if ('年' in job['salary']):
                job['minSalary'] = job['minSalary'] / 12
                job['maxSalary'] = job['maxSalary'] / 12
            job['avgSalary'] = (job['minSalary'] + job['maxSalary']) / 2
        else:
            job['minSalary'] = 0
            job['maxSalary'] = 0
            job['avgSalary'] = 0
       
pre_handling()
analyse_industry()
analyse_education()
analyse_salary()
analyse_industry_salary()
analyse_eduInfo_salary()
analyse_exps_salary()
analyse_best_company(
    predicate=None, 
    title='西安市平均工资排名前10的公司', 
    top=10
)
analyse_best_company(
    predicate=lambda x:x['industry'] in ['计算机软件','互联网/电子商务','互联网'] and x['area'] != '异地招聘', 
    title='西安市IT行业排名前10的公司', 
    top=10
)
analyse_company_size(
    predicate=lambda x:x['industry'] in ['计算机软件','互联网/电子商务','互联网'],
    title='西安市求职招聘公司规模分析'
)
analyse_company_finance(
    predicate=lambda x:x['industry'] in ['计算机软件','互联网/电子商务','互联网'],
    title='西安市求职招聘公司类型分析'
)
analyse_extract_tags(
    words=job_tags,
    title='西安市求职者热词分析'
)
analyse_extract_tags(
    words=company_tags,
    title='西安市招聘者热词分析'
)




from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time
import re
from lxml import html
from selenium.webdriver.common.action_chains import ActionChains

# 策略标签整合
def strat(soup):
    tags = [element.text for element in soup.select("div.line2-tag")]
    if '私募 ' in tags:
        tags.remove('私募 ')
    if '正在运作 ' in tags:
        tags.remove('正在运作 ')

    return '、'.join(tags)

# 提取百分数
def extract_percentage(string):

    pattern = r'\d+\.?\d*%'
    matches = re.findall(pattern, string)

    return matches

# 无数据情况处理
def output_result(data):
    if '--' in data:
        return '--'
    else:
        return extract_percentage(data) 
    
# 加入自选
def add_to_zixuan(fund_codes, driver):

    not_found = []

    for fund in fund_codes:
        time.sleep(15)
        driver.find_element(By.XPATH,'//input[@id="nav_keyword"]').send_keys(fund)
        driver.find_element(By.XPATH,'//button[@class="comp-header-submit"]').click()
        time.sleep(30)

        try:
            driver.find_element(By.XPATH,'//span[@class="select"]').click()
        except:
            not_found.append(fund)
        
        time.sleep(5)
        if fund != fund_codes[-1]:
            driver.get('https://www.simuwang.com/user/option')

    if len(not_found) > 0:
        funds = '、'.join(not_found)
        print(funds + ' 不在私募排排网中！')

# 爬取数据
def grab_data(urls, driver):
    
    prod_info = {k:[] for k in ['基金名称', '管理人', '策略', '今年来收益', '成立来收益',
                           '成立以来年化', '成立来回撤', '成立以来夏普', '基金状态', 
                           '成立日期', '基金经理', '备案编号', '公司管理规模', 
                           '今年以来排名']}

    for url in urls:
        driver.get(url)
        time.sleep(30)
        page = driver.page_source
        soup = BeautifulSoup(page,'html.parser')

        prod_info['基金名称'].append(soup.select("h1.line1-title-name.ellipsis")[0].text) 
        prod_info['管理人'].append(soup.select("a.line4-baseinfo-value.blue")[0].text)
        prod_info['策略'].append(strat(soup))

        profit = soup.select("div.line3-common.flex-h-center")
        this_year_pf = profit[1].text
        all_time_pf  = profit[2].text
        prod_info['今年来收益'].append(output_result(this_year_pf))
        prod_info['成立来收益'].append(output_result(all_time_pf))

        data = list(soup.select("span.line4-baseinfo-value"))[1:]
        names = ['成立以来年化', '成立来回撤', '成立以来夏普', '基金状态', '成立日期', 
                '基金经理', '备案编号', '公司管理规模', '今年以来排名']
        for i in range(len(data)):
            prod_info[names[i]].append(data[i].text)
    
    return prod_info

# 收集基金网址
def collect_urls(soup):
    link_elements = soup.select("a[href]")

    urls = []
    for link_element in link_elements:
        url = link_element['href']
        if "https://dc.simuwang.com/product" in url:
            urls.append(url)
    
    return urls
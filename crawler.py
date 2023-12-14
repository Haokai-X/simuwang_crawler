from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time
import re
from lxml import html
from selenium.webdriver.common.action_chains import ActionChains
import utilities as ul

# 输入用户名和密码
username = '13834596916'
password = 'zxcvbnm1'

# 查询基金代码
fund_codes = ['SW4663', 'SXW323']

# 网址
simuwang_url = 'https://www.simuwang.com'
zixuan_url = 'https://www.simuwang.com/user/option'

# 唤醒浏览器
options = webdriver.EdgeOptions()
driver = webdriver.Edge(options=options)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
  """
})

# 登录私募排排网
driver.get(simuwang_url)                                                                        # 加载网站
driver.find_element(By.XPATH,'//button[@class="comp-login-method comp-login-b2"]').click()      # 点击账号密码登录
driver.find_element(By.XPATH,'//input[@name="username"]').send_keys(username)                   # 输入账号
driver.find_element(By.XPATH,'//input[@type="password"]').send_keys(password)                   # 输入密码
driver.find_element(By.XPATH,'//span[@class="checkbox"]').click()                               # 勾选同意协议
time.sleep(30)
driver.find_element(By.XPATH,'//button[@class="comp-login-btn"]').click()                       # 登录

# 搜索基金信息并加入自选
ul.add_to_zixuan(fund_codes, driver)
driver.get(zixuan_url)
time.sleep(15)

# 在自选中提取所有搜寻基金的网址
page = driver.page_source
soup = BeautifulSoup(page,'html.parser')
fund_urls = ul.collect_urls(soup)

# 爬取数据
prod_info = ul.grab_data(fund_urls, driver)

# 生成excel表格
prod_info = pd.DataFrame(prod_info)

with pd.ExcelWriter('prod_info.xlsx') as excel_writer:
    prod_info.to_excel(excel_writer, sheet_name='Sheet1', index=False)
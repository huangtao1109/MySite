import os
import time
from urllib import request

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from lxml import etree

from cmdb import models

browser = webdriver.Chrome()
browser.get('https://cn.bing.com/')
wait = WebDriverWait(browser, 50)


def search():
    browser.get('https://www.jd.com/')
    try:
        input = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#key")))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#search > div > div.form > button")))
        input[0].send_keys('python')
        submit.click()

        total = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > em:nth-child(1) > b')))
        html = browser.page_source
        prase_html(html)
        return total[0].text
    except TimeoutError:
        search()


def next_page(page_number):
    try:
        # 滑动到底部，加载出后三十个货物信息
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)
        # 翻页动作
        button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_bottomPage > span.p-num > a.pn-next > em')))
        button.click()
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#J_goodsList > ul > li:nth-child(60)")))
        # 判断翻页成功
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#J_bottomPage > span.p-num > a.curr"),
                                                    str(page_number)))
        html = browser.page_source
        prase_html(html)
    except TimeoutError:
        return next_page(page_number)


def prase_html(html):
    html = etree.HTML(html)
    items = html.xpath('//li[@class="gl-item"]')
    for i in range(len(items)):
        try:
            models.JDGoodsInfo.objects.create(title=html.xpath('//div[@class="p-name"]//em')[i].xpath('string(.)'),
                                              price=html.xpath('//div[@class="p-price"]//i')[i].text,
                                              commit=html.xpath('//div[@class="p-commit"]//a')[i].text)
            if html.xpath('//div[@class="p-img"]//img')[i].get('data-lazy-img') != "done":
                pic_url = 'http:' + html.xpath('//div[@class="p-img"]//img')[i].get('data-lazy-img')
                pic_name = './static/imgs/' + html.xpath('//div[@class="p-name"]//em')[i].xpath('string(.)') + '.jpg'
                if not os.path.exists(pic_name):
                    request.urlretrieve(pic_url, filename=pic_name)
            else:
                pic_url = 'http:' + html.xpath('//div[@class="p-img"]//img')[i].get('src')
                pic_name = './static/imgs/' + html.xpath('//div[@class="p-name"]//em')[i].xpath('string(.)') + '.jpg'
                if not os.path.exists(pic_name):
                    request.urlretrieve(pic_url, filename=pic_name)

        except:
            continue


def dynamic_crawler_main():
    # 爬取全部的商品信息（约600项）
    # total = int(search())
    # for i in range(2, total + 1):
    #     time.sleep(3)
    #     next_page(i)

    # 爬取一页商品信息（约60项）
    total = int(search())
    for i in range(2, 3):
        time.sleep(3)
        next_page(i)

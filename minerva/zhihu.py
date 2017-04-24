# -*- coding:utf-8 -*-

################################################################################		
#		
# Copyright (c) 2017 linzhi. All Rights Reserved		
#		
################################################################################		

"""
Created on 2017-04-19
Author: linzhi
"""

import BeautifulSoup
import cookielib
import hashlib
import json
import requests
import time
import traceback

from conf import constant
from lib import log
from html_parser import HtmlParser


class ZhihuParser(HtmlParser):
    """
    @brief: 解析知乎的页面，获取高赞评论
    """

    INDEX_URL = constant.SEED_URL['zhihu']
    LOGIN_URL = 'https://www.zhihu.com/login/email'
    CAPTCHA_URL = 'https://www.zhihu.com/captcha.gif?r='
    PROFILE_URL = "https://www.zhihu.com/settings/profile"

    TIMEOUT = 20

    login_result = False 

    def __init__(self):
        self.session = requests.Session()

        """
        # 抓取知乎的问题&答案无需登录,因此注释掉登录部分代码
        username = raw_input('请输入账户：')
        password = raw_input('请输入密码：')
        if self.login_result:
            log.info('模拟用户{}登陆知乎成功，开始抓取'.format(username))
        else:
            self.login(username, password)
            if not self.login_result:
                raise Exception("模拟登陆知乎失败")
        """

    def login(self, username, password):
        """
        @brief: 用户登录
        """

        self.session.cookies = cookielib.LWPCookieJar(filename='./conf/cookies')
        try:
            self.session.cookies.load(ignore_discard=True)
        except Exception as e:
            log.error("cookie 加载异常".format(traceback.format_exc()))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest'
        }

        # 如果已经登录了，则不用再次登录
        res = self.session.get(self.PROFILE_URL, headers=headers, allow_redirects=False)
        if res.status_code == 200:
            self.login_result = True
            log.info('用户{}已经登录,无需再使用验证码登录'.format(username))
            return 

        try:
            _xsrf = BeautifulSoup.BeautifulSoup(self.session.get(self.INDEX_URL, headers=headers).content).find('input', {'name': '_xsrf'})['value']
        except Exception as e:
            log.error('获取知乎登陆的xsrf参数失败: {}'.format(traceback.format_exc()))

        try:
            captcha_url = self.CAPTCHA_URL + str(int(time.time() * 1000)) + '&type=login'
            img = self.session.get(captcha_url, headers=headers)
            if img.status_code == 200:
                with open('./conf/captcha.jpg', 'wb') as fd:
                    fd.write(img.content)
                    fd.close()
        except Exception as e:
            log.error('获取知乎登陆的验证码失败: {}'.format(traceback.format_exc()))

        captcha = raw_input('请输入验证码：')

        data = {
            '_xrsf': _xsrf,
            'email': username,
            'password': password,
            'remember_me': 'true',
            'captcha': captcha
        }

        try:
            res = self.session.post(self.LOGIN_URL, headers=headers, data=data)
            if res.status_code == 200:
                res = res.json()
                if isinstance(res, dict) and 'r' in res and res.get('r') and 'msg' in res:
                    msg = res.get('msg').encode('utf8')
                    log.error('登录知乎账户失败,失败原因是: {}'.format(msg))
                # 登陆成功,保存cookie
                elif isinstance(res, dict) and 'r' in res and res.get('r') == 0:
                    log.info('用户{}登录知乎成功，返回:{}'.format(username, res))
                    self.login_result = True
                    self.session.cookies.save()
        except Exception as e:
            log.error('登录知乎失败, 异常信息: {}'.format(traceback.format_exc())) 

    def get_zhihu_info(self, url):
        """
        @brief: 获取知乎的问题以及高赞的用户评论
        @return: urls: (['xxx', ['xxx']]); result: {'title': xxx, 'content': xxx}
        """

        # 保存从content中提取的结果
        urls = None
        result = {}

        #urls, content = HtmlParser.get_content(url=url, session=self.session)
        urls, content = HtmlParser.get_content(url=url)

        # 如果不是知乎的问题详情页的url，则退出
        question_id = filter(str.isdigit, url.encode('utf8'))
        if not question_id or 'question/' not in url:
            return urls, result

        try:
            if content:
                log.info("当前抓取的知乎url是: {}".format(url))

                # 解析页面的问题
                question_title = content.find('h1', {'class': 'QuestionHeader-title'}).text.strip().encode('utf8')
                question_detail = content.find('div', {'class': 'QuestionHeader-detail'}).text.encode('utf8')

                result['url'] = url
                result['site'] = 'zhihu'
                result['question_id'] = int(question_id)
                result['question_title'] = question_title
                result['question_detail'] = question_detail

                # 解析页面的答案
                answers = content.findAll('div', {'class': 'List-item'})
                result['answers'] = {}
                for answer in answers:
                    tmp_result = {}
                    user_id = answer.find('div', {'class': 'ContentItem AnswerItem'}).get('name')
                    user_name = answer.find('img', {'class': 'Avatar AuthorInfo-avatar'}).get('alt').encode('utf8')
                    detail = answer.find('span', {'class': 'RichText CopyrightRichText-richText'}).text.encode('utf8')
                    tmp_result['user_name'] = user_name
                    tmp_result['content'] = detail
                    result['answers'][user_id] = tmp_result
        except Exception as e:
            log.error('解析知乎url: {} 异常，异常信息: {}'.format(url, traceback.format_exc()))
        finally:
            log.info('知乎url:{}, 解析结果: {}'.format(url, result))
            return urls, result


if __name__ == "__main__":
    zhihu = ZhihuParser()
    zhihu.get_zhihu_info(url='https://www.zhihu.com/question/56322619')





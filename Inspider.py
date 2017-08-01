# -*- coding: utf-8 -*-
__author__ = 'Orzitsu Loong'

import bs4
import json
import socket
import urllib.parse
import urllib.request


class HTTPMethod(object):
    def __init__(self, url, data={}, headers={}, cookie={}, timeout=10):
        if data:
            temp_data = urllib.parse.urlencode(data, safe='()')
            temp_data = temp_data.encode('utf-8')
            self.request = urllib.request.Request(url, data=temp_data)
        else:
            url = urllib.parse.quote(url, safe=';/?:@&=+$,')
            self.request = urllib.request.Request(url)
        if headers:
            for header in headers:
                self.request.add_header(header, headers[header])
        if cookie:
            cookie_string = ''
            for n, m in cookie.items():
                cookie_string += (n+'='+m+';')
            cookie_string = cookie_string.rstrip(';')
            self.request.add_header('Cookie', cookie_string)
        self.timeout = timeout
        self.url = url
        self.data = data

    def get(self):
        try:
            socket.setdefaulttimeout(self.timeout)
            response = urllib.request.urlopen(self.request)
            return response
        except urllib.error.HTTPError as e:
            print(self.url+' HTTP code ' + e)
            return e

    def post(self):
        try:
            socket.setdefaulttimeout(self.timeout)
            if not self.data:
                response = urllib.request.urlopen(self.request, data=None)
            else:
                response = urllib.request.urlopen(self.request)
            return response
        except urllib.error.HTTPError as e:
            print(self.url + ' HTTP code ' + e)
            return e


class Instagram:
    def __init__(self):
        self.default_headers = {'Host': 'www.instagram.com',
                                'Accept': '*/*',
                                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
                                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                                }
        self.cookie = {}
        self.csrf = ''

    # 读取用户名的主页
    def read_homepage_from(self, username='', hashtag='', headers={}):
        if username:
            url = 'https://www.instagram.com/'+username+'/'
        elif hashtag:
            url = 'https://www.instagram.com/explore/tags/'+hashtag+'/'
        if not headers:
            headers = self.default_headers
        attemps = 0
        success = False
        while attemps < 3 and not success:
            try:
                temp = HTTPMethod(url, headers=headers, cookie=self.cookie)
                html = temp.get()
                return html
            except:
                attemps += 1
                print('read_homepage_from: '+username+' '+hashtag+' error occurred. retry(%d)' %attemps)

    # 从主页中读取JS数据
    def analyze_html(self, html):
        soup = bs4.BeautifulSoup(html, "html.parser")
        temp = soup.find_all('script', {'type': 'text/javascript'})
        entry_data = temp[-4].text.replace('window._sharedData = ', '')
        entry_data = entry_data.rstrip(';')
        data = json.loads(entry_data)
        return data

    # 设置COOKIE
    def set_cookie_from_html(self, html):
        for a, b in html.info().items():
            if a == 'Set-Cookie':
                c = b.split(';')[0].split('=')
                self.cookie[c[0]] = c[1]

    # 读取CSRF TOKEN
    def analyze_csrf_token_from_data(self, data):
        self.csrf = data['config']['csrf_token']

    # 读取用户的初始化
    def read_user_init(self, username):
        html = self.read_homepage_from(username=username)
        self.set_cookie_from_html(html=html)
        data = self.analyze_html(html=html)
        self.analyze_csrf_token_from_data(data=data)
        temp = data['entry_data']['ProfilePage'][0]['user']
        user = {}
        for a, b in temp.items():
            if a != 'media':
                user[a] = b
        nodes = data['entry_data']['ProfilePage'][0]['user']['media']['nodes']
        count = data['entry_data']['ProfilePage'][0]['user']['media']['count']
        page_info = data['entry_data']['ProfilePage'][0]['user']['media']['page_info']
        return dict(user=user, nodes=nodes, count=count, page_info=page_info)

    def read_hashtag_init(self, name):
        html = self.read_homepage_from(hashtag=name)
        self.set_cookie_from_html(html=html)
        data = self.analyze_html(html=html)
        self.analyze_csrf_token_from_data(data=data)
        count = data['entry_data']['TagPage'][0]['tag']['media']['count']
        nodes = data['entry_data']['TagPage'][0]['tag']['media']['nodes']
        page_info = data['entry_data']['TagPage'][0]['tag']['media']['page_info']
        top_posts = data['entry_data']['TagPage'][0]['tag']['top_posts']['nodes']
        content_advisory = data['entry_data']['TagPage'][0]['tag']['content_advisory']
        return dict(nodes=nodes, count=count, page_info=page_info, top_posts=top_posts, content_advisory=content_advisory)

    def login_init(self):
        if not self.csrf:
            url = 'https://www.instagram.com/accounts/login/'
            temp = HTTPMethod(url, headers=self.default_headers)
            html = temp.get()
            self.set_cookie_from_html(html=html)
            self.csrf = self.cookie['csrftoken']

    def query_media_after(self, end_cursor, username='', user_id='', hashtag='', qry_type='ig_user', per=12):
        query_header = self.default_headers
        query_header['X-CSRFToken'] = self.csrf
        query_header['X-Instagram-AJAX'] = '1'
        query_header['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        query_header['X-Requested-With'] = 'XMLHttpRequest'
        if qry_type == 'ig_user':
            query_header['Referer'] = 'https://www.instagram.com/' + username
            query_id = '17862015703145017'
            variables = '{"id":"'+user_id+'","first":'+str(per)+',"after":"'+end_cursor+'"}'

        elif qry_type == 'ig_hashtag':
            url = 'https://www.instagram.com/explore/tags/'+hashtag+'/'
            query_header['Referer'] = urllib.parse.quote(url, safe=';/?:@&=+$,')
            query_id = '17875800862117404'
            variables = '{"tag_name":"'+hashtag+'","first":'+str(per)+',"after":"'+end_cursor+'"}'
        data = dict(variables=variables, query_id=query_id)
        print(data)
        attemps = 0
        success = False
        while attemps < 3 and not success:
            try:
                temp = HTTPMethod('https://www.instagram.com/graphql/query/', headers=query_header, cookie=self.cookie, data=data)
                code = temp.get()
                return code
            except:
                attemps += 1
                print('query_media_after: ' + end_cursor + ' error occurred. retry(%d)' % attemps)

    def query_follow(self, username, user_id, query_type='followers', per=10, set_end_cursor='', error_stop=True):
        headers = self.default_headers
        headers['X-CSRFToken'] = self.csrf
        headers['X-Instagram-AJAX'] = '1'
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers['X-Requested-With'] = 'XMLHttpRequest'
        headers['Referer'] = 'https://www.instagram.com/'+username+'/'
        if query_type == 'followers':
            query_id = '17851374694183129'
        elif query_type == 'following':
            query_id = '17874545323001329'
        if set_end_cursor:
            variables = '{"id":"'+user_id+'","first":'+str(per)+',"after":"'+set_end_cursor+'"}'
        else:
            variables = '{"id":"'+user_id+'","first":'+str(per)+'}'
        data = dict(variables=variables, query_id=query_id)
        attemps = 0
        success = False
        while attemps < 3 and not success:
            try:
                temp = HTTPMethod('https://www.instagram.com/graphql/query/', headers=headers, cookie=self.cookie, data=data).get()
                temp_data = json.loads(temp.read().decode('utf-8'))
                if query_type == 'followers':
                    return temp_data['data']['user']['edge_followed_by']
                elif query_type == 'following':
                    return temp_data['data']['user']['edge_follow']
            except:
                attemps += 1
                print('query_follow: ' + username + ' error occurred. retry(%d)' % attemps)
        return False

    # context:   blended(default)/user/hashtag/place
    def search(self, keyword, context='blended'):
        url = 'https://www.instagram.com/web/search/topsearch/?context='+context+'&query='+keyword
        attemps = 0
        success = False
        while attemps < 3 and not success:
            try:
                temp = HTTPMethod(url, headers=self.default_headers).get()
                temp_data = json.loads(temp.read().decode('utf-8'))
                temp.close()
                return temp_data
            except:
                attemps += 1
                print('search keyword: ' + keyword + ' error occurred. retry(%d)' % attemps)

    def login(self, username, password):
        self.login_init()
        query_header = self.default_headers
        query_header['X-CSRFToken'] = self.csrf
        query_header['X-Instagram-AJAX'] = '1'
        query_header['X-Requested-With'] = 'XMLHttpRequest'
        query_header['Referer'] = 'https://www.instagram.com/accounts/login/'
        url = 'https://www.instagram.com/accounts/login/ajax/'
        data = dict(username=username, password=password)
        temp = HTTPMethod(url, headers=query_header, cookie=self.cookie, data=data)
        code = temp.post()
        temp_data = json.loads(code.read().decode('utf-8'))
        if temp_data['authenticated']:
            self.set_cookie_from_html(html=code)
            print('Successfully Logged in')
            return True
        else:
            print('Login failed')
            return False

    def user(self, username, per=12, page=0, set_end_cursor='', stop_id='', error_stop=True):
        data = self.read_user_init(username=username)
        if data['page_info']['end_cursor'] is not None and data['page_info']['has_next_page'] is True:
            loop = True
            times = 0
            if set_end_cursor:
                end_cursor = set_end_cursor
            else:
                end_cursor = data['page_info']['end_cursor']
            while loop:
                try:
                    code = self.query_media_after(user_id=data['user']['id'], username=username, end_cursor=end_cursor, per=per)
                    if code:
                        times += 1
                        temp_data = json.loads(code.read().decode('utf-8'))
                        code.close()
                        if times >= page > 0:
                            loop = False
                        if stop_id:
                            for temp in temp_data['data']['user']['edge_owner_to_timeline_media']['edges']:
                                if temp['node']['id'] == stop_id:
                                    loop = False
                        if temp_data['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor'] == end_cursor or temp_data['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page'] is False:
                            loop = False
                        else:
                            end_cursor = temp_data['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
                        for tmp1 in temp_data['data']['user']['edge_owner_to_timeline_media']['edges']:
                            data['nodes'].append(tmp1['node'])
                except:
                    data['nodes'] = data['nodes']
                    if error_stop:
                        loop = False
        return data

    def tag(self, name, per=9, page=0, set_end_cursor='', stop_id='', error_stop=True):
        data = self.read_hashtag_init(name=name)
        if data['page_info']['end_cursor'] is not None and data['page_info']['has_next_page'] is True:
            loop = True
            times = 0
            if set_end_cursor:
                end_cursor = set_end_cursor
            else:
                end_cursor = data['page_info']['end_cursor']
            while loop:
                try:
                    code = self.query_media_after(hashtag=name, end_cursor=end_cursor, qry_type='ig_hashtag', per=per)
                    if code:
                        times += 1
                        temp_data = json.loads(code.read().decode('utf-8'))
                        code.close()
                        if times >= page > 0:
                            loop = False
                        if stop_id:
                            for temp in temp_data['data']['hashtag']['edge_hashtag_to_media']['edges']:
                                if temp['node']['id'] == stop_id:
                                    loop = False
                        if temp_data['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor'] == end_cursor or temp_data['data']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page'] is False:
                            loop = False
                        else:
                            end_cursor = temp_data['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
                        for tmp1 in temp_data['data']['hashtag']['edge_hashtag_to_media']['edges']:
                            data['nodes'].append(tmp1['node'])
                        data['page_info'] = temp_data['data']['hashtag']['edge_hashtag_to_media']['page_info']
                except:
                    data['nodes'] = data['nodes']
                    if error_stop:
                        loop = False
        return data

    def media(self, code_or_node):
        if type(code_or_node) is dict:
            # input is node
            if 'code' in code_or_node.keys():
                code = code_or_node['code']
            elif 'shortcode' in code_or_node.keys():
                code = code_or_node['shortcode']
        elif type(code_or_node) is str:
            # input is code
            code = code_or_node
        url = 'https://www.instagram.com/p/'+code+'/?__a=1'
        temp = HTTPMethod(url=url, headers=self.default_headers, cookie=self.cookie).get()
        temp_data = json.loads(temp.read().decode('utf-8'))
        return temp_data

    def follower(self, username, per=10, page=0, set_end_cursor='', stop_id=''):
        data = self.read_user_init(username=username)
        if data:
            user_id = data['user']['id']
            loop = True
            times = 0
            follower_list = []
            while loop:
                try:
                    temp_data = self.query_follow(username, user_id, 'followers', per=per, set_end_cursor=set_end_cursor)
                    if temp_data:
                        times += 1
                        if times >= page > 0:
                            loop = False
                        if temp_data['page_info']['has_next_page'] is False:
                            loop = False
                        else:
                            set_end_cursor = temp_data['page_info']['end_cursor']
                        for temp in temp_data['edges']:
                            follower_list.append(temp['node'])
                            if stop_id:
                                if temp['node']['id'] == stop_id:
                                    loop = False
                    else:
                        loop = False
                except:
                    loop = False
            return follower_list

    def following(self, username, per=10, page=0, set_end_cursor='', stop_id=''):
        data = self.read_user_init(username=username)
        if data:
            user_id = data['user']['id']
            loop = True
            times = 0
            following_list = []
            while loop:
                try:
                    temp_data = self.query_follow(username, user_id, 'following', per=per, set_end_cursor=set_end_cursor)
                    if temp_data:
                        times += 1
                        if times >= page > 0:
                            loop = False
                        if temp_data['page_info']['has_next_page'] is False:
                            loop = False
                        else:
                            set_end_cursor = temp_data['page_info']['end_cursor']
                        for temp in temp_data['edges']:
                            following_list.append(temp['node'])
                            if stop_id:
                                if temp['node']['id'] == stop_id:
                                    loop = False
                    else:
                        loop = False
                except:
                    loop = False
            return following_list


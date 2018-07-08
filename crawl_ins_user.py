#coding=utf-8

import json
import crawl_util
import re
from urllib import quote, urlencode


def crawl_tag(tag, cookies):
    url = 'https://www.instagram.com/explore/tags/%s/' % tag
    content = crawl_util.crawl(url)
    print cookies
    end_cursor = re.findall(r'"end_cursor":"([^"]+)"', content)
    userids = re.findall(r'"owner":{"id":"([^"]+)"}', content)
    end_cursor = end_cursor[0] if end_cursor else ''
    for page in range(10):
        if end_cursor:
            data = dict(query_hash='ded47faa9a1aaded10161a2ff32abb6b', variables={"tag_name":"%s" % tag,"first":page+1,"after":"%s" % end_cursor})
            variables = json.dumps(data['variables'])
            variables = quote(variables)
            url = 'https://www.instagram.com/graphql/query/?query_hash=%s&variables=%s' % (data['query_hash'], variables)
            print url
            content = crawl_util.crawl(url, cookies=cookies)
            data = json.loads(content)
            edge_hashtag_to_media = data['data']['hashtag']['edge_hashtag_to_media']
            edges = edge_hashtag_to_media['edges']
            end_cursor = edge_hashtag_to_media['page_info']['end_cursor']
            for edge in edges:
                userid = edge['node']['owner']['id']
                userids.append(userid)

        else:
            break

    return userids

def register(email, password):
    url = 'https://www.instagram.com/accounts/emailsignup/'
    headers = get_headers(url)
    api = 'https://www.instagram.com/accounts/web_create_ajax/'
    first_name= email.split('@')[0]
    username = first_name + '2018'
    data = dict(email=email, password=password, username=username, first_name=first_name, seamless_login_enabled=1, tos_version='row', opt_into_one_tap=False)
    content, cookies = crawl_util.crawl(api, data=data, headers=headers, method='post', need_return_cookies=True)
    data = json.loads(content)
    if 'user_id' in data:
        return cookies
    return None

def get_headers(url):
    content, cookies = crawl_util.crawl(url, need_return_cookies=True)
    csrftoken = ''
    for cookie in cookies:
        if cookie.name == 'csrftoken':
            csrftoken = cookie.value
            break
    return {'x-csrftoken': csrftoken}

def crawl_user_info(userid, cookies):
    url = 'https://i.instagram.com/api/v1/users/%s/info/' % userid
    content = crawl_util.crawl(url, cookies=cookies)
    return content

def login(username, password):
    url = 'https://www.instagram.com/'
    headers = get_headers(url)
    data = dict(username=username, password=password, queryParams={})
    api = 'https://www.instagram.com/accounts/login/ajax/'
    cookies = crawl_util.login(api, data, headers=headers, cookies=cookies)
    return cookies

def crawl_user_infos(tag):
    cookies = login('viking.liu@qq.com', 'viking138246s')
    userids = crawl_tag(tag, cookies)
    for userid in userids:
        user_info = crawl_user_info(userid, cookies)
        user_info = json.loads(user_info)
        print user_info


if __name__ == '__main__':
    #crawl_user_infos('marvel')
    print register('ad2ai2311@qq.com', 'viking123')


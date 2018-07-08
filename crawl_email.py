#coding=utf-8

import json
import crawl_util
import re
from urllib import quote, urlencode


def crawl_tag(tag, cookies):
    url = 'https://www.instagram.com/explore/tags/%s/' % tag
    content = crawl_util.crawl(url)
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


def crawl_user_info(userid, cookies):
    url = 'https://i.instagram.com/api/v1/users/%s/info/' % userid
    content = crawl_util.crawl(url, cookies=cookies)
    return content

def login(username, password):
    url = 'https://www.instagram.com/'
    content, cookies = crawl_util.crawl(url, need_return_cookies=True)
    csrftoken = ''
    for cookie in cookies:
        if cookie.name == 'csrftoken':
            csrftoken = cookie.value
            break
    data = dict(username=username, password=password, queryParams={})
    api = 'https://www.instagram.com/accounts/login/ajax/'
    headers = {'x-csrftoken': csrftoken}
    cookies = crawl_util.login(api, data, headers=headers, cookies=cookies)
    return cookies

def crawl_user_infos(tag):
    cookies = login('viking.liu@qq.com', 'viking138246s')
    userids = crawl_tag(tag, cookies)
    print userids
    for userid in userids:
        user_info = crawl_user_info(userid, cookies)
        user_info = json.loads(user_info)
        print user_info
        break


if __name__ == '__main__':
    crawl_user_infos('marvel')


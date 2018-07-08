# coding=utf8
import logging
import random
import re
import sys

from requests.exceptions import ProxyError

import requests
from requests.auth import HTTPDigestAuth

reload(sys)
sys.setdefaultencoding('utf-8')

h5_ua = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36'
pc_ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
app_ua = ''

session = requests.Session()


def parse_auth_url(url):
    matched = re.match('^(https?://)(.+?):(.+?)@(.+)$', url)
    if matched:
        prefix, username, password, suffix = matched.groups()
        auth = HTTPDigestAuth(username, password)
        url = prefix + suffix
        return auth, url
    return None, url


def crawl(url, h5=False, data=None, headers=None, cookies=None, auth=None, proxy=None, method='get',
          allow_redirects=True,
          timeout=15, need_return_headers=False, need_return_cookies=False, raise_exception=False, clear_cookies=False):
    headers = headers if headers is not None else {}
    cookies = cookies if cookies else {}
    headers['User-Agent'] = h5_ua if h5 else pc_ua
    if auth is None:
        auth, url = parse_auth_url(url)
    proxy_start = random.randrange(1000)
    for retry in range(3):
        if clear_cookies:
            session.cookies.clear()
        if isinstance(proxy, (list, tuple)):
            current_proxy = proxy[(proxy_start + retry) % len(proxy)]
        else:
            current_proxy = proxy
        try:
            logging.info('retry=%d h5=%s proxy=%s url=%s ' % (retry, h5, current_proxy, url))
            proxies = None
            if current_proxy:
                proxies = {"http": current_proxy, 'https': current_proxy}
            if method == 'post':
                rsp = session.post(url, proxies=proxies, headers=headers, cookies=cookies, data=data, auth=auth,
                                   allow_redirects=allow_redirects,
                                   timeout=timeout)
            elif method == 'put':
                rsp = session.put(url, proxies=proxies, headers=headers, cookies=cookies, data=data, auth=auth,
                                  allow_redirects=allow_redirects,
                                  timeout=timeout)
            else:
                rsp = session.get(url, proxies=proxies, headers=headers, cookies=cookies, data=data, auth=auth,
                                  allow_redirects=allow_redirects,
                                  timeout=timeout)
            content = rsp.content
            headers = rsp.headers
            cookies = rsp.cookies
            if need_return_headers and need_return_cookies:
                return content, headers, cookies
            if need_return_headers:
                return content, headers
            if need_return_cookies:
                return content, cookies
            return content
        except ProxyError as e:
            if raise_exception:
                raise
            logging.warn("Crawl while Server Error reason is %s", e.message)
            break
        except Exception as e:
            logging.exception(e)
    if need_return_headers and need_return_cookies:
        return None, None, None
    if need_return_headers or need_return_cookies:
        return None, None
    return None


def login(api, data, proxy=None, method='post', headers=None, cookies=None):
    content, cookies = crawl(api, data=data, headers=headers, cookies=cookies, allow_redirects=False, proxy=proxy, method=method,
                             need_return_cookies=True)
    return cookies


if __name__ == '__main__':
    api = 'https://account.nicovideo.jp/api/v1/login?show_button_twitter=1&site=niconico&show_button_facebook=1'

    user = {'mail_tel': 'yamaha_koji@yahoo.com', 'password': 'abTB0107!@#',
            'auth_id': str(int(random.random() * 1000000000))}
    data = dict(
        mail_tel=user['mail_tel'],
        password=user['password'],
        auth_id=user['auth_id']
    )

    print login(api, data)
    # print crawl('http://myip.ipip.net/', proxy='52.197.163.195:3128')

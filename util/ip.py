#!/usr/bin/env python
# -*- coding:utf-8 -*-
# import urllib3.util.connection as urllib3_cn
from re import compile
from os import name as os_name, popen
from socket import socket, getaddrinfo, gethostname, AF_INET, AF_INET6, SOCK_DGRAM
from logging import debug, error
try:
    # python2
    from urllib2 import urlopen, Request  # type: ignore
except ImportError:
    # python3
    from urllib.request import urlopen, Request
import ssl
import dnsquery

# IPV4正则
IPV4_REG = r'((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])'
# IPV6正则
# https://community.helpsystems.com/forums/intermapper/miscellaneous-topics/5acc4fcf-fa83-e511-80cf-0050568460e4
IPV6_REG = r'((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))'  # noqa: E501


def default_v4():  # 默认连接外网的ipv4
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("1.1.1.1", 53))
    ip = s.getsockname()[0]
    s.close()
    return ip


def default_v6():  # 默认连接外网的ipv6
    s = socket(AF_INET6, SOCK_DGRAM)
    s.connect(('1:1:1:1:1:1:1:1', 8))
    ip = s.getsockname()[0]
    s.close()
    return ip


def local_v6(i=0):  # 本地ipv6地址
    info = getaddrinfo(gethostname(), 0, AF_INET6)
    debug(info)
    return info[int(i)][4][0]


def local_v4(i=0):  # 本地ipv4地址
    info = getaddrinfo(gethostname(), 0, AF_INET)
    debug(info)
    return info[int(i)][-1][0]


def _open(url, reg):
    try:
        debug("open: %s", url)
        import urllib3.util.ssl_
        urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'
        res = urlopen(
            Request(url, headers={'User-Agent': 'Mozilla/5.0 ddns'}),  timeout=60
        ).read().decode('utf8', 'ignore')
        debug("response: %s",  res)
        return compile(reg).search(res).group()
    except Exception as e:
        error(e)


def _open_original(url, host):
    '''
    _open() 的删减
    直接返回 (不经过正则)

    :param url: 请求 url
    :param host: Host 头
    '''
    try:
        debug("open: %s", url)
        res = urlopen(
            Request(url, headers={
                'User-Agent': 'Mozilla/5.0 ddns',
                'Host': host
            }),  timeout=60
        ).read().decode('utf8', 'ignore')
        debug("response: %s",  res)
        return res
    except Exception as e:
        error(e)
        raise


def spliturl(url: str):
    '''
    :param url: 传入待处理的 url (`https://getip.wyf9.top:1145/test/path`)
    :return protocol: str: 协议 (`https`)
    :return hostname: str: 主机名 (`getip.wyf9.top`)
    :return port: **str**: 端口号 (`1145`)
    :return path: str: 路径 (`test/path`)
    '''
    try:
        protocol, url2 = url.split('://', 1)
    except ValueError:
        protocol = ''
        url2 = url
    try:
        host, path = url2.split('/', 1)
    except ValueError:
        host = url2
        path = ''
    try:
        hostname, port = host.split(':', 1)
    except ValueError:
        hostname = host
        port = ''
    return protocol, hostname, port, path


def public_v4(url="https://getip.wyf9.top/ip", reg=IPV4_REG):  # 公网IPV4地址 = spliturl(url)
    protocol, hostname, port, path = spliturl(url)
    query_ip = dnsquery.get_v4(hostname)
    # urllib3_cn.allowed_gai_family = allowed_gai_family_4 # change
    # # ret = _open(url, reg)
    query_url = f'{protocol}://{query_ip}'
    if port:
        query_url += f':{port}'
    query_url += f'/{path}'
    ret = _open_original(query_url, host=hostname)
    return ret


def public_v6(url="https://getip.wyf9.top/ip", reg=IPV6_REG):  # 公网IPV6地址
    # urllib3_cn.allowed_gai_family = allowed_gai_family_6 # change
    # # ret = _open(url, reg)
    # ret = _open_original(url)
    # return ret
    protocol, hostname, port, path = spliturl(url)
    query_ip = dnsquery.get_v6(hostname)
    # urllib3_cn.allowed_gai_family = allowed_gai_family_4 # change
    # # ret = _open(url, reg)
    query_url = f'{protocol}://[{query_ip}]'
    if port:
        query_url += f':{port}'
    query_url += f'/{path}'
    ret = _open_original(query_url, host=hostname)
    return ret


def _ip_regex_match(parrent_regex, match_regex):

    ip_pattern = compile(parrent_regex)
    matcher = compile(match_regex)

    if os_name == 'nt':  # windows:
        cmd = 'ipconfig'
    else:
        cmd = 'ip address || ifconfig 2>/dev/null'

    for s in popen(cmd).readlines():
        addr = ip_pattern.search(s)
        if addr and matcher.match(addr.group(1)):
            return addr.group(1)


def regex_v4(reg):  # ipv4 正则提取
    if os_name == 'nt':  # Windows: IPv4 xxx: 192.168.1.2
        regex_str = r'IPv4 .*: ((?:\d{1,3}\.){3}\d{1,3})\W'
    else:
        regex_str = r'inet (?:addr\:)?((?:\d{1,3}\.){3}\d{1,3})[\s/]'
    return _ip_regex_match(regex_str, reg)


def regex_v6(reg):  # ipv6 正则提取
    if os_name == 'nt':  # Windows: IPv4 xxx: ::1
        regex_str = r'IPv6 .*: ([\:\dabcdef]*)?\W'
    else:
        regex_str = r'inet6 (?:addr\:\s*)?([\:\dabcdef]*)?[\s/%]'
    return _ip_regex_match(regex_str, reg)

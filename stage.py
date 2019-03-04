#!/usr/bin/env python3

import argparse
import bs4
import requests
from urllib import parse

def main():
    parser=argparse.ArgumentParser()
    add=parser.add_argument
    add('group_name',choices=['snh48','bej48','gnz48','shy48','ckg48'])
    add('id',type=int)
    args=parser.parse_args()
    group_ids={'snh48':1,'bej48':2,'gnz48':3,'shy48':4,'ckg48':5}
    resp=requests.get('https://live.48.cn/Index/invedio/club/%d/id/%d'%(group_ids[args.group_name],args.id)).text
    try:
        url=bs4.BeautifulSoup(resp,'html.parser').find_all('input',id='chao_url')[0]['value']
    except IndexError:
        url=''
    if parse.urlparse(url).hostname=='ts.48.cn':
        url=url.replace('http://','https://')
    if url:
        print(url)

if __name__=='__main__':
    main()

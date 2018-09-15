#!/usr/bin/env python3

import argparse
import arrow
import requests

HEADERS={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'}

def main():
    parser=argparse.ArgumentParser()
    add=parser.add_argument
    add('url')
    args=parser.parse_args()
    first_resp=requests.head(args.url,headers=HEADERS).headers['Location'].replace('http://','https://')
    second_resp=requests.head(first_resp,headers=HEADERS).headers['Last-Modified']
    print(arrow.get(second_resp,'ddd, DD MMM YYYY HH:mm:ss ZZZ').to('Asia/Shanghai').strftime('%Y-%m-%dT%H:%M:%SZ'))

if __name__=='__main__':
    main()

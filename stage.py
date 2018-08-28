#!/usr/bin/env python3

import argparse
import re
import requests

def main():
    parser=argparse.ArgumentParser()
    add=parser.add_argument
    add('group_name',choices=['snh48','bej48','gnz48','shy48','ckg48'])
    add('id',type=int)
    args=parser.parse_args()
    path='/Index/invedio/id/%d'%args.id
    if args.group_name=='snh48':
        url='http://zhibo.ckg48.com%s'%path
    else:
        url='http://live.%s.com%s'%(args.group_name,path)
    try:
        print(re.findall('https?://.*\.m3u8[^"]*',requests.get(url).text)[0])
    except IndexError:
        pass

if __name__=='__main__':
    main()

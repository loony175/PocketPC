#!/usr/bin/env python3

import argparse
import arrow
import base64
import json
import pathlib
import re
import requests
from urllib import parse

def request_process(is_review,last_time,group_id,member_id,limit):
    resp=requests.post('https://plive.48.cn/livesystem/api/live/v1/memberLivePage',headers={'Content-Type':'application/json','version':'5.3.1','os':'android'},json={'lastTime':last_time,'groupId':group_id,'memberId':member_id,'limit':limit}).json()
    if is_review:
        data=resp['content']['reviewList']
    else:
        data=resp['content']['liveList']
    intermediate=[]
    for dict in data:
        info={}
        info['title']=dict['title']
        sub_title={}
        sub_title['raw']=dict['subTitle']
        sub_title['base64']=bytes.decode(base64.b64encode(str.encode(dict['subTitle'])))
        info['subTitle']=sub_title
        info['picPath']=['https://source.48.cn%s'%obj for obj in dict['picPath'].split(',')]
        start_time={}
        start_time['timestamp']=dict['startTime']
        start_time['datetime']=arrow.get(dict['startTime']/1000).to('Asia/Shanghai').strftime('%Y-%m-%dT%H:%M:%SZ')
        info['startTime']=start_time
        info['memberId']=dict['memberId']
        info['liveType']=dict['liveType']
        info['streamPath']=dict['streamPath'].replace('http://','https://')
        intermediate.append(info)
    return intermediate

def update_timestamp(intermediate):
    return [dict['startTime']['timestamp'] for dict in intermediate][-1]

def filter(intermediate,type,format,members):
    if type:
        intermediate=[dict for dict in intermediate if dict['liveType']==type]
    if format:
        intermediate=[dict for dict in intermediate if pathlib.Path(parse.urlparse(dict['streamPath']).path).suffix=='.%s'%format]
    if members:
        intermediate=[dict for dict in intermediate if dict['memberId'] in members]
    return intermediate

def main():
    parser=argparse.ArgumentParser()
    add=parser.add_argument
    add('-r','--review',action='store_true')
    add('-t','--last-time',type=int,default=0)
    add('-g','--group',type=int,choices=[0,10,11,12,13,14],default=0)
    add('-m','--member')
    add('-l','--limit',type=int,default=20)
    add('-T','--type',type=int,choices=[1,2])
    add('-f','--format',choices=['mp4','m3u8'])
    add('-M','--members',choices=['SII','NII','HII','X','Ft','B','E','J','G','NIII','Z','SIII','HIII','C','K'])
    add('-d','--date',nargs='?',const='today')
    add('-q','--quiet',action='store_true')
    add('-n','--sum',action='store_true')
    add('-N','--no-sum',action='store_true')
    args=parser.parse_args()
    member_ids=json.loads(open('member_id.json','r').read())
    members=None
    if args.member:
        member_id=member_ids[args.member]
    else:
        member_id=0
    if args.limit==0:
        args.limit=30000
    if args.date:
        m=re.match(r'^((?P<year>\d{4})-)?((?P<month>\d{2})-)?(?P<day>\d{2})?$',args.date)
        now=arrow.now('Asia/Shanghai')
        try:
            year=int(m.group('year') or now.year)
            month=int(m.group('month') or now.month)
            day=int(m.group('day') or now.day)
        except AttributeError:
            year=now.year
            month=now.month
            day=now.day
        base_timestamp=arrow.get(year,month,day,tzinfo='Asia/Shanghai').timestamp*1000
        args.last_time=base_timestamp+86400000
        args.limit=100
    num_request=args.limit
    if args.type or args.format:
        num_request*=2
    if args.members:
        num_request*=5
        if args.members in ['SII','NII','HII','X','Ft']:
            args.group=10
            gid=10
        elif args.members in ['B','E','J']:
            args.group=11
            gid=20
        elif args.members in ['G','NIII','Z']:
            args.group=12
            gid=30
        elif args.members in ['SIII','HIII']:
            args.group=13
            gid=40
        elif args.members in ['C','K']:
            args.group=14
            gid=50
        resp=requests.get('http://h5.snh48.com/resource/jsonp/members.php',params={'gid':gid}).json()
        member_names=[dict['sname'] for dict in resp['rows'] if dict['tname']==args.members]
        members=[]
        for member in member_names:
            try:
                members.append(member_ids[member])
            except KeyError:
                pass
    intermediate=request_process(args.review,args.last_time,args.group,member_id,num_request)
    if args.review:
        timestamp=update_timestamp(intermediate)
    intermediate=filter(intermediate,args.type,args.format,members)
    if args.review:
        if args.date:
            while update_timestamp(intermediate)>base_timestamp:
                new_intermediate=request_process(args.review,timestamp,args.group,member_id,num_request)
                if len(new_intermediate)==0:
                    break
                timestamp=update_timestamp(new_intermediate)
                new_intermediate=filter(new_intermediate,args.type,args.format,members)
                intermediate+=new_intermediate
            intermediate=[dict for dict in intermediate if dict['startTime']['timestamp']>=base_timestamp]
        else:
            while len(intermediate)<args.limit:
                new_intermediate=request_process(args.review,timestamp,args.group,member_id,num_request)
                if len(new_intermediate)==0:
                    break
                timestamp=update_timestamp(new_intermediate)
                new_intermediate=filter(new_intermediate,args.type,args.format,members)
                intermediate+=new_intermediate
            intermediate=intermediate[:args.limit]
    if args.quiet:
        stdout=[]
        for dict in intermediate:
            info={}
            info['title']=dict['title']
            info['subTitle']=dict['subTitle']['raw']
            info['startTime']=dict['startTime']['datetime']
            info['streamPath']=dict['streamPath']
            stdout.append(info)
    else:
        stdout=intermediate
    if not args.sum:
        print(json.dumps(stdout,indent=2,ensure_ascii=False))
        if not args.no_sum:
            print('%d objects found.'%len(stdout))
    else:
        print(len(stdout))

if __name__=='__main__':
    main()

#!/usr/bin/env python3

import json
import operator
import requests

def main():
    data=[]
    members=[]
    resp=requests.post('https://plive.48.cn/livesystem/api/live/v1/memberLivePage',headers={'Content-Type':'application/json','version':'5.3.1','os':'android'},json={'lastTime':0,'groupId':0,'memberId':0,'limit':30000}).json()
    for dict in sorted(resp['content']['reviewList'],key=operator.itemgetter('memberId')):
        if dict['memberId'] not in members:
            data.append(dict)
            members.append(dict['memberId'])
    members={}
    for dict in data:
        if dict['memberId']==4:
            member_name='呵呵姐'
        elif dict['memberId']==530431:
            member_name='呵呵妹'
        else:
            member_name=dict['title'].replace('的直播间（回放生成中）','').replace('的电台（回放生成中）','').replace('的（回放生成中）','')
        members[member_name]=dict['memberId']
    f=open('member_id.json','w')
    f.write(json.dumps(members,indent=2,ensure_ascii=False))
    f.write('\n')
    f.close()

if __name__=='__main__':
    main()

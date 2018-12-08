#!/usr/bin/env python3

import json
import operator
import re
import requests

def main():
    data=[]
    members=[]
    resp=requests.post('https://plive.48.cn/livesystem/api/live/v1/memberLivePage',headers={'Content-Type':'application/json','version':'5.3.2','os':'android'},json={'lastTime':0,'groupId':0,'memberId':0,'limit':40000}).json()
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
            member_name=re.match(r'^(.*)的.*（回放生成中）$',dict['title']).group(1)
        members[member_name]=dict['memberId']
    f=open('member_id.json','w')
    f.write(json.dumps(members,indent=2,ensure_ascii=False))
    f.write('\n')
    f.close()

if __name__=='__main__':
    main()

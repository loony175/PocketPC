#!/usr/bin/env python3

import json
import operator
import requests
import uuid

HEADERS={
    'Content-Type':'application/json',
    'User-Agent':'PocketFans201807/6.0.0 (iPhone; iOS 12.2; Scale/2.00)',
    'appInfo':json.dumps({
        'vendor':'apple',
        'deviceId':str(uuid.uuid4()).upper(),
        'appVersion':'6.0.0',
        'appBuild':'190409',
        'osVersion':'12.2.0',
        'osType':'ios',
        'deviceName':'iphone',
        'os':'ios',
    }),
}

def main():
    resp=requests.post('https://pocketapi.48.cn/user/api/v1/client/update/group_team_star',headers=HEADERS,json={}).json()
    data=sorted(resp['content']['starInfo'],key=operator.itemgetter('userId'))
    members=[dict['realName'] for dict in data]
    duplicate_names=[]
    for member in set(members):
        if members.count(member)>1:
            duplicate_names.append(member)
    members={}
    for dict in data:
        member_name=dict['nickname'] if dict['realName'] in duplicate_names else dict['realName']
        members[member_name]=dict['userId']
    f=open('member_id.json','w')
    f.write(json.dumps(members,indent=2,ensure_ascii=False))
    f.write('\n')
    f.close()

if __name__=='__main__':
    main()

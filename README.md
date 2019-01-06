基于Python的PocketPC

# Requirements
- [Python](https://www.python.org/downloads/) 3.6.0 or later
```
pip install -U -r requirements.txt
```
- [FFmpeg](https://ffmpeg.org/download.html)
- [Node.js](https://nodejs.org/en/download/current/)
- [PhantomJS](https://phantomjs.org/download.html)
- [You-Get](https://pypi.org/project/you-get/)
- [youtube-dl](https://pypi.org/project/youtube_dl/)

# Usage
## Contents
- [douyin.py](#douyinpy)
- [member_id.py](#member_idpy)
- [migu.py](#migupy)
- [modian.py](#modianpy)
- [pocket.py](#pocketpy)
- [pubed_time.py](#pubed_timepy)
- [recorder.py](#recorderpy)
  - [How it works](#how-it-works)
  - [Usage for recorder.py](#usage-for-recorderpy)
  - [Known bugs](#known-bugs)
  - [Solutions](#solutions)
- [stage.py](#stagepy)

## douyin.py
查询单个抖音账号中所有视频的信息。

```
positional arguments:
  member                      要查询的成员，有效值为指定的配置文件中存在的key。

optional arguments:
  -c CONFIG, --config CONFIG  要读取的配置文件（YAML格式），默认值为同目录下的 douyin.yml 文件。
  -q, --quiet                 只输出主要信息。
  -n, --sum                   只输出实际查询到的数量的值。
  -N, --no-sum                不输出实际查询到的数量，即实际的输出为标准JSON格式。
```

配置文件模板：
```yml
邱欣怡: 57476731686
许佳琪: 57825100366
孙芮: 58050466587
赵韩倩: 58179134820
徐晨辰: 58423660275
冯晓菲: 60304324993
蒋芸: 60912589230
吴哲晗: 61360812916
戴萌: 61363027939
李宇琪: 62383502337
潘燕琦: 62792536161
孔肖吟: 75478657854
徐伊人: 81404951604
赵晔: 85714074050
成珏: 93201175230
张语格: 93454322158
袁雨桢: 94405513146
钱蓓婷: 94481054620
陈观慧: 95594516797
袁丹妮: 95917037675
陈思: 96028160417
徐子轩: 96293082639
莫寒: 96585259273
刘增艳: 97575976658
吕一: 97775160809
```

抖音签名算法来源：<https://github.com/loadchange/amemv-crawler/blob/master/fuck-byted-acrawler.js>

配置文件模板UID来源：<https://github.com/yzlin499/DouYinQuery/blob/master/src/config/memberList.properties>

## member_id.py
更新`member_id.json`的脚本。`member_id.json`是一个存储从成员姓名到成员口袋直播间ID的映射关系的JSON文件。

执行时无需传入任何参数。一般情况下，没有任何输出则表示更新成功。

## migu.py
查询咪咕直播回放M3U8地址。

```
positional arguments:
  id  要查询的回放ID。
```

以`https://tv.miguvideo.com/#/video/tv/550010583120181027002`为例，`id`为`550010583120181027002`。

**本脚本的输出可直接作为[caterpillar](https://pypi.org/project/caterpillar-hls/)的输入。**

## modian.py
查询指定摩点账号中正在众筹的项目。

```
optional arguments:
  -c CONFIG, --config CONFIG  要读取的配置文件（YAML格式），默认值为同目录下的 modian.yml 文件。
  -m MEMBER, --member MEMBER  要查询的成员，有效值为指定的配置文件中存在的key。不传入该参数则为查询所有成员。
  -j JOBS, --jobs JOBS        预设的向 mapi.modian.com 发送POST请求时的并发执行数（实际并发执行数为要查询的账号数量与该参数的较小值），默认值为16。
  -q, --quiet                 只输出主要信息。
  -n, --sum                   只输出实际查询到的数量的值。
  -N, --no-sum                不输出实际查询到的数量，即实际的输出为标准JSON格式。
```

配置文件模板：
```yml
孔肖吟: 986515
邵雪聪: 987799
陈思: 988407
莫寒: 990040
戴萌: 991407
许佳琪: 1067442
吴哲晗: 1073349
邱欣怡: 1078296
温晶婕: 1078429
徐晨辰: 1079154
钱蓓婷: 1081356
吕一: 1082202
孙芮: 1086367
赵晔: 1093167
袁雨桢: 1095343
徐子轩: 1105967
袁丹妮: 1156063
张语格: 1157969
冯晓菲: 1170704
刘增艳: 1171801
李宇琪: 1186273
徐伊人: 1189199
蒋芸: 1452058
陈观慧: 1485197
潘燕琦: 1535074
成珏: 1604111
```

来源：<https://github.com/TeamSII/Notes-for-Media-Team/blob/master/TeamSII%E5%90%84yyh%E6%91%A9%E7%82%B9%E8%B4%A6%E5%8F%B7UID%E7%BB%9F%E8%AE%A1.csv>

## pocket.py
查询成员口袋直播和录播的信息。

```
optional arguments:
  -r, --review                         查询录播信息（简称录播模式），不传入该参数则为查询直播信息（简称直播模式）。
  -t LAST_TIME, --last-time LAST_TIME  要查询的录播的截止时刻，格式为精确到毫秒的UNIX Timestamp（默认值为0，定义为当前时刻）。该参数在直播模式下无效。
  -g GROUP, --group GROUP              要查询的团，有效值为0，10，11，12，13，14（0为整个Group，10为SNH48，11为BEJ48，12为GNZ48，13为SHY48，14为CKG48），默认值为0。该参数在直播模式下无效。
  -m MEMBER, --member MEMBER           要查询的成员，有效值为 member_id.json 中存在的key。该参数在直播模式下无效。
  -l LIMIT, --limit LIMIT              满足其它所有条件的前提下要查询的录播数量（0表示最大数量），默认值为20。该参数在直播模式下无效。
  -T TYPE, --type TYPE                 要查询的类型，有效值为1，2（1为直播间，2为电台）。
  -f FORMAT, --format FORMAT           要查询的录播文件类型，有效值为mp4，m3u8。在直播模式下传入该参数会得到无意义的结果。
  -M MEMBERS, --members MEMBERS        要查询的队，有效值为SII，NII，HII，X，Ft，B，E，J，G，NIII，Z，SIII，HIII，C，K（包括暂休成员，不包括预备生）。传入该参数时同时传入 -g 或 -m 会得到无意义的结果。
  -d [DATE], --date [DATE]             以特定日期为查询条件，格式为 yyyy-mm-dd 。传入该参数时同时传入的 -t 或 -l 会无效。
                                       年与今年相同时可只传入 -d mm-dd 。
                                       年月与今年今月相同时可只传入 -d dd 。
                                       年月日与今年今月今日相同时可只传入 -d 。
  -q, --quiet                          只输出主要信息。
  -n, --sum                            只输出实际查询到的数量的值。
  -N, --no-sum                         不输出实际查询到的数量，即实际的输出为标准JSON格式。
```

## pubed_time.py
查询单个抖音视频的发布时间。

```
positional arguments:
  url  抖音视频URL，有效值为 douyin.py 的输出中 play_addr 的值。
```

## recorder.py
“不间断”录制视频直播流。

核心代码来源：<https://github.com/zmwangx/caterpillar/blob/master/src/caterpillar/merge.py#L43-L114>

### How it works
本脚本在下列情况发生时会重新调用FFmpeg：
- **被动中止**：FFmpeg由于各种原因而自行停止运行。
- **主动中止**：本脚本在下列情况发生时会终止当前FFmpeg进程：
  - 匹配到FFmpeg的输出包含下列内容之一时：
    - `Non-monotonous DTS in output stream \d+:\d+`
    - `DTS \d+ [\<\>] \d+ out of order`
    - `DTS \d+\, next:\d+ st:1 invalid dropping`
    - `missing picture in access unit with size \d+`
  - 检测到当前实际FPS值比当前视频流的理论FPS值低时。
- **用户中止**：用户在录制过程中自行按`q`手动中止当前FFmpeg进程。

### Usage for recorder.py
```
positional arguments:
  arguments                                   执行本脚本必需的参数。

optional arguments:
  --debug                                     调试模式，只输出FFmpeg要连接的远程主机的详细信息。
  -q, --quiet                                 静默模式，只输出脚本开始执行以来的总拉流大小。
  -k, --ignore-errors                         停用上文所述“主动中止”策略。
  --log                                       将FFmpeg的输出同时输出到与输出的视频文件同名的log文件中（仅在不传入 -r 或 -t 时有效）。
  -of OFFI_FORMAT, --offi-format OFFI_FORMAT  指定官网的拉流格式，有效值为flv，rtmp，默认值为flv。该参数在其它平台下无效。
  -bs BILI_STREAM, --bili-stream BILI_STREAM  指定Bilibili的直播线路，有效值为0，1，2，3（0为主线，1为备线1，2为备线2，3为备线3），默认值为0。该参数在其它平台下无效。
  -ua USER_AGENT, --user-agent USER_AGENT     手动指定FFmpeg的User-Agent。
  -f FORMAT, --format FORMAT                  输出文件的封装格式，有效值为ts，flv（仅在不传入 -r 或 -t 时有效），默认值为ts。
  -r REMOTE, --remote REMOTE                  转发模式，有效值为一个合法的RTMP地址。在转发模式下，直播流会被转发到指定的RTMP地址。
  -t, --test                                  测试模式。在测试模式下，直播流会被丢弃到设备黑洞中，同时传入的 -r 也会无效。
  -c, --convert                               结束录制后将录制期间生成的所有输出文件重新封装为mp4文件（仅在不传入 -r 或 -t 时有效）。
```

**在录制过程中按`q`可手动中止当前FFmpeg进程，按`Ctrl + C`即结束录制。**

`arguments`的有效值为下列情形之一：
- `platform` `room_id`两个参数，中间用英文逗号隔开。`platform`的有效值为48live，bilibili，douyu，youtube，yizhibo，miguvideo，netease，1，2，3，4，5，6，7（平台名称和数字一一等价）。`room_id`的有效值为snh，bej，gnz，shy，ckg或各平台的直播间ID。
  - `https://live.bilibili.com/48`的`room_id`为`48`。
  - `https://www.douyu.com/56229`的`room_id`为`56229`。
  - `https://www.youtube.com/channel/UClwRU9iNX7UbzyuVzvZTSkA/live`的`room_id`为`UClwRU9iNX7UbzyuVzvZTSkA`。
  - `https://www.yizhibo.com/member/personel/user_info?memberid=6009826`的`room_id`为`6009826`。
  - `https://tv.miguvideo.com/#/video/tv/550010583120181027002`的`room_id`为`550010583120181027002`。
  - `https://live.ent.163.com/17400180`的`room_id`为`17400180`。
- 一个合法的 RTMP，HLS 或 HTTP-FLV 地址。

### Known bugs
- Windows平台下，如果FFmpeg是通过Chocolatey安装的，那么`subprocess.Popen().terminate()`方法无法终止真正的FFmpeg进程，导致形成僵尸进程。

### Solutions
- 在Chocolatey设置的PATH（如`C:\ProgramData\chocolatey\bin`)下将`ffmpeg.exe`随意更名，并找到存储真正的FFmpeg二进制文件的位置（如`C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin`），将`ffmpeg.exe`复制到之前的PATH。

## stage.py
查询公演录播M3U8地址。

```
positional arguments:
  group_name  要查询的团，有效值为snh48，bej48，gnz48，shy48，ckg48。
  id          要查询的录播ID。
```

以`http://live.bej48.com/Index/invedio/id/1`为例，`group_name`为`bej48`，`id`为`1`。

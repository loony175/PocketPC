基于Python的PocketPC

# Requirement
```
pip install -U -r requirements.txt
```

# Usage
## member_id.py
更新`member_id.json`的脚本。`member_id.json`是一个存储从成员姓名到成员口袋直播间ID的映射关系的JSON文件。

执行时无需传入任何参数。一般情况下，没有任何输出则表示更新成功。

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

## recorder.py
录制公演直播流。

```
positional arguments:
  platform                    直播平台，有效值为48live，bilibili，douyu，youtube，1，2，3，4（名称和数字一一等价）。
  group_name                  直播团体，有效值为snh48，bej48，gnz48，shy48，ckg48，1，2，3，4，5（名称和数字一一等价）。

optional arguments:
  -r REMOTE, --remote REMOTE  转发模式，有效值为一个合法的RTMP地址。在转发模式下，直播流会被转发到指定的RTMP地址。
  -t, --test                  测试模式。在测试模式下，直播流会被丢弃到设备黑洞中，同时传入的 -r 也会无效。
  -c, --convert               结束录制后将录制期间生成的所有ts文件重新封装为mp4文件。
```

在录制过程中按`Ctrl + C`即结束录制。

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

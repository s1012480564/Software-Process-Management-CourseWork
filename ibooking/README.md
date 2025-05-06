# run

python main.py



# 关于 user 鉴权

前端写了管理员和普通用户权限，后端懒得写了。姑且正常访问是区分了权限。
API调用没鉴权，但是懒得写了，就这样了



# 关于 studyroom 和 seat

设计的是，自习室视作矩阵，座位由行列数决定，创建自习室时自动创建全部座位。
自动创建时，座位名称规则我按 "R{row}C{column}" 进行填充

studyroom 和 seat 一对多外键关系。
这里设计的规则是，删除时 CASCADE，级联删除对应 studyroom 下的所有 seat

至于如果修改了 studyroom 的行数列数怎么办，我支持修改，但是没有处理相应的座位逻辑问题。
或许不支持修改也是合理的，管理员直接删除studyroom重建就行了。这个就这样放在这放着，不管了



# 关于 booking 

booking_yyyymmdd 是日分表。见自习室预订系统数据字典.xlsx

每日 0 点更新的 cron 定时任务，让 GPT 搞一下就行了

每日 0 点更新，还要更新 seat 表，status 全部更新为 1 未占用

然后现在实际的处理，偷了个懒，数据库和后端就随便弄了一个 booking 表弄一下

然后 booking 是 user - seat 多对多的联系集。和这两个表的外键关系，删除规则也设计的 CASCADE

关于预约时间，按项目要求文档，只能整点小时为单位预约。
为方便用户直观理解，设计为 xx:00 到 yy:00 预约，于是特别地，有一个特殊的结束时间 23:59

关于抢位，这里设计的做法就是以 post 的系统当前时间作为开始时间，结束时间用户指定

关于签到，需求文档是扫座位现场二维码，这里就只简单弄了个 button 模拟了下

预约各种时间冲突问题之类的就不说了，这些比较关键的问题，也没有什么歧义，也不需要在这里特殊说明的问题，都有好好处理的



# 关于定时任务调度与推送

总的来说，其他那些细节基本都是小问题。本项目的核心问题还是定时任务调度与推送

这里我使用的 Python 的 APScheduler 定时任务调度，以及 SSE (Server-Sent Events) 推送（因为只需要单向推送，就不用 websocket 了）

对于签到功能、booking 和 seat 的状态维护，都进行了实现

然后 scheduler 的选用，由于 background 的需求以及适配 fastapi（基于asyncio），选用 AsyncioScheduler

jobstore 简单选用默认的 MemoryJobStore，而不是 SQLAlchemyJobStore。非持久化，每次重启服务，jobs丢失

executors 简单选用默认的 ThreadPoolExecutor



# 其他

管理员用户名密码随意，自行在数据库添加。
懒得写，没弄管理员注册，也没有密码修改功能。
注册密码也是随意，懒得写安全强度检查

代码量：后端 1266 行；前端 2304 行


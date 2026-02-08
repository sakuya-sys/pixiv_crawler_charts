# pixiv_crawler_charts
爬取p站每日榜单的简易爬虫

![PixPin_2026-02-08_14-44-55](https://github.com/user-attachments/assets/ad43dd6d-e0c3-4c30-bc0c-46ef10add43a)

# cookei设置
<img width="375" height="126" alt="image" src="https://github.com/user-attachments/assets/8f9aac0c-e7f3-4301-a16e-2139295e6d07" />

要想爬取r18榜单的图片 需要设置cookie模拟登录

<img width="1898" height="711" alt="image" src="https://github.com/user-attachments/assets/d19bf7f9-d3e1-4940-ba73-1a61dccb76a5" />

访问p站 按下f12
点击网络 可以看到数据包信息 其中的cookie字段就是我们需要的
将cookise放入py脚本中即可正常爬取r18榜单

<img width="941" height="361" alt="image" src="https://github.com/user-attachments/assets/4a713a9c-0165-40a6-b0b2-b41dd57aef00" />

# 代理设置
使用前需要先设置好代理 然后才能正常爬取
py脚本中默认设置代理地址为

<img width="482" height="99" alt="image" src="https://github.com/user-attachments/assets/ff6ff8d4-f6e1-4bc6-9048-1eb69849ba53" />

# 每日榜单
该脚本有二中模式
第一种模式为默认模式 会爬取当天排行榜的前50张图片

第二种模式为指定类型然后爬取榜单图片

可以选择正常的每日榜单图片 也可以选择r18的每日榜单图片

该模式下还会指定日期与页码 一页就是50张图片

如果提示url错误 大概率是访问url并没有回显json数据 需要检查一下你的url是否写错了

**注意**:选择日期的时候 最多只能指定日期为当天日期的前一天 因为p站每日榜单就是统计昨天的排行榜图片


# movie-douban-crawl
![License](https://img.shields.io/badge/license-MIT-yellow)
![Language](https://img.shields.io/badge/language-python-brightgreen)
## 简介

- 使用了bs4 中 BeautifulSoup，逻辑结构使用pandas和re

## 功能描述

- 功能1：能够爬取到https://movie.douban.com/top250该网址的电影TOP205
- 功能2: 获取到电影的所有信息
- - 电影名（包括港/澳），主演，导演，上映时间，国家，类型
- 功能3：爬取到的信息存到了Execl中表格内，方便查看

### V0.1.2功能

- 功能4：文件存在则不爬取，并读取已存在文件的内容
- - 文件不存在则爬取网页数据，并保存文件
- 代码优化：将代码整体封装，小部分优化逻辑
## 说明与警告

- 代码由本人全全原创，且爬取的内容以及代码内容不可变卖！
- 代码可进行二次创作（内容相似到60%左右以上依旧必须标注二创与来源）
- 代码的获取逻辑可改，但传播也必须标注来源！


通常情况下，你不需要修改这个文件。因为它已经正常工作！除非网站的HTML结构已经改变！

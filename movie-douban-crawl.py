from bs4 import BeautifulSoup
import pandas
import requests
import re


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
}
url = "https://movie.douban.com/top250"
response = requests.get(url, timeout=30, headers=headers)
print(response.url)
print(response.status_code)
print(response.headers)
# print(response.text)

# 构建分页数字列表
page_indexs = list(range(0, 250, 25))
print(page_indexs)

def all_htmls():
    htmls = []
    for index in page_indexs:
        url = f"https://movie.douban.com/top250?start={index}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
        }
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            # 如果返回不是200就Exception
            print(res.status_code)
            raise Exception('error')
        htmls.append(res.text)
    return htmls


# 执行爬取
htmls = all_htmls()


def get_single_html(html):
    """
    解析单个 HTML 得到数据
    :return list({'link', 'title', [label]})
    """
    # 初始化变量
    director = ""
    actor = ""
    year = ""
    country = ""
    genre = ""


    soup = BeautifulSoup(html, 'html.parser')
    article_items = (
        soup.find('div', class_='article')
            .find('ol', class_='grid_view')
            .find_all('div', class_='item')
    )
    datas = []
    for article_item in article_items:
        link = article_item.find('a')['href']
        rank = article_item.find('div', class_='pic').find('em').get_text()
        # info就是整个电影信息，需要解析提取，这样的还有250个
        info = article_item.find('div', class_='info')

        title_elements = article_item.find_all('span', class_='title')
        other_title = article_item.find('span', class_='other').get_text(strip=True).lstrip(' / ')

        # 提取电影名和原名
        title = [title.get_text(strip=True) for title in title_elements]
        main_title = title[0] if len(title) > 0 else ""
        original_title = title[1] if len(title) > 1 else ""
        # 使用正则表达式处理其他标题，确保不误拆分带有 (港/台) 的部分
        other_title_match = re.search(r'\((港/台)\)', other_title)
        if other_title_match:
            other_title = other_title_match.group(0).strip()
        else:
            other_title = other_title
        # 提取评分与级别都在class=star下
        stars = (
            info.find('div', class_='bd')
                .find('div', class_='star')
                .find_all('span')
        )
        rating_star = stars[0]['class'][0]
        rating_num = stars[1].get_text()
        comments = stars[3].get_text()

        """
        提取导演主演等其他信息
        """
        # 提取导演和主演信息
        info_text = info.find('p').get_text(strip=True)
        # 使用正则表达式提取信息
        director_pattern = re.compile(r'导演:(.*?)\s+主演:(.*?)(\d{4}.*)')
        match = director_pattern.match(info_text)
        print("这里是match", match)
        if match:
            director = match.group(1).strip()
            actor = match.group(2).strip()
            # 提取上映年份、国家和类型信息
            ycg = match.group(3).strip()
            # print("这是ycg",ycg)
            # 替换特殊空格字符并正确分割
            ycg = re.sub(r'\xa0', ' ', ycg)
            split_ycg = re.split(r'\s*/\s*', ycg)
            # print("这是split_ycg", split_ycg)
            if len(split_ycg) > 0:
                year = split_ycg[0].strip()
            if len(split_ycg) > 1:
                country = split_ycg[1].strip()
            if len(split_ycg) > 2:
                genre = ' '.join(split_ycg[2:]).strip()

        # 把所有提取的电影信息append
        datas.append({
            '排名': rank,
            '电影名': main_title,
            '电影名(原)': original_title,
            '电影名(其他)': other_title,
            '评分星级': rating_star.replace('rating', '').replace('-t', ''),
            '评分': rating_num,
            '评分人数': comments.replace('人评价', ''),
            '导演':   director,
            '主演': actor,
            '上映时间': year,
            '国家': country,
            '类型': genre,
            '电影链接': link
        })

    return datas

# 执行所有的 HTML 页面解析，得到数据
all_datas = []
for html in htmls:
    all_datas.extend(get_single_html(html))
for data in all_datas:
    print(data)

df = pandas.DataFrame(all_datas)
print(df)

df.to_excel('豆瓣电影TOP250.xlsx')


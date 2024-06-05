import os
import re
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pyecharts.charts import Pie, Bar, Grid
from pyecharts import options as opts


def req_html(url):
    res = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    })
    if res.status_code == 200:
        return res.text
    else:
        print(res.status_code)
        sys.exit(1)

def read_inner(url):
    html_text = req_html(url)
    bs4_html = BeautifulSoup(html_text, 'lxml')
    info = bs4_html.find_all('div', attrs={'id': 'info'})[0].getText()
    actors = re.findall(r'主演:\s*(\D+)\s*类型', info)[0].replace("\xa0", "") if len(
        re.findall(r'主演:\s*(\D+)\s*类型', info)) != 0 else "无"
    directors = re.findall(r'导演:\s*(\D+)\s*编剧', info)[0].replace("\xa0", "") if len(
        re.findall(r'导演:\s*(\D+)\s*编剧', info)) != 0 else "无"
    return actors, directors

def read_req(html_text):
    bs4_html = BeautifulSoup(html_text, 'lxml')
    movies = bs4_html.find_all('div', class_="item")
    data = []
    for movie in movies:
        search_link = movie.find('a').get("href")
        print(search_link)
        titles = movie.find_all('span', class_="title")
        title_Chinese = titles[0].getText()
        print(title_Chinese)
        title_Original = titles[1].getText().replace('/', '').strip() if len(titles) > 1 else None
        title_other = movie.find('span', class_="other").getText().replace('\xa0', '')
        title_HK = re.findall(r"/(.*)\(港\)", title_other)[0] if len(
            re.findall(r"/(.*)\(港\)", title_other)) >= 1 else '无'
        title_HK = title_HK.split('/')[1].replace(" ", "") if '/' in title_HK else title_HK
        title_TW = re.findall(r"/?(.*)\(台\)", title_other)[0] if len(
            re.findall(r"/(.*)\(台\)", title_other)) >= 1 else '无'
        title_TW = title_TW.split('/')[1].replace(" ", "") if '/' in title_TW else title_TW
        title_other_name = '无'
        if title_HK == '无' and title_TW == '无':
            title_other_split = re.split(r'\s*/\s*(?![^(]*\))', title_other)
            if not ('港' in title_other_split[-1] or '台' in title_other_split[-1]):
                title_other_name = title_other_split[-1] if title_other_split else '无'
        info = movie.find('div', class_='bd').getText()
        country = re.findall(r"\d{4}\s*/\s*([^/]+)\s*/", info)[0].replace('\xa0', '') if len(
            re.findall(r"\d{4}\s*/\s*([^/]+)\s*/", info)) != 0 else '无'
        year = re.findall(r"(\d{4})", info)[0]
        type = re.findall(r"/\s*([^/]+)\s*$", info)[0].replace('\n', '')
        type = re.findall(r'^(.*?)\d', type)[0].rstrip()
        grade = re.findall(r'\d+', movie.find('div', class_="star").find('span').get('class')[0])[0]
        grade = eval(grade) / 10 if len(grade) > 1 else eval(grade)
        rate = movie.find('div', class_="star").find('span', class_="rating_num").getText()
        comment_text = movie.find_all('p', class_="quote")
        comment = comment_text[0].getText().replace('\n', '') if len(comment_text) != 0 else '无'
        # directors = re.findall(r'导演:\s*(\D+)\s*编剧', info)[0].replace("\xa0", "") if len(re.findall(r'导演:\s*(\D+)\s*编剧', info)) != 0 else "无"
        actors, directors = read_inner(search_link)
        data.append(
            [title_Chinese, title_Original, title_HK, title_TW, directors, actors, year, country, type, grade, rate,
             comment, search_link, title_other_name])
    cols = ['影片名', '原版片名', '影片名（港）', '影片名（台）', '导演', '主演', '上映日期', '国家', '影片类型', '星级',
            '评分', '评价', '影片链接', '其他']
    new_df = pd.DataFrame(data, columns=cols)
    return new_df

def analyze_all_countries(data):
    # 统计各国出现的总次数
    countries_list = data['国家'].str.split().explode("国家").value_counts().reset_index().values.tolist()
    # 生成各国出现次数的饼图
    pie = Pie()
    pie.add("", countries_list, radius=['10%', '50%'],
            center=['60%', '40%'], label_opts=opts.LabelOpts(is_show=True))
    pie.set_series_opts(
        label_opts=opts.LabelOpts(is_show=True, formatter="{b}:{d}%")
    )
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title='各国出现次数占比'),
        legend_opts=opts.LegendOpts(
            orient='vertical',
            pos_top="5%",
            pos_left="90%",  # 调整图例位置到右侧
            type_='scroll',
            align='left'
        ),
        datazoom_opts=opts.DataZoomOpts()
    )
    pie.render("analyze_all_countries_pie.html")

def analyze_countries_by_types(data):
    df_expanded = data.set_index(['影片名', '国家'])['影片类型'].str.split(' ', expand=True).stack().reset_index(level=2,
                                                                                                               drop=True).reset_index()
    df_expanded.columns = ['影片名', '国家', '影片类型']
    # 再次拆分国家，展开成独立的行
    df_expanded = df_expanded.set_index(['影片名', '影片类型'])['国家'].str.split(' ', expand=True).stack().reset_index(
        level=2, drop=True).reset_index()
    df_expanded.columns = ['影片名', '影片类型', '国家']

    # 统计每个国家在每种类型中的电影数量
    type_counts = df_expanded.groupby(['国家', '影片类型']).size().unstack().fillna(0)

    # 绘制柱状堆叠图
    bar = Bar()

    for country in type_counts.index:
        bar.add_yaxis(country, type_counts.loc[country].tolist())

    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="各国的不同类型电影个数"),
        xaxis_opts=opts.AxisOpts(type_="category", name="影片类型"),
        yaxis_opts=opts.AxisOpts(name="数量"),
        legend_opts=opts.LegendOpts(
            orient='vertical',
            pos_top="5%",
            pos_left="90%",  # 调整图例位置到右侧
            type_='scroll',
            align='left'
        ),
        datazoom_opts=opts.DataZoomOpts()
    )

    bar.set_series_opts(
        label_opts=opts.LabelOpts(is_show=False),
        stack="总量"
    )

    bar.add_xaxis(type_counts.columns.tolist())
    grid = Grid(init_opts=opts.InitOpts(width="1000px", height="600px"))
    grid.add(bar, grid_opts=opts.GridOpts(pos_left="5%", pos_right="20%", pos_bottom="20%"))
    grid.render("analyze_countries_by_types_bar.html")

def analyze_types_by_countries(data):
    # 拆分类型，并展开成独立的行
    df_expanded = data.set_index(['影片名', '国家'])['影片类型'].str.split(' ', expand=True).stack().reset_index(level=2, drop=True).reset_index()
    df_expanded.columns = ['影片名', '国家', '影片类型']
    # 再次拆分国家，展开成独立的行
    df_expanded = df_expanded.set_index(['影片名', '影片类型'])['国家'].str.split(' ', expand=True).stack().reset_index(
        level=2, drop=True).reset_index()
    df_expanded.columns = ['影片名', '影片类型', '国家']
    # 统计每个国家在每种类型中的电影数量
    type_counts = df_expanded.groupby(['国家', '影片类型']).size().unstack().fillna(0)
    # 将数据转换为按类型分组
    country_counts = type_counts.T

    # 绘制柱状堆叠图
    bar = Bar()
    for film_type in country_counts.index:
        bar.add_yaxis(film_type, country_counts.loc[film_type].tolist())
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="各国的不同类型电影个数"),
        xaxis_opts=opts.AxisOpts(type_="category", name="国家", axislabel_opts={"rotate": 45}),
        yaxis_opts=opts.AxisOpts(name="数量"),
        legend_opts=opts.LegendOpts(
            orient='vertical',
            pos_top="5%",
            pos_left="90%",  # 调整图例位置到右侧
            type_='scroll',
            align='left',
        ),
        datazoom_opts = opts.DataZoomOpts()
    )
    bar.set_series_opts(
        label_opts=opts.LabelOpts(is_show=False),
        stack="总量"
    )

    bar.add_xaxis(country_counts.columns.tolist())

    grid = Grid(init_opts=opts.InitOpts(width="1000px", height="600px"))
    grid.add(bar, grid_opts=opts.GridOpts(pos_left="5%", pos_right="20%", pos_bottom="20%"))
    grid.render("analyze_types_by_countries_bar.html")

if __name__ == "__main__":
    path = os.path.join(os.getcwd(), "response.xlsx")
    if os.path.exists(path):
        df = pd.read_excel("./response.xlsx", sheet_name="top250")
        analyze_all_countries(df)
        analyze_types_by_countries(df)
        analyze_countries_by_types(df)
    else:
        df = pd.DataFrame()
        index_val = 0
        if not os.path.exists("response.xlsx"):
            pd.DataFrame([]).to_excel("response.xlsx", index=False, header=False)
        for i in range(0, 226, 25):
            text = req_html(f"https://movie.douban.com/top250?start={i}&filter=")
            new_df = read_req(text)
            df = pd.concat([df, new_df])
            index_val += 1
            with pd.ExcelWriter("response.xlsx", engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                new_df.to_excel(writer, sheet_name=str(index_val), index=False)
                df.to_excel(writer, index=False, sheet_name="top250")

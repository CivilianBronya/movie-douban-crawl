import pandas as pd
import os
from pyecharts.charts import Pie, Bar, Line
from pyecharts import options as opts
from pyecharts.globals import ThemeType, SymbolType
import jieba

from PIL import Image

import numpy as np
from wordcloud import WordCloud, ImageColorGenerator



file_path = os.path.join(os.getcwd(), r'Excel/response.xlsx')
df_excel = pd.read_excel('Excel/response.xlsx')
print(df_excel)


# 创建 DataFrame
df = pd.DataFrame(df_excel)
def data_analysis(df):
    """
       统计每个国家的电影数量
       """
    countries_list = df['国家'].str.split().explode()
    countries_counts = countries_list.value_counts().reset_index().values.tolist()
    return countries_counts


def pie_data_chart(list):
    pie = Pie()
    # 添加数据到饼图中
    pie.add(
        series_name="国家数量",
        radius=["30%", "75%"],  # 设置内外半径，实现环形饼图效果
        data_pair=list
    )

    # 添加总和标签
    pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}个\n占比：{d}%"))
    # 设置标题和标签
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title="每个国家电电影数量"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_top="middle", pos_right="-3%")
    )
    # 渲染图表为 HTML 文件
    pie.render('data/country_movie_counts.html')


def create_stacked_bar_chart(df):
    """
    创建堆叠柱状图并保存为HTML文件
    """

    # 创建国家和影片类型的组合统计
    type_country = df[['影片类型', '国家']].copy()
    type_country['影片类型'] = type_country['影片类型'].str.split()
    type_country = type_country.explode('影片类型')
    type_country['国家'] = type_country['国家'].str.split()
    type_country = type_country.explode('国家')
    print(type_country,"查看")
    type_country_counts = type_country.groupby(['国家', '影片类型']).size().unstack(fill_value=0)
    print(type_country_counts)
    # 创建堆叠柱状图
    bar = Bar(init_opts=opts.InitOpts(
        width="100%",
        height="600px",
        theme=ThemeType.LIGHT))

    bar.add_xaxis(type_country_counts.index.tolist())

    for film_type in type_country_counts.columns:
        bar.add_yaxis(film_type, type_country_counts[film_type].tolist(), stack="stack1")

    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="各国家各影片类型电影数量分布",
                                  title_textstyle_opts=opts.TextStyleOpts(font_size=20)),

        xaxis_opts=opts.AxisOpts(
            type_="category",
            name="影片类型",
            axislabel_opts=opts.LabelOpts(rotate=45, font_size=12),
            name_textstyle_opts=opts.TextStyleOpts(font_size=16)
        ),

        yaxis_opts=opts.AxisOpts(name="电影数量", name_textstyle_opts=opts.TextStyleOpts(font_size=16)),
        legend_opts=opts.LegendOpts(
            orient="vertical",
            pos_top="middle",
            pos_right="0%",
            type_="scroll",
            textstyle_opts=opts.TextStyleOpts(font_size=12),
            item_gap=10
        ),
        toolbox_opts=opts.ToolboxOpts(is_show=True),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
        datazoom_opts=opts.DataZoomOpts()
    )

    bar.set_series_opts(
        label_opts=opts.LabelOpts(is_show=False),
        markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max", name="最大值")])
    )

    bar.render("data/country_category_counts.html")


def create_line_chart(df):
    # 创建国家和影片类型的组合统计
    type_time = df[['上映日期', '国家']].copy()
    type_time = type_time.explode('上映日期')
    type_time['国家'] = type_time['国家'].str.split()
    type_time= type_time.explode('国家')
    print(type_time, "查看")
    type_time_counts = type_time.groupby(['国家','上映日期']).size().unstack(fill_value=0)
    # .T也可以，但没必要
    print(type_time_counts)

    # 创建Line对象
    line = Line(init_opts=opts.InitOpts(
        width="100%",
        height="600px",
        theme=ThemeType.LIGHT))

    line.add_xaxis(type_time_counts.columns.tolist())
    # print(type(type_time_counts.index))

    for country in type_time_counts.index:
        line.add_yaxis(country, type_time_counts.loc[country].tolist(), stack="stack1", is_smooth=True)

    line.set_global_opts(
        title_opts=opts.TitleOpts(title="各国家各影片类型电影数量分布",
                                  title_textstyle_opts=opts.TextStyleOpts(font_size=20)),

        xaxis_opts=opts.AxisOpts(
            type_="category",
            name="年份",
            axislabel_opts=opts.LabelOpts(rotate=45, font_size=12),
            name_textstyle_opts=opts.TextStyleOpts(font_size=16)
        ),

        yaxis_opts=opts.AxisOpts(name="电影数量", name_textstyle_opts=opts.TextStyleOpts(font_size=16)),
        legend_opts=opts.LegendOpts(
            orient="vertical",          # 垂直布局
            pos_top="middle",           # 设置垂直居中
            pos_right="0%",
            type_="scroll",             # 图例设置为滚动
            textstyle_opts=opts.TextStyleOpts(font_size=12),
            item_gap=10                 # 图例每项之间的间隔距离
        ),
        toolbox_opts=opts.ToolboxOpts(is_show=True),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
        datazoom_opts=opts.DataZoomOpts()

    )

    line.set_series_opts(
        label_opts=opts.LabelOpts(is_show=False),
        markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max", name="最大值")])
    )

    line.render("data/time_category_counts.html")


def word_cloud_chart(df):
    word = df['评价']
    print(type(word), word)

    # 将数据转换为字符串，并合并所有句子
    text = " ".join(word.tolist())
    seglist = jieba.lcut_for_search(text)
    result = ''.join(seglist)
    print(seglist)
    print(result)
    # 使用 jieba 进行分词
    # words = jieba.cut(text)
    # 设置停用词
    stop_words = ['又', '也', '们', '了', '我', '你', '是', '他', '她', '有', '与', '在', '乃', '好', '道']
    im = np.array(Image.open('images/lmm_cucub.jpg'))

    # 创建词云图对象
    wordcloud = WordCloud(
        font_path='C:\Windows\Fonts\STXINGKA.ttf',
        background_color='white',
        mask=im
    )

    # 渲染并显示词云图
    wordcloud.to_file('data/wordcloud.jpg')
def line_A_bar_movie_chart(df):
    df['year'] = df['上映日期']
    min_year = df['year'].min()
    # print(df['year'])
    # 计算每五年的时间段
    df['year_group'] = ((df['year'] - min_year) // 5) * 5 + min_year
    # print(((df['year'] - min_year) // 5) * 5)
    # print(df['year_group'])
    # 统计每个五年段的电影数量
    # year_group_counts = df.groupby('year_group')['year'].count()
    year_group_counts = df['year_group'].value_counts().sort_index()
    print(type(year_group_counts))

    # 评分
    # 计算每个五年段的平均评分
    year_group_means = df.groupby('year_group')['评分'].mean().round(2)

    # 准备数据
    x_data = [f"{year}-{year + 4}" for year in year_group_counts.index]
    y_data_counts = year_group_counts.values.tolist()
    y_data_means = year_group_means.values.tolist()

    # for year in year_group_counts.index:
    #     x_data.append(f"{year}-{year + 4}")
    # y_data = year_group_counts.values.tolist()

    # 计算电影数量的平均值
    # mean_count = sum(y_data_counts) / len(y_data_counts)
    # 计算评分的平均值
    # mean_score = sum(y_data_means) / len(y_data_means)

    """ 
    柱状图内容！！！114514
    """
    # 使用pyecharts绘制柱状图
    bar = (
        Bar()
        .add_xaxis(x_data)
        .add_yaxis("电影数量", y_data_counts)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="每五年电影数量统计与平均评分"),
            xaxis_opts=opts.AxisOpts(axislabel_opts={"rotate": 45}),
            yaxis_opts=opts.AxisOpts(name="电影数量&电影评分",position="left"),
            datazoom_opts=opts.DataZoomOpts(),
        )
        .set_series_opts(
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(type_="average", name="平均数量")]
            ),
            markpoint_opts=opts.MarkPointOpts(
                data=[opts.MarkPointItem(type_="max", name="最大值")]
            ),
        )
    )

    # 渲染图表到本地HTML文件
    # bar.render("data/movies_by_five_years.html")

    """
    折线图内容！！！1919810
    """
    line = (
        Line()
        .add_xaxis(x_data)
        .add_yaxis("电影评分", y_data_means)
        .set_global_opts(
        )
        .set_series_opts(
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(type_="average", name="平均评分")]
            ),
            markpoint_opts=opts.MarkPointOpts(
                data=[opts.MarkPointItem(type_="max", name="最高评分")]
            ),
        )
    )
    all = bar.overlap(bar).overlap(line)
    all.render("data/bar_A_line_chart.html")
    # 统计年数区间内的评分




if __name__ == "__main__":
    # 加载数据
    Pie_chart = pie_data_chart(data_analysis(df))
    Bar_chart = create_stacked_bar_chart(df)
    Line_chart = create_line_chart(df)
    # word_cloud = word_cloud_chart(df)
    line_A_bar_movie_chart(df)

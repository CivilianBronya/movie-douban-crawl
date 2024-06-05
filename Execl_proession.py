import pandas as pd
import os
from pyecharts.charts import Pie, Bar
from pyecharts import options as opts
from pyecharts.globals import ThemeType


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
    # 提取国家和影片类型数据
    countries = df['国家'].str.split().explode()
    film_types = df['影片类型'].str.split().explode()

    # 统计每个国家的电影数量
    country_counts = data_analysis(df)

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
    bar = Bar(init_opts=opts.InitOpts(width="100%", height="600px", theme=ThemeType.LIGHT))
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
            pos_right="-3%",
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


if __name__ == "__main__":
    # 加载数据
    Pie_chart = pie_data_chart(data_analysis(df))
    Bar_chart = create_stacked_bar_chart(df)


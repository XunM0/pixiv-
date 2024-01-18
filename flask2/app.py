import time

from flask import Flask
from jinja2 import Environment,FileSystemLoader
from markupsafe import Markup
from pyecharts.globals import CurrentConfig
import pandas as pd
CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./templates"))
from flask import render_template
from pyecharts import  options as opts
from pyecharts.charts import  Bar,Line,Timeline,WordCloud,EffectScatter
import DAO
app = Flask(__name__)
data = ''
def pre():
    global data
    sql = "select * from test"
    data = DAO.select_data(sql)



def webFlow_base()->Bar:
    result = data.groupby('日期').agg({'浏览': 'sum'}).to_dict()['浏览']
    # result

    c = (
        Line()
        .add_xaxis(list(result.keys()))
        .add_yaxis('浏览量', list(result.values()))
        .set_global_opts(title_opts=opts.TitleOpts(title="网站每日流量变化图")
                         ,datazoom_opts=opts.DataZoomOpts(range_start=10,range_end=30))

    )
    return c
def firstTenWriter_base()->Timeline:
    # 动态展示网站每日排名前十作者
    times = data.日期.unique()

    t1 = Timeline()

    t1.add_schema(
        is_auto_play=True,
        is_loop_play=True,
        play_interval=2000
    )

    for dt in times:
        items = data[data.日期 == dt].groupby('作者').agg({'浏览': 'sum', '评分': 'mean'}).sort_values('评分',
                                                                                                       ascending=False)[
                :10].to_dict()

        bar = (
            Bar()
            .add_xaxis(list(items['浏览'].keys()))
            .add_yaxis('评分', [val for val in items['评分'].values()])
            .add_yaxis('浏览量', [val for val in items['浏览'].values()])
            #         .reversal_axis()
            .set_global_opts(title_opts=opts.TitleOpts(title="pixiv网站每日排名前十作者"))
        )
        t1.add(bar, dt)
    return t1

def writer_base()->Timeline:
    # 动态展示网站作家每日评分变化
    t2 = Timeline()
    t2.add_schema(
        is_auto_play=True,
        is_loop_play=True,
        play_interval=2000
    )

    writers = data.作者.unique()
    for w in writers:
        item = data[data.作者 == w].groupby('日期').agg({'评分': 'mean'}).to_dict()['评分']

        bar = (
            Bar()
            .add_xaxis(list(item.keys()))
            .add_yaxis('评分', [val for val in item.values()])
            .set_global_opts(title_opts=opts.TitleOpts(title="作家 {} 评分变化图".format(w)))
        )

        #     break;
        t2.add(bar, w)
    return t2

def hotWord_base()->WordCloud:
    # 热点标签生成
    label_value = {}

    for i in range(len(data)):
        temp = data['类型'][i].split(',')

        temp = [var.replace('[', '').replace(']', '').replace("'", '') for var in temp]
        for v in temp:
            if v not in label_value.keys():
                label_value[v] = 0
            label_value[v] += data['评分'][i]
    label_value = label_value.items()

    c = (
        WordCloud()
        .add(series_name="热点标签", data_pair=label_value, word_size_range=[6, 66])
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="热点标签", title_textstyle_opts=opts.TextStyleOpts(font_size=23)
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True),
        )
    )
    return c

def effectScatter()->EffectScatter:
    x_data = data.日期.unique()
    y_data = data.groupby('日期').agg({'评分': 'mean'}).to_dict()['评分']

    c = (EffectScatter()
                     .add_xaxis(list(x_data))
                     .add_yaxis('评分', [int(i) for i in list(y_data.values())])
                     .set_global_opts(title_opts=opts.TitleOpts(title="网站每日评分变化图")
                                      , datazoom_opts=opts.DataZoomOpts(range_start=10, range_end=30))
                     )

    return c
@app.route("/webFlow")
def index():
    c = webFlow_base()
    c.render("static/webFlow.html")
    time.sleep(0.5)
    return render_template("webFlow.html")

@app.route("/firstTenWriter")
def index2():
    c = firstTenWriter_base()
    c.render("static/firstTenWriter.html")
    time.sleep(0.5)
    return render_template("firstTenWriter.html")
@app.route("/writer")
def index3():
    c = writer_base()
    c.render("static/writer.html")
    time.sleep(0.5)
    return render_template("writer.html")

@app.route("/hotWord")
def index4():

    c = hotWord_base()
    c.render("static/hotWord.html")
    time.sleep(0.5)
    return render_template("hotword.html")

@app.route("/effectScatter")
def index5():
    print(1)
    c = effectScatter()
    c.render("static/effectScatter.html")
    time.sleep(0.5)
    print(2)
    return render_template("effectScatter.html")

@app.route("/")
def index6():
    return render_template("index.html")


if __name__ == "__main__":
    pre()
    app.run(host='0.0.0.0',port=5000)


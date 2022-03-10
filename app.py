from flask import Flask, render_template, request, jsonify, redirect, url_for
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import requests

app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.xo7xh.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/')
def home():
    matjips = list(db.matjip.find({}, {"_id": False}))
    return render_template('index.html', matjips=matjips)

@app.route('/login')
def login():
    return render_template('loginForm.html')

@app.route('/post')
def post():
    return render_template('post.html')


@app.route('/post', methods=['POST'])
def post_matjip():
    # 맛집 등록하기
    url_link_receive = request.form["url_link_give"]
    store_name_receive = request.form["store_name_give"]
    location_receive = request.form["location_give"]
    description_receive = request.form["description_give"]



    driver = webdriver.Chrome('./chromedriver')
    driver.get(url_link_receive)
    sleep(3)
    element = driver.find_element_by_id("entryIframe")  # iframe 태그 엘리먼트 찾기
    driver.switch_to.frame(element)  # 프레임 이동


    req = driver.page_source
    soup = BeautifulSoup(req, 'html.parser')

    callnums = soup.select("span._3ZA0S")
    addresss = soup.select("span._2yqUQ")
    opentimes = soup.select("span._2WoIY > time")

    sleep(2)
    driver.find_element_by_css_selector("#_autoPlayable").click()

    sleep(2)
    req = driver.page_source
    soup = BeautifulSoup(req, 'html.parser')
    driver.close()

    images = soup.select("._3TiO6._1wsFm ._img")

    for callnum in callnums:
        callnum = callnum.text
    for adress in addresss:
        adress = adress.text
    for opentime in opentimes:
        opentime = opentime.text
    for image in images:
        src = image['src']

        headers = {
            "X-NCP-APIGW-API-KEY-ID": "d2ekfousjn",
            "X-NCP-APIGW-API-KEY": "Dr2VTkWjpX8cwYs9eLrm5hh4vkjYjRCYEXmPxQLX"
        }
        r = requests.get(f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={adress}",
                         headers=headers)
        response = r.json()

        if response["status"] == "OK":
            if len(response["addresses"]) > 0:
                x = float(response["addresses"][0]["x"])
                y = float(response["addresses"][0]["y"])


    matjip_list = list(db.matjip.find({}, {'_id': False}))
    count = len(matjip_list) + 1

    doc = {
        "url_link": url_link_receive,
        "store_name": store_name_receive,
        "location": location_receive,
        "description": description_receive,
        "callnum": callnum,
        "adress": adress,
        "opentime": opentime,
        "src": src,
        "num": count,
        "mapx": x,
        "mapy": y
    }
    db.matjip.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '등록 완료!'})

# @app.route("/matjip", methods=["GET"])
# def get_matgip():
#     matjip_list = list(db.matjip.find({},{"_id": False}))
#     return jsonify({'matjip_list': matjip_list})


@app.route('/detail')
def detail():
    return render_template('detail.html')

@app.route('/detail/<keyword>')
def get_detail(keyword):



    matjip = db.matjip.find_one({'store_name' : keyword})
    print(matjip)
    return render_template("detail.html", matjip=matjip)

@app.route('/detail/<keyword>', methods=['POST'])
def comment_post(keyword):
    comment_receive = request.form['comment_give']

    doc = {"comment": comment_receive,
           "store_name":keyword
           }
    db.comment.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '댓글 저장 완료'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

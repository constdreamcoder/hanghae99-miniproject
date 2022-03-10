from flask import Flask, render_template, request, jsonify, redirect, url_for
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import jwt
import datetime
import hashlib
import certifi
import requests

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.xo7xh.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)

db = client.dbsparta

@app.route('/')
def home():

    matjips = list(db.matjip.find({}, {"_id": False}))
    return render_template('index.html', matjips=matjips)

    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return render_template('index.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('loginForm.html', msg=msg)


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.accounts.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
    }
    db.accounts.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    # 아이디 중복확인
    username_receive = request.form['username_give']
    # 같은 아이다가 데이터베이스에 존재한다면 true, 아니면 false
    exists = bool(db.accounts.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


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

@app.route('/detail')
def detail():
    return render_template('detail.html')


@app.route('/detail/<keyword>')
def get_detail(keyword):
    matjip = db.matjip.find_one({'store_name' : keyword})
    return render_template("detail.html", matjip=matjip)

# 댓글은 추후 업데이트 예정
# @app.route('/detail/<keyword>', methods=['POST'])
# def comment_post(keyword):
#     comment_receive = request.form['comment_give']
#
#     doc = {"comment": comment_receive,
#            "store_name":keyword
#            }
#     db.comment.insert_one(doc)
#     return jsonify({'result': 'success', 'msg': '댓글 저장 완료'})

@app.route('/restaurantslist')
def restaurantslist():
    matjip_list = list(db.matjip.find({}, {'_id': False}))
    d_today = datetime.date.today();
    return render_template('restaurantslist.html', matjiplist=matjip_list, current_time=d_today)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

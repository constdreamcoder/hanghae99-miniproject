from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('loginForm.html')


@app.route('/post')
def post():
    return render_template('post.html')


@app.route('/detail')
def detail():
    return render_template('detail.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

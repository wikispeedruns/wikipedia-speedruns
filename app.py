from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_home():
    return render_template('home.html')

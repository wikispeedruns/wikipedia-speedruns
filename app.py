from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_start():
    return render_template('start.html')

from flask import Flask, render_template

app = Flask(__name__)

#@app.route('/', methods=['GET'])
#def get_home():
#    return render_template('home.html', name='home')

@app.route('/', methods=['GET'])
def get_start():
    return render_template('start.html')#, start='United States', end='Gross domestic product')

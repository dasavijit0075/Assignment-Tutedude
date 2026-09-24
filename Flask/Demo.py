# print("Avijit Developer")

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Welcome to the home page'

@app.route('/details')
def details():
    return 'Welcome to the details page'

if __name__ == '__main__' :
    app.run(debug=True)
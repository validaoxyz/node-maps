import shutil
from flask import Flask, send_from_directory

app = Flask(__name__)

# Copy 'output.csv' from the parent directory to the current directory
shutil.copy('../output.csv', './output.csv')

@app.route('/')
def index():
    return send_from_directory('.', 'map.html')

@app.route('/output.csv')
def output_csv():
    return send_from_directory('.', 'output.csv')

if __name__ == '__main__':
    app.run(port=8080, debug=True)

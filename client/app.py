import os, json
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify(message="Hello, HTTPS world!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)


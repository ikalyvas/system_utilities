
from flask import Flask, jsonify

predictor = Flask(__name__)

@predictor.route('/')
def index():
    return "Hello, World!"



@predictor.route('/predict/api/v1.0/data', methods=['GET'])
def get_tasks():


    return jsonify({'tasks': 2})



if __name__ == '__main__':
    predictor.run(debug=True)
from flask import abort, request, jsonify
from predictor import DiabPred
import numpy as np

from . import app

model = DiabPred()
model.train()


@app.route('/')
def hello():
    return 'Hello world'

@app.route('/predict/<list:data>', methods=['POST','GET'])
def predict(data):

    print data
    print len(data)
    print 'requests are' +  str(request)
   # print 'attributes of requests' + str(dir(request))
    print request.args
    if len(data) == 0:
        abort(404)
    #if not request.json:
    #    abort(400)
    data = np.array([[int(i)] for i in data])
    predict_results = model.predict(np.array(data))
    #if 'title' in request.json and type(request.json['title']) != unicode:
    #    abort(400)
    #if 'description' in request.json and type(request.json['description']) is not unicode:
    #    abort(400)
    #if 'done' in request.json and type(request.json['done']) is not bool:
    #    abort(400)
   # task[0]['title'] = request.json.get('title', task[0]['title'])
   # task[0]['description'] = request.json.get('description', task[0]['description'])
   # task[0]['done'] = request.json.get('done', task[0]['done'])
    print predict_results
    return jsonify({'results': predict_results})
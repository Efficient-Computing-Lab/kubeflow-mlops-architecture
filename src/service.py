import pickle
from flask import Flask, request, jsonify
    
app = Flask(__name__)
    
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
    
    
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    prediction = model.predict([data['features']])
    return jsonify(prediction=prediction.tolist())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
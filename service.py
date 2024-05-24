import os


def get_service_file():
    service_file_content = f"""import pickle
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
    app.run(host='0.0.0.0', port=8080)"""
    return service_file_content

def get_dockerfile(model_file):
    dockerfile_content = f"""
        FROM python:3.9
        COPY {os.path.basename(model_file)} /app/model.pkl
        RUN pip install scikit-learn flask
        COPY src/service.py /app/service.py
        CMD ["python", "/app/service.py"]
        """
    return dockerfile_content
from kfp import dsl, compiler
from kfp.dsl import component, pipeline
import tarfile
import os
import kfp


# Define the prepare_data component
@component(
    packages_to_install=["pandas", "numpy", "scikit-learn"],
    base_image="python:3.9",
)
def prepare_data(output_csv: dsl.Output[dsl.Artifact]):
    import pandas as pd
    import os
    from sklearn import datasets

    # Load dataset
    iris = datasets.load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['species'] = iris.target

    # Save the prepared data to CSV
    df = df.dropna()

    # Ensure the output directory exists
    os.makedirs(output_csv.path, exist_ok=True)

    output_csv_path = os.path.join(output_csv.path, 'final_df.csv')
    df.to_csv(output_csv_path, index=False)


# Define the train_test_split component
@component(
    packages_to_install=["pandas", "numpy", "scikit-learn"],
    base_image="python:3.9",
)
def train_test_split(input_csv: dsl.Input[dsl.Artifact], output_dir: dsl.Output[dsl.Artifact]):
    import pandas as pd
    import numpy as np
    import os
    from sklearn.model_selection import train_test_split

    # Load the prepared data
    final_data = pd.read_csv(os.path.join(input_csv.path, 'final_df.csv'))

    # Split the data into training and testing sets
    target_column = 'species'
    X = final_data.loc[:, final_data.columns != target_column]
    y = final_data.loc[:, final_data.columns == target_column]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=47)

    # Ensure the output directory exists
    os.makedirs(output_dir.path, exist_ok=True)

    # Save the splits to .npy files
    np.save(os.path.join(output_dir.path, 'X_train.npy'), X_train)
    np.save(os.path.join(output_dir.path, 'X_test.npy'), X_test)
    np.save(os.path.join(output_dir.path, 'y_train.npy'), y_train)
    np.save(os.path.join(output_dir.path, 'y_test.npy'), y_test)


# Define the training_basic_classifier component
@component(
    packages_to_install=["pandas", "numpy", "scikit-learn"],
    base_image="python:3.9",
)
def training_basic_classifier(input_dir: dsl.Input[dsl.Artifact], model_output: dsl.Output[dsl.Artifact]):
    import numpy as np
    import os
    from sklearn.linear_model import LogisticRegression
    import pickle

    # Load the training data
    X_train = np.load(os.path.join(input_dir.path, 'X_train.npy'), allow_pickle=True)
    y_train = np.load(os.path.join(input_dir.path, 'y_train.npy'), allow_pickle=True)

    # Train the logistic regression classifier
    classifier = LogisticRegression(max_iter=500)
    classifier.fit(X_train, y_train)

    # Ensure the output directory exists
    os.makedirs(model_output.path, exist_ok=True)
    print(model_output.path)
    # Save the trained model to a pickle file
    model_path = os.path.join(model_output.path, 'model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(classifier, f)


@component(
    packages_to_install=["docker", "requests"],
    base_image="python:3.9",
)
def build_docker_image(model_path: dsl.Input[dsl.Artifact], docker_image: str):
    import os
    import docker
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

    def get_dockerfile(model_file, service_file_path):
        dockerfile_content = f"""
            FROM python:3.9
            COPY {os.path.basename(model_file)} /app/model.pkl
            RUN pip install scikit-learn flask
            COPY {os.path.basename(service_file_path)} /app/service.py
            CMD ["python", "/app/service.py"]
            """
        return dockerfile_content

    # Get the model file path
    model_file = os.path.join(model_path.path, 'model.pkl')

    service_file_content = get_service_file()
    service_file_path = os.path.join(model_path.path, 'service.py')
    with open(service_file_path, 'w') as f:
        f.write(service_file_content)
    # Create a Dockerfile
    dockerfile_content = get_dockerfile(model_file, service_file_path)
    dockerfile_path = os.path.join(model_path.path, 'Dockerfile')
    with open(dockerfile_path, 'w') as f:
        f.write(dockerfile_content)

    # Build the Docker image
    client = docker.DockerClient(base_url="tcp://192.168.1.240:2375")
    image, logs = client.images.build(path=model_path.path, tag=docker_image)
    for log in logs:
        print(log)

    # Push the Docker image to a registry (optional)
    # Replace '<username>' and '<password>' with your Docker registry credentials
    #registry_url = "https://index.docker.io/v1/"
    #client.login(username='<username>', password='<password>', registry=registry_url)
    #client.images.push(docker_image)


# Define the pipeline
@pipeline
def my_pipeline(docker_image: str):
    """My ML pipeline."""
    prepare_data_task = prepare_data()
    train_test_split_task = train_test_split(input_csv=prepare_data_task.outputs['output_csv'])
    training_task = training_basic_classifier(input_dir=train_test_split_task.outputs['output_dir'])
    build_docker_image(
        model_path=training_task.outputs['model_output'],
        docker_image=docker_image,
    )


# Compile the pipeline
compiler.Compiler().compile(my_pipeline, package_path='pipeline.yaml')

# Package the pipeline YAML
with tarfile.open("pipeline.tar.gz", "w:gz") as tar:
    tar.add("pipeline.yaml", arcname=os.path.basename("pipeline.yaml"))

# Upload and run the pipeline
client = kfp.Client(host="http://192.168.1.240:3001")
client.upload_pipeline_version(pipeline_name='test', pipeline_version_name='v21',
                               pipeline_package_path='pipeline.tar.gz')
pipeline_id = client.get_pipeline_id('test')

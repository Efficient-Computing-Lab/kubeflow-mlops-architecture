import json

import requests
from kfp import dsl, compiler
from kfp.dsl import component, pipeline
from kfp import kubernetes
import tarfile
import os
import kfp


# Define the prepare_data component
@component(
    packages_to_install=["pandas", "numpy", "scikit-learn"],
    base_image="python:3.9",
)
def prepare_requi(output_csv: dsl.Output[dsl.Artifact]):
    import pandas as pd
    import os
    from sklearn import datasets
    import subprocess

    # Load dataset
    iris = datasets.load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["species"] = iris.target

    # Save the prepared data to CSV
    df = df.dropna()

    # Ensure the output directory exists
    os.makedirs(output_csv.path, exist_ok=True)

    output_csv_path = os.path.join(output_csv.path, "final_df.csv")
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
    final_data = pd.read_csv(os.path.join(input_csv.path, "final_df.csv"))

    # Split the data into training and testing sets
    target_column = "species"
    X = final_data.loc[:, final_data.columns != target_column]
    y = final_data.loc[:, final_data.columns == target_column]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=47)

    # Ensure the output directory exists
    os.makedirs(output_dir.path, exist_ok=True)

    # Save the splits to .npy files
    np.save(os.path.join(output_dir.path, "X_train.npy"), X_train)
    np.save(os.path.join(output_dir.path, "X_test.npy"), X_test)
    np.save(os.path.join(output_dir.path, "y_train.npy"), y_train)
    np.save(os.path.join(output_dir.path, "y_test.npy"), y_test)


# Define the training_basic_classifier component
@component(
    packages_to_install=["pandas", "numpy", "scikit-learn", "onnx", "skl2onnx"],
    base_image="python:3.9",
)
def training_basic_classifier(input_dir: dsl.Input[dsl.Artifact], model_output: dsl.Output[dsl.Artifact]):
    import numpy as np
    import os
    from sklearn.linear_model import LogisticRegression
    import onnx
    import skl2onnx
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType

    # Load the training data
    X_train = np.load(os.path.join(input_dir.path, "X_train.npy"))
    y_train = np.load(os.path.join(input_dir.path, "y_train.npy"))

    # Train the logistic regression classifier
    classifier = LogisticRegression(max_iter=500)
    classifier.fit(X_train, y_train)

    # Convert the trained model to ONNX format
    initial_type = [('float_input', FloatTensorType([None, X_train.shape[1]]))]
    onnx_model = convert_sklearn(classifier, initial_types=initial_type)

    # Ensure the output directory exists
    os.makedirs(model_output.path, exist_ok=True)
    print(model_output.path)

    # Save the ONNX model to a file
    model_path = os.path.join(model_output.path, "model.v9.onnx")
    with open("/trained_models/model.v9.onnx", "wb") as f:
        f.write(onnx_model.SerializeToString())


# Define the pipeline
@pipeline
def my_pipeline():
    """My ML pipeline."""
    prepare_data_task = prepare_data()
    train_test_split_task = train_test_split(input_csv=prepare_data_task.outputs["output_csv"])
    training_task = training_basic_classifier(input_dir=train_test_split_task.outputs["output_dir"])
    kubernetes.mount_pvc(training_task, pvc_name="trained-models", mount_path="/trained_models")


# Compile the pipeline
compiler.Compiler().compile(my_pipeline, package_path="pipeline.yaml")

# Package the pipeline YAML
with tarfile.open("pipeline.tar.gz", "w:gz") as tar:
    tar.add("pipeline.yaml", arcname=os.path.basename("pipeline.yaml"))

# Upload and run the pipeline
json_info = {
    "user_namespace": "test",
    "experiment": "experiment_test",
    "pipeline_name": "test",
    "job_name": "training_job",
    "pipeline_version": "74"
}
# Create a multipart-encoded file
files = {
    'file': ('file.tar', open('pipeline.tar.gz', 'rb'), 'application/x-tar')
}

# Send the POST request to submit pipeline and initialize training phase
response = requests.post('http://192.168.1.187:5005/submit', files=files, data={'json_data': json.dumps(json_info)})

from kfp import dsl, compiler
from kfp.dsl import component, pipeline
from kfp import kubernetes
import tarfile
import os
import kfp
import torchvision
import torch

# Define the prepare_data component
@component(
    packages_to_install=["pandas", "numpy", "torchvision"],
    base_image="python:3.9",
)
def prepare_data(output_csv: dsl.Output[dsl.Artifact]):
    import pandas as pd
    import os
    import torchvision.datasets as datasets
    from torchvision import transforms

    # Load dataset
    iris = datasets.FakeData(transform=transforms.ToTensor())  # Using FakeData as a placeholder

    # Convert to DataFrame
    df = pd.DataFrame(iris.data.numpy(), columns=['feat1', 'feat2', 'feat3', 'feat4'])  # Adjust column names as needed
    df["species"] = iris.targets.numpy()

    # Save the prepared data to CSV
    df = df.dropna()

    # Output directory
    output_csv_path = "./output_csv"  # Adjust as needed
    os.makedirs(output_csv_path, exist_ok=True)

    # Save to CSV
    output_csv_path = os.path.join(output_csv_path, "final_df.csv")
    df.to_csv(output_csv_path, index=False)

    print(f"CSV saved to {output_csv_path}")



# Define the train_test_split component
@component(
    packages_to_install=["pandas", "numpy", "scikit-learn", "torch"],
    base_image="python:3.9",
)
def train_test_split(input_csv: dsl.Input[dsl.Artifact], output_dir: dsl.Output[dsl.Artifact]):
    import pandas as pd
    import numpy as np
    import os
    import torch
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

    # Convert to PyTorch tensors
    X_train_tensor = torch.tensor(X_train.values, dtype=torch.float32)
    X_test_tensor = torch.tensor(X_test.values, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train.values.flatten(), dtype=torch.long)  # Assuming y_train is categorical
    y_test_tensor = torch.tensor(y_test.values.flatten(), dtype=torch.long)    # Assuming y_test is categorical

    # Save the splits to .pt files
    torch.save(X_train_tensor, os.path.join(output_dir.path, "X_train.pt"))
    torch.save(X_test_tensor, os.path.join(output_dir.path, "X_test.pt"))
    torch.save(y_train_tensor, os.path.join(output_dir.path, "y_train.pt"))
    torch.save(y_test_tensor, os.path.join(output_dir.path, "y_test.pt"))



# Define the training_basic_classifier component
@component(
    packages_to_install=["pandas", "numpy", "scikit-learn", "torch"],
    base_image="python:3.9",
)
def training_basic_classifier(input_dir: dsl.Input[dsl.Artifact], model_output: dsl.Output[dsl.Artifact]):
    import numpy as np
    import os
    import torch
    from sklearn.linear_model import LogisticRegression

    # Load the training data
    X_train = np.load(os.path.join(input_dir.path, "X_train.npy"))
    y_train = np.load(os.path.join(input_dir.path, "y_train.npy"))

    # Train the logistic regression classifier
    classifier = LogisticRegression(max_iter=500)
    classifier.fit(X_train, y_train)

    # Ensure the output directory exists
    os.makedirs(model_output.path, exist_ok=True)

    # Save the trained model to a .pt file
    model_path = os.path.join(model_output.path, "model.v7.pt")

    # Create a dictionary to save the model state
    model_state = {
        'coef_': torch.tensor(classifier.coef_),    # Convert coefficients to a PyTorch tensor
        'intercept_': torch.tensor(classifier.intercept_),  # Convert intercepts to a PyTorch tensor
        'classes_': torch.tensor(classifier.classes_)  # Convert classes to a PyTorch tensor
    }

    torch.save(model_state, model_path)



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
client = kfp.Client(host="http://192.168.1.240:3001")
client.set_user_namespace("test")
client.create_experiment(name="experiment_test")
retrieved_experiment_id = client.get_experiment(experiment_name="experiment_test").experiment_id
retrieved_pipeline_id =client.get_pipeline_id("test")
defined_job_name = "training_job"
if not id:
    client.upload_pipeline(pipeline_name="test",
                        pipeline_package_path="pipeline.tar.gz")
    running_pipeline = client.run_pipeline(pipeline_package_path="pipeline.tar.gz", experiment_id=retrieved_experiment_id, job_name=defined_job_name, enable_caching=False)
    client.wait_for_run_completion(run_id=running_pipeline.run_id,timeout=500,sleep_duration=5)
    client.delete_run(run_id=running_pipeline.run_id)
else:
    running_version = client.upload_pipeline_version(pipeline_name="test", pipeline_version_name="v62",
                                pipeline_package_path="pipeline.tar.gz")
    retrieved_version_id = running_version.pipeline_version_id
    running_pipeline = client.run_pipeline(pipeline_id=retrieved_pipeline_id, version_id=retrieved_version_id, experiment_id=retrieved_experiment_id, job_name=defined_job_name, enable_caching=False)
    client.wait_for_run_completion(run_id=running_pipeline.run_id,timeout=500,sleep_duration=5)
    client.delete_run(run_id=running_pipeline.run_id)
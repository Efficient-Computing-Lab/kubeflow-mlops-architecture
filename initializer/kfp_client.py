import kfp
import logging

logging.basicConfig(level=logging.INFO)
client = kfp.Client(host="http://192.168.1.187:3001")


def run_instance(user_namespace, experiment, pipeline_name, job_name, pipeline_version, tar_path):
    client.set_user_namespace(user_namespace)
    client.create_experiment(name=experiment)
    retrieved_experiment_id = client.get_experiment(experiment_name=experiment).experiment_id
    logging.info(retrieved_experiment_id)
    retrieved_pipeline_id = client.get_pipeline_id(pipeline_name)
    logging.info(retrieved_pipeline_id)
    if not retrieved_pipeline_id:
        client.upload_pipeline(pipeline_name=pipeline_name,
                               pipeline_package_path=tar_path)
        running_pipeline = client.run_pipeline(pipeline_package_path=tar_path, experiment_id=retrieved_experiment_id,
                                               job_name=job_name, enable_caching=False)
        logging.info(running_pipeline)

    else:
        running_version = client.upload_pipeline_version(pipeline_name=pipeline_name,
                                                         pipeline_version_name=pipeline_version,
                                                         pipeline_package_path=tar_path)
        retrieved_version_id = running_version.pipeline_version_id
        running_pipeline = client.run_pipeline(pipeline_id=retrieved_pipeline_id,
                                               version_id=retrieved_version_id, experiment_id=retrieved_experiment_id,
                                               job_name=job_name, enable_caching=False)
        logging.info(running_pipeline)

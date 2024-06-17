import kfp

client = kfp.Client(host="http://192.168.1.240:3001")
def run_instance(user_namespace, experiment, pipeline_name, job_name, pipeline_version):
        
        client.set_user_namespace(user_namespace)
        client.create_experiment(name=experiment)
        retrieved_experiment_id = client.get_experiment(experiment_name=experiment).experiment_id
        retrieved_pipeline_id =client.get_pipeline_id(pipeline_name)
        if not retrieved_pipeline_id:
            client.upload_pipeline(pipeline_name=pipeline_name,
                                pipeline_package_path="pipeline.tar.gz")
            running_pipeline = client.run_pipeline(pipeline_package_path="pipeline.tar.gz", experiment_id=retrieved_experiment_id, job_name=job_name, enable_caching=False)
            client.wait_for_run_completion(run_id=running_pipeline.run_id,timeout=500,sleep_duration=5)
            client.delete_run(run_id=running_pipeline.run_id)
        else:
            running_version = client.upload_pipeline_version(pipeline_name=pipeline_name, pipeline_version_name=pipeline_version,
                                        pipeline_package_path="pipeline.tar.gz")
            retrieved_version_id = running_version.pipeline_version_id
            running_pipeline = client.run_pipeline(pipeline_id=retrieved_pipeline_id, version_id=retrieved_version_id, experiment_id=retrieved_experiment_id, job_name=job_name, enable_caching=False)
            client.wait_for_run_completion(run_id=running_pipeline.run_id,timeout=500,sleep_duration=5)
            client.delete_run(run_id=running_pipeline.run_id)
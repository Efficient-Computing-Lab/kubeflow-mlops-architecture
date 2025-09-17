# Initializer

## Overview
Initializer receives POST requests containing JSON data and a tar file from Github actions and uses KFP client to start a pipeline.

## Usage
To submit JSON data along with a file to the web service, use the following `curl` command:

```sh
curl -X POST http://<ip>:5000/submit -F "json_data={\"user_namespace\":\"test\",\"experiment\":\"experiment_test\",\"pipeline_name\":\"test\",\"job_name\":\"training_job\",\"pipeline_version\":\"v62\"}" -F "file=@path/to/your/file.tar"
```
# Dataset Registry

## Overview

This registry stores the datasets that will be used in order to train models. Developers are able to upload
the desired datasets and then download them to train their models.

## Upload
The upload endpoint saves the dataset under the appropriate model
```sh
curl -X POST http://147.102.109.92:4422:5000/upload/ \
    -F "file=@/path/to/epos.zip" \
    -F "model_name=epos"
```
## Download
The download endpoint requires to know the name of the model and it finds by its own the respective dataset.
```sh
curl -X GET http://147.102.109.92:4422/download/epos --output epos.zip
```
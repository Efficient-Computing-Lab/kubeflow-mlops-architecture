# Use an Ubuntu-based image for simplicity
FROM continuumio/miniconda3

WORKDIR /app
RUN mkdir store
RUN mkdir datasets
SHELL ["/bin/bash", "-c"]
# Install dependencies and git
RUN apt-get update && apt-get install -y \
    wget \
    git \
    bzip2 \
    ca-certificates \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    unzip \
    nvidia-367-dev \
    && apt-get clean
# Clone epos repository
RUN git clone https://github.com/thodan/epos.git
COPY dataset_params.py /app/epos/external/bop_toolkit/bop_toolkit_lib/dataset_params.py
# Install Miniconda, create the conda environment with Python 3.6.10, and install packages
RUN conda config --set ssl_verify false && \
    conda create --name epos python=3.6.10 -y && \
    conda init bash && \
    source /root/.bashrc && \
    conda activate epos && \
    conda install -y numpy=1.16.6 && \
    conda install -y cudatoolkit=9.0 && \
    conda install -y _tflow_select=2.1.0 && \
    conda install -y -c conda-forge tensorflow=1.12.0 && \
    conda install -y -c conda-forge tensorflow-gpu=1.12.0 && \
    conda install -y pyyaml=5.3.1 && \
    conda install -y opencv=3.4.2 && \
    conda install -y pandas=1.0.5 tabulate=0.8.3 imageio=2.9.0 && \
    conda install -y -c mjirik pypng=0.0.18 && \
    conda install -y -c conda-forge igl && \
    conda install -y glog=0.4.0

CMD ["python3", "-c", "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"]

ENV REPO_PATH=/app/epos
ENV STORE_PATH=/app/store
ENV BOP_PATH=/app/datasets

ENV TF_DATA_PATH=$STORE_PATH/tf_data
ENV TF_MODELS_PATH=$STORE_PATH/tf_models

ENV PYTHONPATH=$REPO_PATH:$PYTHONPATH
ENV PYTHONPATH=$REPO_PATH/external/bop_renderer/build:$PYTHONPATH
ENV PYTHONPATH=$REPO_PATH/external/bop_toolkit:$PYTHONPATH
ENV PYTHONPATH=$REPO_PATH/external/progressive-x/build:$PYTHONPATH
ENV PYTHONPATH=$REPO_PATH/external/slim:$PYTHONPATH

ENV LD_LIBRARY_PATH=$REPO_PATH/external/llvm/lib:$LD_LIBRARY_PATH
COPY params.yml $TF_MODELS_PATH/params.yml
COPY training_epos_Objs12.zip $BOP_PATH/training_epos_Objs12.zip
RUN cd /app/datasets/ && \
    unzip training_epos_Objs12.zip && \
    rm params.yml && \
    mkdir carObj12 && \
    mv training_set carObj12/training_primesense

RUN conda init bash && \
    source /root/.bashrc && \
    conda activate epos &&


# Set the entry point to use the conda environment
CMD ["/bin/bash"]

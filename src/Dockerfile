# Use a Miniconda-based image
FROM ubuntu:20.04
#FROM latelee/cuda:9.0-cudnn7-runtime
#FROM nvidia/cuda:12.4.1-runtime-ubuntu20.04

WORKDIR /app
#SHELL ["/bin/bash","-c"]
# Create necessary directories in one step
RUN mkdir -p store/tf_models/obj12 datasets/carObj12

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y tzdata
RUN ln -fs /usr/share/zoneinfo/Region/City /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata
# Install dependencies and git
RUN apt-get update && apt-get install -y \
    locales wget git bzip2 ca-certificates libglib2.0-0 libxext6 libsm6 libxrender1 unzip curl patch g++ cmake && \
    apt-get clean

RUN mkdir -p /opt/miniconda3 && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /opt/miniconda3/miniconda.sh && \
    bash /opt/miniconda3/miniconda.sh -b -u -p /opt/miniconda3


ENV PATH=/opt/miniconda3/bin:$PATH
RUN conda init bash
# Clone the epos repository
RUN git clone --recurse-submodules https://github.com/thodan/epos.git

# Copy relevant files
COPY dataset_params.py /app/epos/external/bop_toolkit/bop_toolkit_lib/dataset_params.py
#COPY config.py /app/epos/epos_lib/config.py
COPY params.yml /app/store/tf_models/obj12/params.yml
COPY start_training.sh /app/
#COPY datagen.py /app/epos/epos_lib/datagen.py
#COPY training_epos_Objs12.zip /app/datasets/
COPY models_cad.zip /app/datasets/carObj12/

# Install Conda environment and packages in a single step to keep environment activation
RUN conda config --set ssl_verify false && \
    conda create --name epos python=3.6.10 -y &&\
    conda install -n epos -y numpy=1.16.6 cudatoolkit=9.0 _tflow_select=2.1.0 tensorflow=1.12.0 tensorflow-gpu=1.12.0 && \
    conda install -n epos -y pyyaml=5.3.1 opencv=3.4.2 pandas=1.0.5 tabulate=0.8.3 imageio=2.9.0 && \
    conda install -n epos -y -c mjirik pypng=0.0.18 && \
    conda install -n epos -y -c conda-forge igl && \
    conda install -n epos -y glog=0.4.0 && \
    conda run -n epos pip install absl-py==1.1.0

#ENV PATH=/opt/miniconda3/envs/epos/bin:$PATH

# Extract datasets
#RUN unzip /app/datasets/training_epos_Objs12.zip -d /app/datasets/ && \
#    rm /app/datasets/params.yml && \
#    mv /app/datasets/training_set /app/datasets/carObj12/train_primesense
RUN unzip /app/datasets/carObj12/models_cad.zip -d /app/datasets/carObj12 && \
    mkdir -p /app/datasets/carObj12/models_eval && \
    cp /app/datasets/carObj12/models_cad/obj_000001.ply /app/datasets/carObj12/models_eval && \
    cp /app/datasets/carObj12/models_cad/obj_000002.ply /app/datasets/carObj12/models_eval

# Set environment variables
ENV REPO_PATH=/app/epos
ENV STORE_PATH=/app/store
ENV BOP_PATH=/app/datasets
ENV TF_DATA_PATH=$STORE_PATH/tf_data
ENV TF_MODELS_PATH=$STORE_PATH/tf_models
ENV PYTHONPATH=$REPO_PATH:$PYTHONPATH
#ENV $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
ENV PYTHONPATH=$REPO_PATH/external/bop_renderer/build:$PYTHONPATH
ENV PYTHONPATH=$REPO_PATH/external/bop_toolkit:$PYTHONPATH
ENV PYTHONPATH=$REPO_PATH/external/progressive-x/build:$PYTHONPATH
ENV PYTHONPATH=$REPO_PATH/external/slim:$PYTHONPATH
#ENV LD_LIBRARY_PATH=/usr/local/cuda-12.4/lib64:/usr/local/cuda-12.4/lib
ENV LD_LIBRARY_PATH=$REPO_PATH/external/llvm/lib:$LD_LIBRARY_PATH

ENV OSMESA_PREFIX=$REPO_PATH/external/osmesa
ENV LLVM_PREFIX=$REPO_PATH/external/llvm
#ENV CUDA_HOME=/usr/local/cuda-12.4

COPY osmesa-install.sh $REPO_PATH/external/bop_renderer/omesa-install/
RUN apt-get update && apt-get install -y zlib1g-dev autoconf build-essential pkgconf libtool
RUN mkdir -p $OSMESA_PREFIX && \
    mkdir -p $LLVM_PREFIX && \
    mkdir -p build &&\
    cd build && \
    bash $REPO_PATH/external/bop_renderer/omesa-install/osmesa-install.sh
RUN conda init bash && \
    . /root/.bashrc && \
    conda activate epos && \
    cd $REPO_PATH/external/bop_renderer && \
    mkdir build && \
    cd build && \
    export PYTHON_PREFIX=/opt/miniconda3/envs/epos && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j8
# Set the final CMD to run bash with the activated conda environment
RUN echo "source /opt/miniconda3/etc/profile.d/conda.sh" >> /root/.bashrc && \
    echo "conda init" >> /root/.bashrc && \
    echo "conda activate epos" >> /root/.bashrc

#CMD ["conda", "run", "-n", "epos", "/bin/bash", "-c","./start_training.sh"] \
CMD ["/bin/bash"]

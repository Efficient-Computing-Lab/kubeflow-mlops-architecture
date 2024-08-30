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
    && apt-get clean
# Clone epos repository
RUN git clone https://github.com/thodan/epos.git
# Install Miniconda, create the conda environment with Python 3.6.10, and install packages
RUN conda config --set ssl_verify false && \
    conda create --name epos python=3.6.10 -y && \
    conda init bash && \
    source /root/.bashrc && \
    conda activate epos && \
    conda install -y numpy=1.16.6 && \
    conda install -y tensorflow-gpu=1.12.0 && \
    conda install -y pyyaml=5.3.1 && \
    conda install -y opencv=3.4.2 && \
    conda install -y pandas=1.0.5 tabulate=0.8.3 imageio=2.9.0 && \
    conda install -y -c mjirik pypng=0.0.18 && \
    conda install -y -c conda-forge igl && \
    conda install -y glog=0.4.0

COPY env_vars.sh $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
RUN  conda activate epos


# Set the entry point to use the conda environment
CMD ["conda", "run", "-n", "epos", "/bin/bash"]

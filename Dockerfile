# A mass cytometry workflow environment
FROM condaforge/mambaforge:24.3.0-0

# Upgrade pip and install necessary Python packages, then clean up
RUN pip install --upgrade pip && \
    pip install pyyaml && \
    mamba clean --all --yes

# Copy environment.yml and install environment
COPY environment.yml /tmp/environment.yml
COPY scripts/install_environment.py /tmp/install_environment.py

# Install environment and clean up
RUN cd /tmp && \
    python /tmp/install_environment.py > /tmp/conda_install.sh && \
    bash /tmp/conda_install.sh && \
    mamba clean --all --yes

# Set non-interactive frontend to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and clean up
RUN apt-get update && \
    apt-get install -y libcairo2-dev tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install R packages using Mamba
RUN mamba install -c conda-forge r-cairo=1.6 && mamba clean --all --yes

# Install Cairo R package from CRAN
RUN R -e "install.packages('Cairo', dependencies=TRUE, repos='http://cran.rstudio.com/')"

# Copy the source code and install the package
COPY . /source/cio-mass-cytometry
RUN cd /source/cio-mass-cytometry && pip install . && mamba clean --all --yes

# Create necessary directories and set permissions
RUN mkdir /.local && chmod 777 /.local && mkdir /.jupyter && chmod 777 /.jupyter

# Set the working directory
WORKDIR /home

# Command to start Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--allow-root"]


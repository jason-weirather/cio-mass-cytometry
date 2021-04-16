# A mass cytometry workflow environment
FROM continuumio/miniconda3:4.9.2
ENV CONDA_PREFIX /opt/conda

RUN conda update -y conda

RUN pip install --upgrade pip && \
    pip install pyyaml

COPY environment.yml /tmp/environment.yml
COPY scripts/install_environment.py /tmp/install_environment.py

RUN cd /tmp && \
    python /tmp/install_environment.py > /tmp/conda_install.sh && \
    bash /tmp/conda_install.sh

#COPY entrypoint.sh /usr/local/bin/entrypoint.sh
#RUN conda env create -f /tmp/environment.yml
#RUN echo "source activate $(head -1 /tmp/environment.yml | cut -d' ' -f2)" > ~/.bashrc
#ENV PATH /opt/conda/envs/$(head -1 /tmp/environment.yml | cut -d' ' -f2)/bin:$PATH
# Set subsequent commands to use the environment
#SHELL ["conda","run","-n","cio_mass_cytometry","/bin/bash","-c"]

# Make sure the environment is activate
#RUN echo "Make sure R is installed"
#RUN R --version

#COPY conda /tmp/conda
#COPY LICENSE /tmp/LICENSE
#COPY conda/.condarc ~/.condarc

#RUN cd /tmp/conda && \
#    conda build --output-folder . .

WORKDIR /home

##ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
#ENTRYPOINT ["conda","run","--no-capture-output","-n",

CMD ["jupyter","lab","--ip=0.0.0.0","--port=8888","--allow-root"]

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

RUN mkdir /.local && \
    chmod 777 /.local

WORKDIR /home

##ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
#ENTRYPOINT ["conda","run","--no-capture-output","-n",

CMD ["jupyter","lab","--ip=0.0.0.0","--port=8888","--allow-root"]

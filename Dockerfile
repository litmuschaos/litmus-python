
FROM python:3.8

LABEL maintainer="LitmusChaos"

ARG TARGETARCH

# upgrade and setup python
RUN apt-get update \
    && apt-get -y install gcc python-pip python3-pip python-dev curl \
    && pip install --upgrade pip

# Setup kubectl
WORKDIR /litmus/kubectl/
RUN curl -Lsf -o kubectl https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

RUN rm -rf /tmp/* /root/.cache

ENV LC_ALL=C.UTF-8

ENV LANG=C.UTF-8

WORKDIR /litmus

# Copying Necessary Files
COPY . .

# Setup requirements
RUN pip3 install -r requirements.txt
RUN python3 setup.py install

# Copying experiment file
COPY ./bin/experiment/experiment.py ./experiments

ENV PYTHONPATH /litmus

ENTRYPOINT ["python3"]

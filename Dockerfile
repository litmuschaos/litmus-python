
FROM python:3.8

LABEL maintainer="LitmusChaos"

ARG TARGETARCH

# upgrade and setup python
RUN apt-get update \
    && apt-get -y install gcc python3-pip python-dev curl \
    && pip install --upgrade pip \
    && pip install jinja2 pyYaml

#Installing kops
ENV kopsversion=v1.20.0
RUN curl -Lsf -o kops-linux https://github.com/kubernetes/kops/releases/download/${kopsversion}/kops-linux-${TARGETARCH}
RUN chmod +x ./kops-linux
RUN mv ./kops-linux /usr/local/bin/kops

#Installing Kubectl
ENV KUBE_LATEST_VERSION="v1.18.0"
RUN curl -L https://storage.googleapis.com/kubernetes-release/release/${KUBE_LATEST_VERSION}/bin/linux/${TARGETARCH}/kubectl -o     /usr/local/bin/kubectl && \
chmod +x /usr/local/bin/kubectl

RUN rm -rf /tmp/* /root/.cache

ENV LC_ALL=C.UTF-8

ENV LANG=C.UTF-8

WORKDIR /litmus

# Copying Necessary Files
COPY . .

# Setup requirements
RUN pip3 install -r requirements.txt
RUN python3 setup.py install

WORKDIR /litmus/byoc

# Setup requirements for byoc
RUN chmod +x install.sh
RUN ./install.sh

WORKDIR /litmus

# Copying experiment file
COPY ./bin/experiment/experiment.py ./experiment

ENV PYTHONPATH /litmus

ENTRYPOINT ["python3"]

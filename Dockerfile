FROM python:3.8

LABEL maintainer="LitmusChaos"

ARG TARGETARCH
ARG USER=litmus
### upgrade and setup python
### upgrade and setup python
RUN apt-get update \
    && apt-get -y install gcc python-pip python3-pip python-dev curl \
    && pip install --upgrade pip

### Setup kubectl
WORKDIR /litmus/kubectl/
RUN curl -Lsf -o kubectl https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

### Setup requirements

RUN rm -rf /tmp/* /root/.cache
ENV LC_ALL=C.UTF-8

ENV LANG=C.UTF-8

# COPY requirements.txt requirements.txt
# RUN pip install -r requirements.txt

RUN ls
WORKDIR /litmus
COPY . .
RUN ls
RUN pip3 install -r requirements.txt
RUN python3 setup.py install
RUN pip3 install kubernetes
COPY ./bin/experiment/experiment.py ./experiments
RUN ls 
#CMD ["python3", "experiments"]
ENV PYTHONPATH /litmus
#RUN ENV PYTHONPATH

ENTRYPOINT ["python3"]
# #WORKDIR /
# COPY . .
# #Copying Necessary Files

# COPY ./bin/experiment/experiment.py ./litmus/experiments
# RUN ls -A
# # COPY requirements.txt requirements.txt
# # RUN pip install -r requirements.txt
# #RUN python3 setup.py install
# WORKDIR /litmus
# COPY . .
# RUN ls
# COPY setup.py setup.py
# RUN python3 setup.py install

# RUN python3 experiments
# CMD ["python3", "experiments"]
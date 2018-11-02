FROM resin/raspberry-pi-debian

RUN apt-get update && apt-get install -yq \
	git \
	python3 \
	python3-dev \
	gcc \
	nano \
	build-essential  \
&& apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -yq \
	python3-venv \
&& apt-get clean && rm -rf /var/lib/apt/lists/*	

WORKDIR /usr/src/app

# Install pip from download
RUN curl https://bootstrap.pypa.io/get-pip.py | python3 && pip3 install pip -U

# RUN python3 -m venv env

# Install Code For DHT22
RUN git clone --recursive https://github.com/freedom27/MyPyDHT && \
cd /usr/src/app/MyPyDHT && \
python3 setup.py install

# --prefix=/usr/src/app/env
COPY ./requirements.txt /requirements.txt

# Install the python dependancies, and use the piwheels repo
RUN pip install -r /requirements.txt --extra-index-url https://www.piwheels.org/simple


COPY . .

CMD ["python3", "texter.py"]

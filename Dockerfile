FROM balenalib/rpi-raspbian:stretch

ENV VERSION 0.1.0

RUN install_packages \
	git \
	python3 \
	python3-dev \
	python3-pip \
	gcc \
	nano \
	build-essential  \
	python3-venv \
	wget \
	openssl

WORKDIR /usr/src/app

# Install pip from download
RUN pip3 install pip -U

# RUN python3 -m venv env



# --prefix=/usr/src/app/env
COPY ./requirements.txt /requirements.txt

# Install the python dependancies, and use the piwheels repo
RUN pip install -Ur /requirements.txt --extra-index-url https://www.piwheels.org/simple


ENV UPGATEGIT 1.7
# Install GO! And make go folder
RUN curl https://dl.google.com/go/go1.14.3.linux-armv6l.tar.gz | tar -C /usr/local -xvz && mkdir -p /usr/src/app/go

# Do GO environment things to we can use it
ENV GOPATH="/usr/src/app/go"
ENV PATH="/usr/local/go/bin:$GOPATH/bin:$PATH"

# Install the latest version of LND!
RUN go get -d -v github.com/lightningnetwork/lnd && \
  cd $GOPATH/src/github.com/lightningnetwork/lnd && \
  make && make install tags="experimental autopilotrpc signrpc walletrpc chainrpc invoicesrpc routerrpc watchtowerrpc dev"

RUN git clone https://github.com/sako0938/lnd_pyshell.git
ENV PATH="/usr/src/app/lnd_pyshell/node_scripts:$PATH"
ENV NODE_IP="localhost"


# Install Code For DHT22
RUN git clone --recursive https://github.com/freedom27/MyPyDHT && \
cd /usr/src/app/MyPyDHT && \
python3 setup.py install

COPY . .

CMD ["bash", "start"]

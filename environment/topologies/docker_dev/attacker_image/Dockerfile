FROM ubuntu:22.04

# Install python 3.10
RUN apt-get update && \
    apt-get -y install software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get -y install python3.10 python3-venv python3-pip

RUN apt-get -y install git curl golang-go

# Set up python virtualenv
ENV VIRTUAL_ENV=/opt/venv/caldera
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN git clone https://github.com/bsinger98/caldera.git --recursive

WORKDIR /caldera

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8888
# Default HTTPS port for web interface and agent beacons over HTTPS (requires SSL plugin to be enabled)
EXPOSE 8443
# TCP and UDP contact ports
EXPOSE 7010
EXPOSE 7011/udp
# Websocket contact port
EXPOSE 7012
# Default port to listen for DNS requests for DNS tunneling C2 channel
EXPOSE 8853
# Default port to listen for SSH tunneling requests
EXPOSE 8022
# Default FTP port for FTP C2 channel
EXPOSE 2222

CMD ["python3", "server.py", "--insecure", "--fresh"]
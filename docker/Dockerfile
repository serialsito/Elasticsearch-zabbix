
FROM ubuntu:xenial
RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add
RUN apt-get -y --no-install-recommends install -y software-properties-common
RUN add-apt-repository 'deb http://packages.elastic.co/elasticsearch/2.x/debian stable main'

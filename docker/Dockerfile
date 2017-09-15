FROM ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive

RUN  apt-get update \
  && apt-get install -y wget
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN apt-get install -y git
RUN apt-get install -y python-pip

RUN wget https://download.elasticsearch.org/elasticsearch/release/org/elasticsearch/distribution/tar/elasticsearch/2.1.1/elasticsearch-2.1.1.tar.gz
RUN tar xzvf elasticsearch-2.1.1.tar.gz

RUN add-apt-repository -y ppa:webupd8team/java
RUN echo debconf shared/accepted-oracle-license-v1-1 select true |  debconf-set-selections
RUN echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections
RUN apt-get update
RUN wget http://download.oracle.com/otn-pub/java/jdk/8u144-b01/090f390dda5b47b9b721c7dfaa008135/jdk-8u144-linux-i586.tar.gz
RUN mkdir /var/cache/oracle-jdk8-installer
RUN mv jdk-8u144-linux-i586.tar.gz /var/cache/oracle-jdk8-installer/jdk-8u144-linux-i586.tar.gz
RUN apt-get install -y oracle-java8-installer
RUN java -version

RUN wget http://repo.zabbix.com/zabbix/3.2/ubuntu/pool/main/z/zabbix/zabbix-agent_3.2.0-1+xenial_amd64.deb
RUN apt-get install libcurl3 && dpkg -i zabbix-agent_3.2.0-1+xenial_amd64.deb
ADD ./ /opt/elasticsearch-zabbix/
ADD ./config/zabbix_agentd.conf /etc/zabbix/zabbix_agentd.conf
RUN cd /opt/ \
  &&  ls -la /opt/elasticsearch-zabbix/ \
  &&  cp -fv /opt/elasticsearch-zabbix/ESzabbix.userparm /etc/zabbix/zabbix_agentd.d/elasticsearch.conf \
  &&  sed -i 's/\/opt\/zabbix\/externalscripts/\/opt\/elasticsearch-zabbix/g' /etc/zabbix/zabbix_agentd.d/elasticsearch.conf \
  &&  chown -v -R zabbix:zabbix /opt/elasticsearch-zabbix \
  &&  pip install pyes elasticsearch

RUN apt-get update && apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor

ADD ./config/elasticsearch.conf /etc/supervisor/conf.d/elasticsearch.conf
ADD ./config/zabbix-agent.conf /etc/supervisor/conf.d/zabbix-agent.conf
RUN ./elasticsearch-2.1.1/bin/elasticsearch -Des.insecure.allow.root=true
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
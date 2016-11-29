FROM ubuntu:14.04
MAINTAINER Maria Yancheva <maria.yancheva@gmail.com>

# General installs of various dependencies, and webserver + python
RUN sudo apt-get -y update && apt-get -y install \
	apache2 \
	apache2-doc \
	apache2-utils \
    build-essential \
	git \
	libapache2-mod-wsgi \
	libcurl4-openssl-dev \
	libffi-dev \
	libgsl0-dev \
	libmysqlclient-dev \
    ntp \
	python-dev \
	python-matplotlib \
	python-pip \
	supervisor \
	unzip \
	wget \
	&& rm -rf /var/lib/apt/lists/*

# Setup environment variables
ENV TALK2ME_BASEDIR=/u/spoclabweb/site/csc2518 \
    HOME=/u/spoclabweb 
    
# Set up directories to mimic the CSLab setup
RUN sudo mkdir /u && sudo mkdir /u/spoclabweb && sudo mkdir /u/spoclabweb/site && sudo mkdir /u/spoclabweb/site/www && sudo mkdir /u/spoclabweb/site/cgi-bin
RUN sudo mkdir /cs && sudo mkdir /cs/htdata && sudo mkdir /cs/htdata/user-webserver && sudo mkdir /cs/htdata/user-webserver/conf

# Install Python libraries
RUN sudo mkdir $HOME/temp
COPY docker/requirements.txt $HOME/temp/requirements.txt
RUN sudo pip install --upgrade pip && sudo pip install -r $HOME/temp/requirements.txt

# SERVER.
RUN sudo a2enmod ssl
COPY docker/talk2me.conf /etc/apache2/sites-available/talk2me.conf
COPY docker/apache2.conf /etc/apache2/apache2.conf
COPY docker/blank.conf /cs/htdata/user-webserver/conf/apache2.conf
RUN chmod 644 /etc/apache2/sites-available/talk2me.conf
RUN sudo a2ensite talk2me
RUN sudo a2enmod rewrite
EXPOSE 80 443

# vim config
COPY docker/.vimrc $HOME/.vimrc

# Clean up
WORKDIR $TALK2ME_BASEDIR
RUN sudo rm -rf $HOME/temp

# Start up the web server and the ntpd for keeping the system time synced to the network
COPY docker/supervisord.conf /etc/supervisord.conf
RUN chmod 644 /etc/supervisord.conf
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisord.conf"]
FROM	debian:buster

RUN		apt upgrade

RUN		apt-get update && apt-get install -y nginx openssl vim

RUN		apt-get install curl -y


RUN     mkdir -p /var/www/html/media/avatars

COPY    ./front/default_avatar.png /var/www/html/media/avatars

COPY	./tools/nginx_configure.sh /tmp/

RUN		chmod +x /tmp/nginx_configure.sh

RUN		rm -rf /etc/nginx/sites-enabled/default && rm -rf /etc/nginx/sites-available/default 

COPY	./conf/config_transcendence  /etc/nginx/sites-available


RUN 	ln -s	/etc/nginx/sites-available/config_transcendence  /etc/nginx/sites-enabled/config_transcendence

EXPOSE	443

CMD ["/tmp/nginx_configure.sh"]

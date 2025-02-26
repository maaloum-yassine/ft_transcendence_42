#!/bin/sh

# Créer un répertoire pour les certificats SSL
mkdir -p /etc/nginx/certificate

openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/certificate/transcendence.key -out /etc/nginx/certificate/transcendence.crt -subj /C=MA/ST=AGA/L=agadir/O=1337/OU=42Network/CN=ymaaloum

# Écrire la configuration de NGINX dans nginx.conf
cat > /etc/nginx/nginx.conf << EOF
	events
	{
			worker_connections 768;
	}
	http
	{
		include /etc/nginx/sites-enabled/*;
	}
EOF

# sed -i -e "s/container_user_managemant/$(getent hosts container_user_managemant | awk '{print $1}')/g" /etc/nginx/sites-enabled/config_transcendence
# sed -i -e "s/container_user_managemant/$(getent hosts container_user_managemant | awk '{print $1}')/g" /etc/nginx/sites-available/config_transcendence

nginx -g "daemon off;"
#!/bin/sh

# Créer un répertoire pour les certificats SSL
mkdir -p /etc/nginx/certificate

openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/certificate/transcendence.key -out /etc/nginx/certificate/transcendence.crt -subj /C=MA/ST=AGA/L=agadir/O=1337/OU=42Network/CN=ymaaloum

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

nginx -g "daemon off;"

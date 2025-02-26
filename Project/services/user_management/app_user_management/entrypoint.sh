#!/bin/bash


# sleep 5

echo "Vérification de la disponibilité de la base de données PostgreSQL..."
until pg_isready -h "$CONTAINER_POSTGRES" -p 5432 -U "$POSTGRES_USER" -d "$DB_NAME"; do
  echo "En attente de PostgreSQL..."
  sleep 2
done

echo "PostgreSQL est prêt ! Lancement des migrations."

python manage.py makemigrations

sleep 2

python manage.py migrate

# python manage.py runserver_plus   --cert-file cert.pem --key-file key.pem  127.0.0.1:8000


python manage.py runserver 0.0.0.0:8000

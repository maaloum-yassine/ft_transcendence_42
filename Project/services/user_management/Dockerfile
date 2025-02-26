FROM python:3.9

WORKDIR  /app

RUN     apt-get update && apt-get install -y postgresql-client

COPY    ./app_user_management /app/

RUN      python -m pip install --upgrade pip 

RUN     pip install -r requirement_new.txt 

EXPOSE  8000

ENTRYPOINT ["/app/entrypoint.sh"]

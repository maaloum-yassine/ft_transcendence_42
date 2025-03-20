all : up

up:
	docker compose -f ./Project/docker-compose.yml up --build

down :
	@docker compose -f ./Project/docker-compose.yml down -v --rmi all

stop :
	@docker compose -f ./Project/docker-compose.yml stop

start :
	@docker compose -f ./Project/docker-compose.yml start  || true

status :
	@docker ps -a | grep "nginx\|container_redis\|container_postgres\|container_user_managemant" || true

	# echo $(ifconfig | grep inet | awk 'NR==5{print $2}')

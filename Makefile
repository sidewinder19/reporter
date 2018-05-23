initial:
	sudo apt-get update && sudo apt-get install -y docker git
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
	sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
	sudo apt-get update
	apt-cache policy docker-ce
	sudo apt-get install -y docker-ce

docker-up:
	sudo docker-compose --verbose up -d db
	sudo docker-compose --verbose up -d dbtest
	sudo docker-compose --verbose up -d api

docker-down:
	sudo docker-compose down -v

seed-database:
	git clone https://github.com/datacharmer/test_db.git
	cd test_db; \
	IP_DB=$$(sudo docker inspect --format '{{ .NetworkSettings.Networks.reporter_backend.IPAddress }}' reporter_db_1); \
	echo $$IP_DB; \
	TEST=$$(echo 'yada') \
	sudo mysql --host $$IP_DB --port 3306 --user root -pmasterpw employees < employees.sql

test-api:
	IP_DB_TEST=$$(sudo docker inspect --format '{{ .NetworkSettings.Networks.reporter_backend.IPAddress }}' reporter_dbtest_1); \
	sudo docker-compose run -e MYSQL_HOST_TEST=$$IP_DB_TEST api python manage.py test web

sample-api:
	IP_API=$$(sudo docker inspect --format '{{ .NetworkSettings.Networks.reporter_backend.IPAddress }}' reporter_api_1); \
        curl -X GET http://$$IP_API:8000/reports/?quarters=2


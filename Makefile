# Initialize an Ubuntu instance to operate as Docker host.
initial:
	sudo apt-get update && sudo apt-get install -y docker git
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
	REL=$$(lsb_release -cs); \
	sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $$REL stable"
	sudo apt-get update
	apt-cache policy docker-ce
	sudo apt-get install -y docker-ce

# Build and start up database and API containers.
docker-up:
	sudo docker-compose --verbose up -d db
	sudo docker-compose --verbose up -d dbtest
	sudo docker-compose --verbose up -d api

# Shut down docker containers
docker-down:
	sudo docker-compose down -v

# Load test data into database container.
seed-database:
	if [ -d "~/test_db" ]; then \
	     git clone https://github.com/datacharmer/test_db.git; \
	fi
	cd test_db; \
	IP_DB=$$(sudo docker inspect --format '{{ .NetworkSettings.Networks.reporter_backend.IPAddress }}' reporter_db_1); \
	sudo mysql --host $$IP_DB --port 3306 --user root employees < employees.sql

# Run database-oriented unit tests.
tests:
	IP_DB_TEST=$$(sudo docker inspect --format '{{ .NetworkSettings.Networks.reporter_backend.IPAddress }}' reporter_dbtest_1); \
	sudo docker-compose run -e MYSQL_HOST_TEST=$$IP_DB_TEST api python manage.py test web

# Make a sample call against the running API container.
sample-api:
	IP_API=$$(sudo docker inspect --format '{{ .NetworkSettings.Networks.reporter_backend.IPAddress }}' reporter_api_1); \
        curl -X GET http://$$IP_API:8000/reports/?quarters=2

# Run all dependencies.
all: initial docker-up seed-database tests sample-api


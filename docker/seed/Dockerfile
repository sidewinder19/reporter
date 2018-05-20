FROM ubuntu:16.04
RUN mkdir /data
WORKDIR /data
COPY docker/seed/mysql_upload.sh .
RUN chmod +x mysql_upload.sh
RUN apt-get update && apt-get install -y \
  git
  mysql-server
  libmysqlclient-dev 
  mysql-client 
RUN git clone $GIT_REPO
CMD ./mysql_upload.sh


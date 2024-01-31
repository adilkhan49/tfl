FROM mariadb:latest

ENV MYSQL_ROOT_PASSWORD root123
ENV MYSQL_DATABASE tfl
ENV MYSQL_USER dev
ENV MYSQL_PASSWORD pwd

COPY init /docker-entrypoint-initdb.d/

EXPOSE 3306
FROM postgres:latest

# RUN apt-get -y update && apt-get install -y wget

COPY entrypoint.sh /docker-entrypoint-initdb.d/

ENV POSTGRES_USER root
ENV POSTGRES_PASSWORD secret 
ENV POSTGRES_DB tfl

EXPOSE 54321
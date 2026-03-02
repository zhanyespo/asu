# Base image: ubuntu:22.04
FROM ubuntu:22.04

# ARGs
# https://docs.docker.com/engine/reference/builder/#understand-how-arg-and-from-interact
ARG TARGETPLATFORM=linux/amd64,linux/arm64
ARG DEBIAN_FRONTEND=noninteractive
ARG GITHUB_TOKEN

# neo4j 5.5.0 installation and some cleanup
RUN apt-get update && \
    apt-get install -y wget gnupg software-properties-common git && \
    wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add - && \
    echo 'deb https://debian.neo4j.com stable latest' > /etc/apt/sources.list.d/neo4j.list && \
    add-apt-repository universe && \
    apt-get update && \
    apt-get install -y nano unzip neo4j python3-pip && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN python3 -m pip install --upgrade pip && \
    pip install neo4j pandas pyarrow requests
    
# TODO: Complete the Dockerfile
WORKDIR /app

RUN git clone https://$GITHUB_TOKEN@github.com/SP-2025-CSE511-Data-Processing-at-Scale/Project-1-zyesposs.git

# used for local testing by docker-compose before git switch
# COPY . /app

WORKDIR /app/Project-1-zyesposs

RUN wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-03.parquet -O yellow_tripdata_2022-03.parquet

# Copy GDS plugin
RUN mkdir -p /var/lib/neo4j/plugins
# used for locally as file was provide by TA
# COPY data/neo4j-graph-data-science-2.15.0.jar /var/lib/neo4j/plugins/

#switched to use it TA provided website 
RUN wget https://graphdatascience.ninja/neo4j-graph-data-science-2.15.0.zip -O /tmp/gds.zip && \
    unzip /tmp/gds.zip -d /tmp && \
    mv /tmp/neo4j-graph-data-science-2.15.0.jar /var/lib/neo4j/plugins/ && \
    rm -rf /tmp/*

RUN sed -i 's/#dbms.default_listen_address=0.0.0.0/dbms.default_listen_address=0.0.0.0/' /etc/neo4j/neo4j.conf && \
    echo 'dbms.security.procedures.unrestricted=gds.*' >> /etc/neo4j/neo4j.conf && \
    echo 'dbms.security.procedures.allowlist=gds.*' >> /etc/neo4j/neo4j.conf

# Run the data loader script
# RUN chmod +x /cse511/data_loader.py && \
#     neo4j start && \
#     python3 data_loader.py && \
#     neo4j stop

# Expose neo4j ports
EXPOSE 7474 7687

# # Start neo4j service and show the logs on container run
# CMD ["/bin/bash", "-c", "neo4j start && tail -f /dev/null"]

# required to scratch start of server
RUN rm -rf     /var/lib/neo4j/data/*     /var/lib/neo4j/logs/*     /var/lib/neo4j/run/*     /var/lib/neo4j/import/*     /var/lib/neo4j/transactions/*     /var/log/neo4j/*


# Start neo4j, wait for it to be ready, then run data loader, run tester and ouput to logs
CMD ["/bin/bash", "-c", "\
    neo4j-admin dbms set-initial-password project1phase1 && \
    neo4j start && \
    echo 'Waiting for Neo4j to start' && \
    sleep 20 && \
    mkdir -p /app/logs && \
    python3 /app/Project-1-zyesposs/scripts/data_loader.py > /app/logs/data_loader.log 2>&1 && \
    sleep 10 && \
    python3 /app/Project-1-zyesposs/scripts/tester.py > /app/logs/tester.log 2>&1 && \
    tail -f /dev/null"]


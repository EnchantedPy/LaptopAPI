ARG ELASTIC_VERSION

# https://www.docker.elastic.co/
FROM docker.elastic.co/logstash/logstash:${ELASTIC_VERSION:-8.13.4}

# Add your logstash plugins setup here
# Example: RUN logstash-plugin install logstash-filter-json
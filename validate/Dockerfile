# Use a Debian-based image as the base
FROM debian:bookworm

# Install system dependencies
RUN apt update && \
    apt install -y \
        make \
        zip \
        curl \
        unzip \
        openjdk-17-jdk

# Install Jena (Apache Jena 5.2.0)
RUN mkdir -p /jena && \
    curl -L https://archive.apache.org/dist/jena/binaries/apache-jena-5.2.0.zip -o /jena/jena.zip && \
    unzip /jena/jena.zip -d /jena && \
    rm /jena/jena.zip && \
    ln -s /jena/apache-jena-5.2.0/bin/riot /usr/local/bin/riot && \
    ln -s /jena/apache-jena-5.2.0/bin/qparse /usr/local/bin/qparse

# Set environment variables
ENV PATH="/usr/local/bin:$PATH"

# Add shapes refreshement sctipt
COPY refresh-shapes.sh /refresh-shapes.sh
RUN chmod +x /refresh-shapes.sh
COPY drop.ru /drop.ru
COPY Makefile /Makefile
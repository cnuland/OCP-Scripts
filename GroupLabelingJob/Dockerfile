FROM ubi8:latest

USER 0
RUN mkdir /app
ENV HOME=/app
WORKDIR /app
ADD group-label.py ./
RUN rm /etc/rhsm-host && \
    chmod 775 /app && \
    yum repolist > /dev/null && \
    yum update -y && \
    yum install -y python3 && \
    pip3 install requests

USER 1001
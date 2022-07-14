FROM nginx:1.14.2-alpine

# setup gateway configurations
COPY conf/gateway/backend-nginx.conf /etc/nginx/conf.d/
COPY conf/gateway/amq-nginx.conf /etc/nginx/tcpconf.d/

# setup directory for volume mount
RUN echo "include /etc/nginx/tcpconf.d/*.conf;" >> /etc/nginx/nginx.conf \
    && mkdir /opt/static-content/
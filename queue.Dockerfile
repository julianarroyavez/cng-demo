FROM rmohr/activemq:5.15.9-alpine

# setup configurations
COPY conf/queue/* conf/

# declare exposed ports
# PORTAL UI
EXPOSE 8161
# JMS
EXPOSE 61616
# AMQP
#EXPOSE 5672
# STOMP
EXPOSE 61613
# MQTT
EXPOSE 1883
# WS
#EXPOSE 61614
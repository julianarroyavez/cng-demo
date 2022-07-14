## Build images commands:
1. build server image
docker build -t hygge-ev-backend-server:{ver-no} --build-arg APP_ENV=prod /path/to/Dockerfile

2. build gateway image
docker build -t hygge-ev-platform:latest /path/to/Dockerfile

3. build queue image
docker build -t hygge-ev-queue:latest /path/to/Dockerfile

4. build sms image
docker build -t sms-listener:latest /path/to/Dockerfile

5. build notification images
docker build -t notification-alert:latest /path/to/Dockerfile
docker build -t notification-event:latest /path/to/Dockerfile


## Docker run commands:

1. Run docker for NGINX:
    docker run -d --network="host" -v /etc/ssl/:/etc/ssl/ -v /home/hygge-ev-user/hygge-ev-static-content/:/home/hygge-ev-user/hygge-ev-static-content/ hygge-ev-platform:latest

2. Run docker for ActiveMQ:
    docker run -p 61616:61616 -p 8161:8161 -p 61613:61613 -p 1883:1883 -d hygge-ev-queue:latest

3. Run docker for Application:
    docker run -d -v /home/hygge-ev-user/application/log/:/application/hygge-ev-backend-python/log/ --net=host -p 8080:8080 hygge-ev-backend-server:latest

4. Run docker for SMS listener:
    docker run -d -v /home/hygge-ev-user/sms-connector/log/:/mqtt-listener/hygge-ev-sms-connector/log/ --net=host sms-listener:latest

5. Run docker for Notification Events:
    docker run -d -v /home/hygge-ev-user/notification-connector/log/alert/:/mqtt-listener/hygge-ev-backend-notification-connector/log/ --net=host notification-alert:latest

6. Run docker for Notification Alerts:
    docker run -d -v /home/hygge-ev-user/notification-connector/log/event/:/mqtt-listener/hygge-ev-backend-notification-connector/log/ --net=host notification-event:latest
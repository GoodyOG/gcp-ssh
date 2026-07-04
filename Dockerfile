FROM teddysun/xray:latest

EXPOSE 8080

COPY config.json /etc/xray/config.json

CMD ["xray", "run", "-config", "/etc/xray/config.json"]

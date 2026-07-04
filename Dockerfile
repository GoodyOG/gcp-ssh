FROM alpine:latest

RUN apk add --no-cache dropbear python3

# ===== SSH CREDENTIALS - EDIT BEFORE PUSH =====
RUN echo 'root:MyRootPass1' | chpasswd && \
    adduser -D admin && \
    echo 'admin:MyAdminPass1' | chpasswd
# ===============================================

COPY proxy.py /proxy.py

# Dropbear on port 109 (internal), proxy.py listens on $PORT
CMD dropbear -R -p 109 -B -w && python3 /proxy.py

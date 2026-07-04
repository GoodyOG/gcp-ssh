import os, socket, threading, select

PORT = int(os.environ.get("PORT", 8080))
SSH_PORT = 109

RESP_101 = b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n\r\n"
RESP_200 = b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"

def handle(client):
    srv = None
    try:
        req = client.recv(4096)
        if not req:
            return

        req_clean = req.lower().replace(b" ", b"")

        # Health check — respond 200, don't forward to SSH
        if b"upgrade:websocket" not in req_clean:
            client.sendall(RESP_200)
            # If it's Cloud Run's startup probe (GET /), just respond and close
            return

        # WebSocket upgrade — forward to Dropbear
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.connect(("127.0.0.1", SSH_PORT))
        client.sendall(RESP_101)

        while True:
            r, _, _ = select.select([client, srv], [], [])
            if client in r:
                d = client.recv(4096)
                if not d: break
                srv.send(d)
            if srv in r:
                d = srv.recv(4096)
                if not d: break
                client.send(d)
    except:
        pass
    finally:
        client.close()
        if srv:
            srv.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", PORT))
s.listen(200)
while True:
    c, _ = s.accept()
    threading.Thread(target=handle, args=(c,)).start()

import os, socket, threading, select, hashlib, base64

PORT = int(os.environ.get("PORT", 8080))
SSH_PORT = 109
WS_MAGIC = b"258EAFA5-E914-47DA-95CA-5AB6DC11B85"

RESP_200 = b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: keep-alive\r\n\r\nOK"

def parse_headers(data):
    """Parse HTTP headers from request"""
    lines = data.split(b"\r\n")
    if not lines:
        return {}
    headers = {}
    for line in lines[1:]:
        if b":" in line:
            key, val = line.split(b":", 1)
            headers[key.strip().lower()] = val.strip()
    return headers

def handle(client):
    srv = None
    try:
        req = client.recv(4096)
        if not req:
            return

        headers = parse_headers(req)

        # Check if it's a WebSocket upgrade
        upgrade = headers.get(b"upgrade", b"").lower()
        conn = headers.get(b"connection", b"").lower()
        ws_key = headers.get(b"sec-websocket-key", b"")

        is_ws = b"websocket" in upgrade or b"websocket" in conn or b"upgrade" in conn

        if not is_ws:
            # Health check - respond 200
            client.sendall(RESP_200)
            return

        # WebSocket upgrade - compute accept key
        accept_key = base64.b64encode(
            hashlib.sha1(ws_key + WS_MAGIC).digest()
        )

        resp = (
            b"HTTP/1.1 101 Switching Protocols\r\n"
            b"Upgrade: websocket\r\n"
            b"Connection: Upgrade\r\n"
            b"Sec-WebSocket-Accept: " + accept_key + b"\r\n"
            b"\r\n"
        )
        client.sendall(resp)

        # Forward to Dropbear
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.connect(("127.0.0.1", SSH_PORT))

        # Bidirectional forwarding
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

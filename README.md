# gcp-ssh — SSH over WebSocket on Cloud Run

SSH through Cloud Run using WebSocket tunnelling. Works inside Skills Boost labs (or any temporary GCP project). Deploy and connect in 2 minutes.

## 🔧 What's in the box

| File | Purpose |
|---|---|
| `Dockerfile` | Alpine + Dropbear SSH + Python |
| `proxy.py` | WebSocket-to-TCP bridge, listens on `$PORT` |

## 🚀 Deploy

1. Go to **Cloud Run** → **Create Service**
2. Source: **Continuously deploy from source** → pick this repo
3. **Timeout**: set to **3600** (max 60 min)
4. **Min instances**: **1** (keeps container warm)
5. Deploy

## 🔑 Credentials

| User | Password |
|---|---|
| `root` | `MyRootPass1` |
| `admin` | `MyAdminPass1` |

Edit these in `Dockerfile` before pushing.

## 📡 Connect

```bash
# Install wstunnel (one-time)
npm install -g wstunnel

# Tunnel SSH through Cloud Run
wstunnel client -L 2222:localhost:22 wss://YOUR_CLOUD_RUN_URL

# SSH through the tunnel (separate terminal)
ssh admin@localhost -p 2222
```

One-liner:
```bash
wstunnel client -L 2222:localhost:22 wss://YOUR_CLOUD_RUN_URL & sleep 1 && ssh admin@localhost -p 2222
```

## ⏱️ 60-min timeout

Cloud Run kills requests at 60 min (hard limit). SSH drops. Just re-run the `wstunnel` + `ssh` command. For a 5-hour lab, that's at most 5 reconnects.

## 📦 Client dependencies

- `wstunnel` — wraps SSH in WebSocket (`npm install -g wstunnel`)
- SSH client (comes with every OS)

## 🧱 How it works

```
Client → wstunnel → WebSocket → Cloud Run $PORT → proxy.py → Dropbear:109 → SSH
```

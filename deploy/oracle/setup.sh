#!/usr/bin/env bash
# Oracle Cloud Always Free (Ampere A1 / Ubuntu) one-shot setup.
# Run on the VM as your normal user. It is idempotent: just re-run it.
set -euo pipefail

REPO="https://github.com/Xvbgf467/Ai-Job-Search.git"
DIR="Ai-Job-Search"
PORT="${PORT:-7860}"

echo "==> Docker"
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
  sudo systemctl enable --now docker
  sudo usermod -aG docker "$USER"
  echo "Docker installed. Run:  newgrp docker   (or log out and back in), then re-run this script."
  exit 0
fi

echo "==> Code"
if [ -d "$DIR" ]; then
  cd "$DIR" && git pull --rebase
else
  git clone "$REPO" && cd "$DIR"
fi

echo "==> LLM key"
if ! grep -qE "^LLM_API_KEY=.+" .env 2>/dev/null; then
  [ -f .env ] || cp .env.example .env
  echo "Edit  $(pwd)/.env  and set LLM_API_KEY=<your Z.AI key>, then re-run this script."
  exit 0
fi

echo "==> OS firewall (iptables) for port $PORT"
sudo iptables -C INPUT -p tcp --dport "$PORT" -j ACCEPT 2>/dev/null \
  || sudo iptables -I INPUT -p tcp --dport "$PORT" -j ACCEPT
if command -v netfilter-persistent >/dev/null 2>&1; then
  sudo netfilter-persistent save
elif [ -d /etc/iptables ]; then
  sudo iptables-save | sudo tee /etc/iptables/rules.v4 >/dev/null
fi

echo "==> Build & start (first run downloads PyTorch + the model, ~5-10 min)"
docker compose up -d --build

echo
IP="$(curl -s -m 5 ifconfig.me || hostname -I | awk '{print $1}')"
echo "==> App:   http://$IP:$PORT"
echo "==> Health: http://$IP:$PORT/health"
echo "==> Logs:   docker compose logs -f"
echo
echo "If the URL is unreachable, open port $PORT in the OCI VCN Security List"
echo "(Networking > Virtual Cloud Network > Security Lists > Ingress, 0.0.0.0/0 TCP $PORT)."

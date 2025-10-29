#!/usr/bin/env bash
set -euo pipefail

# Usage: ./sonos_scan.sh 192.168.1.0/24
CIDR="${1:-}"
if [[ -z "$CIDR" ]]; then
  echo "Usage: $0 <CIDR, e.g. 192.168.1.0/24>"; exit 1
fi

which nmap >/dev/null 2>&1 || { echo "nmap is required"; exit 1; }
which curl >/dev/null 2>&1 || { echo "curl is required"; exit 1; }

echo "[*] Scanning $CIDR for ports 1400,1443..."
# -Pn чтобы не терять устройства при ICMP-блоке, --open только открытые
mapfile -t HOSTS < <(nmap -n -Pn -p 1400,1443 --open --min-rate 1000 "$CIDR" \
  | awk '/Nmap scan report/{ip=$NF} /open/{print ip}' | sort -u)

if [[ ${#HOSTS[@]} -eq 0 ]]; then
  echo "[-] No hosts with 1400/1443 open found."; exit 1
fi

echo "[*] Checking device descriptions..."
printf "%-16s | %-25s | %s\n" "IP" "RoomName" "Model"
printf -- "-----------------+---------------------------+-----------------------------\n"

for ip in "${HOSTS[@]}"; do
  # Пытаемся по HTTP (классика), если нет — пробуем HTTPS:1443
  DESC_HTTP=$(curl -m 2 -fs "http://$ip:1400/xml/device_description.xml" || true)
  if [[ -z "$DESC_HTTP" ]]; then
    DESC_HTTP=$(curl -m 3 -kfs "https://$ip:1443/xml/device_description.xml" || true)
  fi

  if [[ -n "$DESC_HTTP" ]] && echo "$DESC_HTTP" | grep -qi "<manufacturer>Sonos</manufacturer>"; then
    ROOM=$(echo "$DESC_HTTP"  | sed -n 's:.*<roomName>\(.*\)</roomName>.*:\1:ip' | head -n1)
    MODEL=$(echo "$DESC_HTTP" | sed -n 's:.*<modelName>\(.*\)</modelName>.*:\1:ip' | head -n1)
    printf "%-16s | %-25s | %s\n" "$ip" "${ROOM:-?}" "${MODEL:-?}"
  fi
done

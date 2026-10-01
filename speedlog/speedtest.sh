#!/usr/bin/env bash
# Hourly internet speed log. Appends one CSV row per run to data/speed.csv.
# Uses ~450 MB per run (~11 GB/day). Stops by itself after STOP_AFTER.
set -u
STOP_AFTER="2026-10-04 16:00"
DIR="$(cd "$(dirname "$0")" && pwd)"
CSV="$DIR/data/speed.csv"
URL_DOWN="http://lax-ca-us-ping.vultr.com/vultr.com.100MB.bin"
URL_UP="https://speed.cloudflare.com/__up"

[ "$(date +%s)" -lt "$(date -d "$STOP_AFTER" +%s)" ] || exit 0
exec 9>"$DIR/data/.lock"; flock -n 9 || exit 0
[ -f "$CSV" ] || echo "time,route,down_1_mbps,down_4_mbps,up_mbps,ping_ms" > "$CSV"

now() { date +%s.%N; }
down() { # streams
  local s e tmp; tmp=$(mktemp -d); s=$(now)
  for i in $(seq 1 "$1"); do curl -s -o /dev/null -m 30 -w "%{size_download}\n" "$URL_DOWN" > "$tmp/$i" & done; wait
  e=$(now); cat "$tmp"/* | awk -v s="$s" -v e="$e" "{t+=\$1} END {printf \"%.0f\", t*8/(e-s)/1e6}"; rm -rf "$tmp"
}
up() { head -c 30000000 /dev/zero | curl -s -o /dev/null -m 40 -w "%{speed_upload}" --data-binary @- "$URL_UP" | awk "{printf \"%.0f\", \$1*8/1e6}"; }
ping_ms() { ping -c5 -q 1.1.1.1 2>/dev/null | awk -F/ "/rtt/ {printf \"%.1f\", \$5}"; }

route=$(ip route show default | awk "NR==1 {print \$5}")
echo "$(date -Iseconds),$route,$(down 1),$(down 4),$(up),$(ping_ms)" >> "$CSV"

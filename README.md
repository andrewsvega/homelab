# homelab

Turning old hardware into a self-hosted homelab for network security, media, photo storage, and learning Linux.

## Hardware

| Host | Hardware | Role |
|---|---|---|
| `droo-hp` | HP 15-bs015dx, i5-7200U, 8 GB, 240 GB SSD, Ubuntu 26.04 LTS | Lab box / Docker host |
| `droo-srv` | Chuwi HeroBox mini PC | Always-on services (Proxmox), planned |
| Router | TP-Link Archer AX21 v4.6 | Main router (OpenWrt planned) |

## Network

| Range | Use |
|---|---|
| `.1` | Router |
| `.10–.19` | Servers (`droo-srv` = `.10`) |
| `.20–.29` | Lab (`droo-hp` = `.20`) |
| `.100+` | DHCP pool |

Remote access via Tailscale. SSH is key-only, and ufw allows SSH inbound only.

## Services

| Service | Host | Port | Purpose |
|---|---|---|---|
| [Uptime Kuma](uptime-kuma/) | droo-hp | 3001 | Uptime monitoring |
| [AdGuard Home](adguard/) | droo-hp | 53, 3000 | DNS ad/tracker blocking, encrypted upstream (DoH/DoT) |
| [Immich](immich/) | droo-hp | 2283 | Photo/video backup; library on `/data/photos`, DB on SSD |

## System config (`system/droo-hp/`)

| File | Location | Why |
|---|---|---|
| `00-hardening.conf` | `/etc/ssh/sshd_config.d/` | Disable password and root SSH login |
| `wifi-powersave-off.conf` | `/etc/NetworkManager/conf.d/` | Wi-Fi power save caused ~79 ms ping; now ~9 ms |
| `lid.conf` | `/etc/systemd/logind.conf.d/` | Keep running with the lid closed |
| `90-hp-lid-wlan.hwdb` | `/etc/udev/hwdb.d/` | Firmware sends `KEY_WLAN` (scancode `d7`) on lid open and triggers airplane mode. Remapped to `reserved`. |
| `98-arp-per-nic.conf` | `/etc/sysctl.d/` | Each NIC answers ARP only for its own IP. Stops Wi-Fi from claiming the Ethernet address (.20). |

## Troubleshooting log

- **Airplane mode on lid open:** traced with `journalctl`, `libinput debug-events`, and `evtest` to scancode `d7` on the AT keyboard. Fixed with an hwdb remap.
- **Slow Wi-Fi (~8 Mbps):** RTL8723DE is 2.4 GHz / 802.11n only. The router was on overlapping channel 3; moving to channel 6 at 20 MHz brought it to ~33 Mbps (card ceiling). Ethernet planned.
- **Ethernet unused, everything on Wi-Fi:** `eno1` had .20 but no routes; NetworkManager kept falling back to Wi-Fi. Cause was ARP flux: Wi-Fi answered ARP for .20, so the router sent .20 replies to the Wi-Fi card and the connectivity check on `eno1` failed (+20000 metric penalty). Fixed with `ipv4.route-metric 100` on `netplan-eno1` and `98-arp-per-nic.conf`. Internet went from ~40/23 to ~545/185 Mbps.
- **Internet capped at ~550 Mbps on a 1 Gbps plan:** same cap from every server, on the HP (Ethernet) and the Mac (Wi-Fi), so not the HP. Toggling QoS on the AX21 and saving cleared it; QoS on vs. off made no difference afterwards, so QoS stays off. Now ~800–870 down / ~500 up (Vultr LA, 4 streams). Cause unknown (router state or ISP load). [`speedlog/`](speedlog/) logs hourly until 2026-10-04 to catch it if it returns.

## Roadmap

- [ ] AdGuard Home, Jellyfin, Immich, RomM
- [ ] Proxmox on `droo-srv`
- [ ] 3-2-1 photo backups
- [ ] OpenWrt on the AX21

## AdGuard settings (live in web UI, not in repo)
- Upstreams (load-balanced): `https://security.cloudflare-dns.com/dns-query`, `tls://dns.quad9.net`, both malware-filtering
- AdGuard browsing security web service: ON
- Blocklists: AdGuard DNS filter, HaGeZi Threat Intelligence Feeds

## Whole-house DNS (router DHCP → AdGuard)
- AX21 DHCP hands out DNS 192.168.0.20 (primary) / .21 (secondary, same HP via Wi-Fi)
- HP itself uses 1.1.1.1 / 9.9.9.9 (not its own AdGuard)
- **Emergency rollback:** 192.168.0.1 → Advanced → Network → DHCP Server → clear DNS fields → Save → reconnect devices

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

## System config (`system/droo-hp/`)

| File | Location | Why |
|---|---|---|
| `00-hardening.conf` | `/etc/ssh/sshd_config.d/` | Disable password and root SSH login |
| `wifi-powersave-off.conf` | `/etc/NetworkManager/conf.d/` | Wi-Fi power save caused ~79 ms ping; now ~9 ms |
| `lid.conf` | `/etc/systemd/logind.conf.d/` | Keep running with the lid closed |
| `90-hp-lid-wlan.hwdb` | `/etc/udev/hwdb.d/` | Firmware sends `KEY_WLAN` (scancode `d7`) on lid open and triggers airplane mode. Remapped to `reserved`. |

## Troubleshooting log

- **Airplane mode on lid open:** traced with `journalctl`, `libinput debug-events`, and `evtest` to scancode `d7` on the AT keyboard. Fixed with an hwdb remap.
- **Slow Wi-Fi (~8 Mbps):** RTL8723DE is 2.4 GHz / 802.11n only. The router was on overlapping channel 3; moving to channel 6 at 20 MHz brought it to ~33 Mbps (card ceiling). Ethernet planned.

## Roadmap

- [ ] AdGuard Home, Jellyfin, Immich, RomM
- [ ] Proxmox on `droo-srv`
- [ ] 3-2-1 photo backups
- [ ] OpenWrt on the AX21

#!/usr/bin/env python3
"""Build an iptv-org/epg channels.xml from the tvg-ids in an M3U playlist."""
import collections, json, re, sys, urllib.request
from xml.sax.saxutils import escape, quoteattr

M3U, OUT = sys.argv[1], sys.argv[2]
GUIDES_URL = "https://iptv-org.github.io/api/guides.json"
SKIP = {"tvtv.us"}  # returning 404 as of 2026-09-29
PREFERRED = ["tvguide.com", "pluto.tv", "plex.tv", "tvpassport.com"]

ids = {}
for line in open(M3U, encoding="utf-8"):
    if line.startswith("#EXTINF"):
        m = re.search(r'tvg-id="([^"]+)"', line)
        if m:
            ids.setdefault(m.group(1), line.rsplit(",", 1)[-1].strip())

guides = json.load(urllib.request.urlopen(GUIDES_URL))
by_channel = collections.defaultdict(list)
for g in guides:
    if g.get("channel") and g["site"] not in SKIP:
        by_channel[g["channel"]].append(g)

def rank(g, feed):
    feed_score = 0 if g.get("feed") == feed else (1 if not g.get("feed") else 2)
    lang_score = 0 if g.get("lang") == "en" else 1
    site_score = PREFERRED.index(g["site"]) if g["site"] in PREFERRED else len(PREFERRED)
    return (feed_score, lang_score, site_score)

rows, sites, missing = [], collections.Counter(), 0
for tvg_id, name in ids.items():
    channel, _, feed = tvg_id.partition("@")
    options = by_channel.get(channel)
    if not options:
        missing += 1
        continue
    g = min(options, key=lambda x: rank(x, feed))
    sites[g["site"]] += 1
    rows.append(f'  <channel site={quoteattr(g["site"])} lang={quoteattr(g.get("lang") or "en")} '
                f'xmltv_id={quoteattr(tvg_id)} site_id={quoteattr(g["site_id"])}>{escape(name)}</channel>')

with open(OUT, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<channels>\n' + "\n".join(rows) + "\n</channels>\n")

print(f"{len(ids)} channels with tvg-id | {len(rows)} matched a guide source | {missing} have no guide")
for site, n in sites.most_common():
    print(f"  {n:4}  {site}")

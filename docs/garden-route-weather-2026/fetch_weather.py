#!/usr/bin/env python3
"""Fetch multi-source forecasts for Garden Route spots and write weather-data.js.

Sources: Open-Meteo deterministic models (ECMWF IFS, ECMWF AIFS, GFS, ICON,
UK Met Office, GEM, JMA), ECMWF 51-member ensemble, MET Norway (yr.no),
Open-Meteo marine (wave height). Re-run to refresh: python3 fetch_weather.py
"""
import json
import statistics
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

START, END = "2026-09-24", "2026-09-27"
DAYS = ["2026-09-24", "2026-09-25", "2026-09-26", "2026-09-27"]
SLOTS = {"AM": range(7, 13), "PM": range(13, 19)}  # local hours (SAST)
MODELS = ["ecmwf_ifs025", "ecmwf_aifs025_single", "gfs_seamless", "icon_seamless",
          "ukmo_seamless", "gem_seamless", "jma_seamless"]
MODEL_LABEL = {"ecmwf_ifs025": "ECMWF", "ecmwf_aifs025_single": "ECMWF-AI",
               "gfs_seamless": "GFS", "icon_seamless": "ICON", "ukmo_seamless": "UKMO",
               "gem_seamless": "GEM", "jma_seamless": "JMA", "yr": "yr.no"}
UA = "personal-travel/1.0 (trip weather check)"

# kind: beach | coast-hike | forest | inland | pass | indoor | wildlife | town
# exposed: wind matters more (cliff/peninsula/sea); marine: fetch wave height
SPOTS = [
    ("CT", "Cape Town", -33.92, 18.42, "town", False, False, "Departure/return city; CPT⇄GRJ flights"),
    ("MB", "Mossel Bay", -34.18, 22.14, "beach", True, True, "St Blaize trail, Point, Dias museum"),
    ("GE", "George (GRJ airport)", -33.96, 22.46, "town", False, False, "Airport; Outeniqua foothills"),
    ("WI", "Wilderness", -33.99, 22.58, "beach", True, True, "Beach, Map of Africa, Kingfisher trail, lagoon"),
    ("SE", "Sedgefield", -34.02, 22.80, "beach", True, True, "Gericke's Point, Saturday Wild Oats market"),
    ("KN", "Knysna Heads", -34.08, 23.06, "coast-hike", True, True, "Heads viewpoint, Featherbed, lagoon boats"),
    ("KF", "Knysna Forest (Diepwalle)", -33.95, 23.16, "forest", False, False, "Elephant walk, Big Tree — sheltered in wind"),
    ("PB", "Plettenberg Bay", -34.05, 23.37, "beach", True, True, "Base; Central/Lookout beach, whale boats"),
    ("RO", "Robberg Peninsula", -34.10, 23.40, "coast-hike", True, True, "Peninsula loop — rock scrambles, closes in bad weather"),
    ("NV", "Nature's Valley", -33.98, 23.56, "beach", True, True, "Lagoon beach, Salt River mouth walk"),
    ("SR", "Storms River Mouth (Tsitsikamma)", -34.02, 23.90, "coast-hike", True, True, "Suspension bridge, Waterfall trail"),
    ("BK", "Bloukrans Bridge", -33.97, 23.65, "pass", True, False, "Bungee — cancelled in high wind/lightning"),
    ("JB", "Jeffreys Bay", -34.05, 24.92, "beach", True, True, "Supertubes surf"),
    ("AD", "Addo Elephant Park", -33.44, 25.75, "wildlife", False, False, "Self-drive safari (~3h from Plett)"),
    ("UN", "Uniondale / Prince Alfred Pass", -33.66, 23.12, "pass", False, False, "Gravel pass N of Knysna — avoid after heavy rain"),
    ("DR", "De Rust / Meiringspoort", -33.49, 22.53, "inland", False, False, "Tarred gorge drive, waterfall — rain-shadow side"),
    ("OU", "Oudtshoorn / Cango Caves", -33.59, 22.20, "indoor", False, False, "Caves (indoor), ostrich farms — rain-shadow"),
    ("PA", "Prince Albert / Swartberg Pass", -33.22, 22.03, "pass", False, False, "Gravel pass — dramatic, avoid in rain/snow"),
    ("CD", "Calitzdorp (Route 62)", -33.53, 21.69, "inland", False, False, "Port-wine farms, Route 62 — usually dry"),
]


def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001 — retry any network error
            if i == tries - 1:
                raise
            time.sleep(2 ** (i + 1))


def open_meteo_models():
    lats = ",".join(str(s[2]) for s in SPOTS)
    lons = ",".join(str(s[3]) for s in SPOTS)
    url = ("https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s"
           "&hourly=precipitation,precipitation_probability,weather_code,wind_gusts_10m,"
           "wind_speed_10m,wind_direction_10m,temperature_2m,cloud_cover"
           "&models=%s&timezone=Africa/Johannesburg&start_date=%s&end_date=%s"
           % (lats, lons, ",".join(MODELS), START, END))
    data = get(url)
    return data if isinstance(data, list) else [data]


def ensemble():
    lats = ",".join(str(s[2]) for s in SPOTS)
    lons = ",".join(str(s[3]) for s in SPOTS)
    url = ("https://ensemble-api.open-meteo.com/v1/ensemble?latitude=%s&longitude=%s"
           "&daily=precipitation_sum,wind_gusts_10m_max&models=ecmwf_ifs025"
           "&timezone=Africa/Johannesburg&start_date=%s&end_date=%s" % (lats, lons, START, END))
    data = get(url)
    return data if isinstance(data, list) else [data]


def marine():
    out = {}
    for s in SPOTS:
        if not s[6]:
            continue
        url = ("https://marine-api.open-meteo.com/v1/marine?latitude=%s&longitude=%s"
               "&hourly=wave_height&timezone=Africa/Johannesburg&start_date=%s&end_date=%s"
               % (s[2], s[3], START, END))
        try:
            d = get(url)
            out[s[0]] = dict(zip(d["hourly"]["time"], d["hourly"]["wave_height"]))
        except Exception:  # noqa: BLE001 — marine is optional context
            out[s[0]] = {}
    return out


def yr(lat, lon):
    d = get("https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=%.2f&lon=%.2f" % (lat, lon))
    hours = {}
    for ts in d["properties"]["timeseries"]:
        t = datetime.fromisoformat(ts["time"].replace("Z", "+00:00")) + timedelta(hours=2)
        det = ts["data"]["instant"]["details"]
        rain = None
        if "next_1_hours" in ts["data"]:
            rain = ts["data"]["next_1_hours"]["details"].get("precipitation_amount")
        elif "next_6_hours" in ts["data"]:
            rain = ts["data"]["next_6_hours"]["details"].get("precipitation_amount", 0) / 6
        hours[t.strftime("%Y-%m-%dT%H:00")] = {
            "rain": rain, "gust": det.get("wind_speed", 0) * 3.6 * 1.5,  # compact API has no gust; ~1.5× mean
            "temp": det.get("air_temperature")}
    # 6-hourly steps: spread to fill each hour so window sums work
    filled = {}
    keys = sorted(hours)
    for i, k in enumerate(keys):
        filled[k] = hours[k]
        t = datetime.fromisoformat(k)
        nxt = datetime.fromisoformat(keys[i + 1]) if i + 1 < len(keys) else t
        step = int((nxt - t).total_seconds() // 3600)
        for h in range(1, step):
            filled[(t + timedelta(hours=h)).strftime("%Y-%m-%dT%H:00")] = hours[k]
    return filled


def window(series_time, series, day, hrs):
    idx = {t: i for i, t in enumerate(series_time)}
    vals = []
    for h in hrs:
        k = "%sT%02d:00" % (day, h)
        if k in idx and series[idx[k]] is not None:
            vals.append(series[idx[k]])
    return vals


def main():
    om = open_meteo_models()
    ens = ensemble()
    sea = marine()
    out = {"fetched": datetime.now(timezone.utc).isoformat(timespec="minutes"),
           "days": DAYS, "slots": list(SLOTS), "spots": []}
    for n, s in enumerate(SPOTS):
        code, name, lat, lon, kind, exposed, is_marine, note = s
        h = om[n]["hourly"]
        yrd = {}
        try:
            yrd = yr(lat, lon)
        except Exception:  # noqa: BLE001 — yr optional
            pass
        e = ens[n]["daily"]
        spot = {"code": code, "name": name, "lat": lat, "lon": lon, "kind": kind,
                "exposed": exposed, "note": note, "days": {}}
        for di, day in enumerate(DAYS):
            members_r = [v[di] for k, v in e.items() if k.startswith("precipitation_sum") and v[di] is not None]
            members_g = [v[di] for k, v in e.items() if k.startswith("wind_gusts") and v[di] is not None]
            dayrec = {"ens": {
                "rain_med": round(statistics.median(members_r), 1) if members_r else None,
                "p10": round(100 * sum(r > 10 for r in members_r) / len(members_r)) if members_r else None,
                "p25": round(100 * sum(r > 25 for r in members_r) / len(members_r)) if members_r else None,
                "g60": round(100 * sum(g > 60 for g in members_g) / len(members_g)) if members_g else None,
            }, "slots": {}}
            for slot, hrs in SLOTS.items():
                per = {}
                for m in MODELS:
                    rain = window(h["time"], h.get("precipitation_" + m, []), day, hrs)
                    if not rain:
                        continue
                    gust = window(h["time"], h.get("wind_gusts_10m_" + m, []), day, hrs)
                    temp = window(h["time"], h.get("temperature_2m_" + m, []), day, hrs)
                    wc = window(h["time"], h.get("weather_code_" + m, []), day, hrs)
                    pp = window(h["time"], h.get("precipitation_probability_" + m, []), day, hrs)
                    wd = window(h["time"], h.get("wind_direction_10m_" + m, []), day, hrs)
                    per[MODEL_LABEL[m]] = {
                        "rain": round(sum(rain), 1),
                        "gust": round(max(gust)) if gust else None,
                        "tmax": round(max(temp)) if temp else None,
                        "tmin": round(min(temp)) if temp else None,
                        "thunder": any(c >= 95 for c in wc),
                        "pop": max(pp) if pp else None,
                        "wdir": round(statistics.median(wd)) if wd else None,
                    }
                yr_vals = [yrd.get("%sT%02d:00" % (day, hh)) for hh in hrs]
                yr_vals = [v for v in yr_vals if v and v["rain"] is not None]
                if yr_vals:
                    per["yr.no"] = {"rain": round(sum(v["rain"] for v in yr_vals), 1),
                                    "gust": None,
                                    "tmax": round(max(v["temp"] for v in yr_vals)),
                                    "tmin": round(min(v["temp"] for v in yr_vals)),
                                    "thunder": False, "pop": None, "wdir": None}
                waves = [sea.get(code, {}).get("%sT%02d:00" % (day, hh)) for hh in hrs]
                waves = [w for w in waves if w is not None]
                dayrec["slots"][slot] = {"models": per,
                                         "wave": round(max(waves), 1) if waves else None}
            spot["days"][day] = dayrec
        out["spots"].append(spot)
    path = Path(__file__).with_name("weather-data.js")
    path.write_text("window.WEATHER = " + json.dumps(out, indent=1) + ";\n")
    print("wrote", path, "spots", len(out["spots"]))


if __name__ == "__main__":
    main()

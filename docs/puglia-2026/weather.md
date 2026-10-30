# Puglia weather for Sat 31 Oct to Sun 8 Nov 2026

Pulled **Fri 30 Oct 2026**. Sources:
- Open-Meteo deterministic forecast.
- ECMWF IFS 51-member ensemble.
- Open-Meteo marine (sea temperature, waves).
- ERA5 climatology for 31 Oct–8 Nov, 2006–2025.

Script: scratchpad `eu/pug.py`, `pugan.py`, `pugclim.py`.

## Bottom line

**This is a poor week for Puglia.** A Mediterranean low sits over the south of Italy for the first four days.
- **Sat 31 Oct:** rain all day in the north (Bari, Polignano, Ostuni): 22–26 mm, thunderstorms, about 0 h sun. **100% of ensemble members show rain.** Salento (Lecce, Gallipoli, Leuca) is drier and sunnier.
- **Sun 1:** a showery break with 5–8 h sun. 84–98% of members show rain.
- **Mon 2:** **the worst day everywhere.**
  - 20–53 mm of rain and thunderstorms.
  - E/SE gusts of 55–74 km/h, with 2 m waves on the coast.
  - 100% of members show rain; 88–98% show more than 5 mm.
- **Tue 3:** still wet in the north (12–15 mm at Bari and Polignano). Salento clears to about 7–9 h sun.
- **Wed 4 and Thu 5:** **the only reliable days.** Sunny (9–10 h), dry (0–10% of members show rain) and calm, 16–19 °C.
- **Fri 6 to Sun 8:** uncertain, with 20–33% of members showing rain. The deterministic run brings another wet spell to Salento on Sat 7 and Sun 8 (Gallipoli 20 mm, Leuca 27 mm), with grey skies in the north.
- **Temperatures:** **highs of 14–19 °C**, which is 1–4 °C below the 20-year normal. Lows are 9–15 °C, and inland at Alberobello and Matera only 5–9 °C.
- **Sea:** 19.5–20 °C. Swimmable for the brave, but not with these air temperatures.

## Live, by area (high °C / rain mm / ensemble rain ≥1 mm / sun h)

| Day | Bari / Polignano | Ostuni / Valle d'Itria | Lecce | Gallipoli / Leuca (Salento) |
|---|---|---|---|---|
| Sat 31 | 16 / 22–26 / 100% / 0 h | 15 / 24 / 100% / 1 h | 18 / 5 / 100% / 8 h | 18 / 0 / 98% / 9 h |
| Sun 1 | 16 / 1–5 / 95% / 6–8 h | 15 / 7 / 98% / 5 h | 17 / 0 / 94% / 6 h | 17–18 / 0 / 86–94% / 5–6 h |
| **Mon 2** | 16 / **46–53** / 100% / 0 h, gust 69–74 | 14 / **36** / 100% / 0 h | 16 / **24** / 100% / 0 h | 17–18 / **21–23** / 100% / 0 h |
| Tue 3 | 15–16 / 12–15 / 96–98% / 0 h | 14 / 3 / 96% / 1 h | 17 / 0 / 88% / 7 h | 18 / 0 / 84–88% / 9 h |
| **Wed 4** | 17–18 / 0 / 29–33% / **9–10 h** | 16 / 0 / 14% / **10 h** | 18 / 0 / 8% / **9 h** | 18–19 / 0 / 10% / **10 h** |
| **Thu 5** | 18 / 0 / 24–27% / **9 h** | 18 / 0 / 33% / **9 h** | 19 / 0 / 10% / **9 h** | 18–19 / 0 / 6–18% / **9 h** |
| Fri 6 | 19 / 0–1 / 29–31% / 0–4 h | 17 / 0 / 29% / 3 h | 19 / 0 / 31% / 6 h | 18–19 / 0–1 / 25–33% / 5–7 h |
| Sat 7 | 17 / 2 / 27–29% / 3–6 h | 16 / 1 / 29% / 1 h | 18 / 5 / 25% / 8 h | 16–17 / 10–19 / 20–22% / 0 h |
| Sun 8 | 15–17 / 0–1 / 24% / 3–5 h | 14 / 4 / 25% / 0 h | 15 / 7 / 29% / 0 h | 15–16 / 20–27 / 25–29% / 0–3 h |

Two other areas:
- **Gargano (Vieste):** the same wet Sat 31 to Mon 2, then dry; the north coast is sunnier on Sat 7 and Sun 8.
- **Matera:** the same pattern but colder, with highs of 13–16 °C and a 5 °C night on Thu 5.

## What a normal year looks like (ERA5, 2006–2025, 31 Oct–8 Nov)

| Area | Max / min °C | Rain days | Rain per 9 days | Days ≥20 °C | Sun h/day | Wet years (>40 mm) |
|---|---|---|---|---|---|---|
| Bari | 19.6 / 13.5 | 26% | 17 mm | 45% | 7.8 | 1 of 20 |
| Polignano / Monopoli | 19.7 / 13.5 | 26% | 22 mm | 46% | 7.9 | 2 of 20 |
| Ostuni | 18.7 / 12.5 | 31% | 23 mm | 30% | 8.0 | 3 of 20 |
| Lecce | 19.9 / 13.3 | 34% | 31 mm | 48% | 7.8 | 7 of 20 |
| Otranto | 19.9 / 14.7 | 34% | 36 mm | 51% | 7.9 | 7 of 20 |
| Gallipoli | 19.9 / 15.0 | 32% | 31 mm | 51% | 7.9 | 7 of 20 |

- Even in a normal year, early November in Puglia is **around 19–20 °C with rain on 1 day in 3**. It's an autumn food-and-towns trip, not a beach week.
- This year's forecast is **wetter and about 2–3 °C cooler than normal**. Bari and Polignano get about 95 mm over 9 days, against a normal of 17–22 mm.

## Getting there
- **No direct flights from Brussels or Charleroi to Bari or Brindisi on these dates.** Google Flights shows none, and Ryanair's fare finder has no fares around 31 Oct or 8 Nov.
- **The quickest option connects through Rome:** SN3175 BRU 07:00 → FCO 09:10, then AZ1607 FCO 17:35 → BRI 18:45. That's an all-day trip.
- **Price:** about €650–715 return for 2 adults with a bag, so roughly €1,000 for three.

## Verdict
**Puglia isn't worth switching to this week.** Expect 2–3 washed-out days at the start and highs in the mid-teens, and no direct flight.
- If it's Puglia or nothing: base in **Salento (Lecce / Otranto / Gallipoli)**. It's drier on Sat 31 and Tue 3, but stormy on Mon 2 and wetter again on Sat 7 and Sun 8.
- **Better: keep Puglia for late May, June or September**, when it's 25–30 °C with a warm sea.

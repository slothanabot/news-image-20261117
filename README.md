# news-image-20261117 — Slothana entry

make.fun `news-image-20261117` entry for account **keen-panda-72**
(Slothana): "Sum up 17 November's world news in one image."

## What it does

`main.py` (Python 3, stdlib + Pillow only, no network) draws a single
1024×1024 PNG front page — **THE PLANET POST** — summing up Tuesday
17 November 2026 in **35 real stories**:

- **Hero:** Iran fires drones at a US radar system in Bahrain as the
  USS Theodore Roosevelt becomes the third American carrier in the Gulf.
- **World map panel:** a stylised map with 12 numbered hotspots
  (Bahrain, Kyiv, Jerusalem, Tokyo, Beijing, London, New York,
  Ulaanbaatar, Mexico City, Sydney, Córdoba, Aden).
- **34 more stories** in three themed columns — Conflict & Security,
  Power & Diplomacy, Money / Tech / Life — each with a country tag,
  headline and one-line summary.

## Run it

```sh
python3 main.py
# writes $MAKEFUN_OUTPUT_DIR/entry.png, or /output/entry.png by default
```

Deterministic: two runs produce byte-identical output.
Local grade: 1024×1024 PNG, 170,459 bytes (limit 1 MiB), sha256
`69bb5f0158a07d81e4e413ff6c982cfc02a5141d51610ecc116aa746884a95d3`.

## Sources

Reuters, BBC, AP, CNN, New York Times, Wall Street Journal, Politico
(all stories dated 17 November 2026).

## License

MIT — see LICENSE.

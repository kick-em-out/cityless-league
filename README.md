# The Cityless League

A shareable independent website showing Premier League standings from **2009/10 onward**, compared to tables that **exclude Manchester City and void every one of their fixtures**.

## Set up free hosting (GitHub Pages)

1. Make a **public** GitHub repository, e.g. `cityless-league`.
2. Upload the **contents of this folder** to the repository root, including `.github/workflows/update.yml` (the leading dot makes `.github` a hidden folder on some computers).
3. In your repository **Settings → Pages → Build and deployment → Source**, choose **GitHub Actions**.
4. Open **Actions → Update Cityless League data → Run workflow** to populate the historical data and publish the website.
5. Your URL will normally be `https://YOUR_USERNAME.github.io/cityless-league/` once GitHub Pages reports a successful deployment.
6. The GitHub Actions workflow checks for updated results every three hours. Actual run times may vary, and the source CSV may lag the final whistle.

You can alternatively host the static generated files on Cloudflare Pages, but would need to set up a deployment/update workflow for Cloudflare separately.

## Important limitations

- **Historical source**: downloads England's top division `E0.csv` season CSVs from `football-data.co.uk`. The data endpoint and columns may change. Confirm **data usage, licensing and redistribution permissions** before going public; the site currently stores and publishes underlying match data in the JSON file.
- **Official table**: recomputed from match results, with **2009/10 Portsmouth -9 points** and **2023/24 Everton -8 and Nottingham Forest -4** configured as known deductions. Other competition-specific administrative adjustments, final tiebreakers, abandoned fixtures, or later deductions might need manual confirmation. Do not present it as a formally certified official table.
- **No City table**: no City team and no City fixtures whatsoever; this is a mathematical what-if, **not** a historical claim about league sanctions or a prediction of how other fixtures would have played out.
- **Relegation/promotion**: each season uses the clubs actually playing that season. It does not carry alternative relegations/promotions into the next season.
- **xG**: not included. This free results data feed does not supply reliable historical xG; it would require a licensed xG provider.
- **League winner**: comparison calls the first club in each table the 'table leader', since alternative European/relegation qualification is theoretical.
- **Historic start**: the calculation goes back to 2009/10 (not the 2008/09 season).
- **Current season**: comes from CSV once results are available. Check source coverage, particularly 2026/27. Missing seasons are skipped and older saved data retained on transient fetch failures.
- **Free tiers**: GitHub Pages and Actions are free for qualifying public repositories subject to platform limits and terms; cannot guarantee unlimited visitors or free access forever.

## Manually regenerate

With Python 3.9+:

```bash
python build_data.py
python -m http.server 8000
```

Then visit `http://localhost:8000`. An internet connection is required for the download step. The page cannot load CSV itself; serve it after generating `data/seasons.json`.

## Customize the branding

Change the title, headlines, and theme in `index.html`.

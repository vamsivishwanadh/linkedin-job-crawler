# LinkedIn Job Crawler (v1)

Daily LinkedIn job search via [Apify](https://apify.com/), filtered to the **last 24 hours**, scored against your **resume**, and appended to an **Excel** workbook. Designed to run on your PC with **Windows Task Scheduler**.

## What v1 does

| Step | Behavior |
|------|----------|
| Search | Calls `bebity/linkedin-jobs-scraper` (no LinkedIn login required for public job listings) |
| Recency | Apify input `publishedAt: r86400` + optional client-side hour window |
| Fit | TF-IDF cosine similarity between your resume text and each job (title + company + description) |
| Export | Dedupes by job `id`, appends to `data/jobs.xlsx` |

## What v1 does *not* do (v2 ideas)

- Log into LinkedIn with your account or cookies
- Tailor a resume per job or submit Easy Apply / external applications
- LLM-based ranking (easy to add later on top of the same pipeline)

**Note:** Scraping public job listings is common for personal job search, but LinkedIn’s Terms of Service restrict automated access. Use this for your own job hunt, keep volume reasonable, and avoid storing unnecessary personal data from listings.

## Quick start

1. **Apify account** — Create a token at [Apify Integrations](https://console.apify.com/account/integrations). New accounts get free monthly credits; you pay per job returned by the actor.

2. **Clone / open this folder** and create a virtual environment:

   ```powershell
   cd C:\Users\vamsi\Projects\linkedin-job-crawler
   python -m venv .venv
   .\.venv\Scripts\pip install -r requirements.txt
   ```

3. **Configure**

   ```powershell
   copy .env.example .env
   copy config.example.yaml config.yaml
   copy resume\resume.example.txt resume\resume.txt
   ```

   - Put your Apify token in `.env`
   - Edit `config.yaml`: job titles, locations, experience filters, match thresholds
   - Paste your resume into `resume/resume.txt`

4. **Dry run** (config + resume only):

   ```powershell
   .\.venv\Scripts\python -m src.main --dry-run
   ```

5. **Full run**:

   ```powershell
   .\.venv\Scripts\python -m src.main
   ```

   Output: `data/jobs.xlsx`

6. **Schedule daily** (example 8:00 AM):

   ```powershell
   .\scripts\register_scheduled_task.ps1 -Time "08:00"
   ```

   Or run manually: `.\scripts\run_daily.ps1` (logs under `logs/`).

## Config reference

### Apify actor

Default: [`bebity/linkedin-jobs-scraper`](https://apify.com/bebity/linkedin-jobs-scraper) — supports 2026 LinkedIn filters including date posted and experience level. Set `enrich_company: true` only if you want extra fields (extra cost per job).

### Date posted (`publishedAt`)

| Value | Meaning |
|-------|---------|
| `r86400` | Past 24 hours |
| `r604800` | Past week |
| `r2592000` | Past month |

### Experience levels (`experienceLevels` in actor input)

Configure in `config.yaml` under `search.experience_levels` using LinkedIn’s codes (same as in a filtered search URL), for example:

- `1` — Internship  
- `2` — Entry level  
- `3` — Associate  
- `4` — Mid-Senior level  
- `5` — Director  
- `6` — Executive  

Leave empty to not filter by level at search time; resume scoring still ranks fit.

### Work types (`workTypes`)

Examples from the actor docs: `1` on-site, `2` remote, `3` hybrid (verify against a LinkedIn search URL you care about).

### Match score

`min_match_score` and `min_score_to_export` are cosine similarities in `0–1`. Start around `0.12` and raise if you get too much noise, or lower if you miss good roles.

## v2 roadmap (your ideas)

1. **Custom resume per job** — Generate a tailored PDF/DOCX from base resume + job description (LLM or template + keyword injection).
2. **Submit applications** — Would require LinkedIn session (cookies), Playwright automation, and careful rate limits; high ToS/account risk. Better scoped as optional “assist” (open apply URL + prefilled answers) before full auto-submit.

## Project layout

```
config.yaml          # your search + thresholds (not committed)
resume/resume.txt    # plain-text resume for matching
src/main.py          # entrypoint
scripts/run_daily.ps1
data/jobs.xlsx       # generated output
```

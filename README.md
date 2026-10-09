# LinkedIn Job Crawler

Daily LinkedIn job search via [Apify](https://apify.com/), filtered to the **last 24 hours**, scored against your **resume**, and appended to an **Excel** workbook. Optional **AI-tailored PDF resumes** per job. Designed to run on your PC with **Windows Task Scheduler**.

## Crawler (v1)

| Step    | Behavior                                                                     |
| ------- | ---------------------------------------------------------------------------- |
| Search  | Calls `bebity/linkedin-jobs-scraper` (no LinkedIn login for public listings) |
| Recency | Apify `publishedAt: r86400` + optional client-side hour window               |
| Fit     | TF-IDF cosine similarity vs `resume/resume.txt`                              |
| Export  | Dedupes by job `id`, writes `data/jobs.xlsx`                                 |

## Resume generator

| Step           | Behavior                                                                   |
| -------------- | -------------------------------------------------------------------------- |
| Master resume  | Reuses `resume/resume.txt` via `load_resume_text()` (same as scoring)      |
| Job from Excel | Reads `export.excel_path` / `description` column (full JD when crawled)    |
| Manual JD      | `--jd-file` or `--jd-paste`                                                |
| LLM            | OpenAI JSON → JD analysis + tailored resume (Pydantic)                     |
| Validation     | Evidence quotes must appear in master resume; unsupported claims block PDF |
| Output         | PDF + `.meta.json` + `.preview.json` under `data/resumes/`                 |

**Not included:** LinkedIn login, URL scraping for JDs, auto-apply, or changing TF-IDF scoring.

## Quick start

```powershell
cd C:\Users\vamsi\Projects\linkedin-job-crawler
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
copy config.example.yaml config.yaml
copy resume\resume.example.txt resume\resume.txt
```

- `.env`: `APIFY_TOKEN` (crawler), `OPENAI_API_KEY` (resume generator), optional `OPENAI_MODEL`
- `config.yaml`: search + `resume:` block (see `config.example.yaml`)
- Paste your resume into `resume/resume.txt`

### Crawl jobs

```powershell
.\.venv\Scripts\python -m src.main --dry-run
.\.venv\Scripts\python -m src.main
# equivalent: python -m src.main crawl
```

Output: `data/jobs.xlsx` (close Excel before writing to avoid permission errors).

### Generate a tailored resume

List jobs from the workbook:

```powershell
.\.venv\Scripts\python -m src.main resume --list
```

From a crawled job (uses `description` in Excel):

```powershell
.\.venv\Scripts\python -m src.main resume --job-id 4477101573
```

Preview only (no PDF, writes `*.preview.json`):

```powershell
.\.venv\Scripts\python -m src.main resume --job-id 4477101573 --preview-only
```

From a text file:

```powershell
.\.venv\Scripts\python -m src.main resume --jd-file .\jd.txt --title "Backend Engineer" --company "Acme"
```

Paste JD (Ctrl+Z then Enter on Windows):

```powershell
.\.venv\Scripts\python -m src.main resume --jd-paste --title "Role" --company "Co"
```

Outputs: `data/resumes/Company_Role.pdf` (timestamp suffix if file exists), plus `.meta.json` and `.preview.json`.

### Schedule daily crawl

```powershell
.\scripts\register_scheduled_task.ps1 -Time "08:00"
```

Scheduled task runs **crawl only**, not resume generation.

## JD resolution (workbook jobs)

1. Full `description` cell in `data/jobs.xlsx` (primary; populated by crawler)
2. No separate job database or JSON cache
3. Job URL fetch is **not** implemented — use `--jd-file` / `--jd-paste` if description is missing
4. Will not generate from title/company alone

## Environment variables

| Variable         | Required for      | Purpose               |
| ---------------- | ----------------- | --------------------- |
| `APIFY_TOKEN`    | Crawl             | Apify API             |
| `OPENAI_API_KEY` | Resume            | OpenAI API            |
| `OPENAI_MODEL`   | Resume (optional) | Default `gpt-4o-mini` |

## Config: `resume` section

```yaml
resume:
  output_dir: data/resumes
  strict_validation: true
  allow_warnings_pdf: true
```

## API costs

Each resume run uses **two** LLM calls (analysis + tailoring). Use `--preview-only` to inspect JSON before paying for a full run. Crawler costs are per Apify job returned.

## Validation limits

Validation checks that bullet `evidence` strings appear in the master resume and flags unknown companies/skills. It is **heuristic**, not a guarantee against hallucinations — review `*.preview.json` before applying.

## Privacy / gitignore

Ignored: `.env`, `config.yaml`, `resume/resume.txt`, `data/*.xlsx`, `data/resumes/`, `*.meta.json`, `*.preview.json`.

## Tests

```powershell
.\.venv\Scripts\pytest
```

Uses mocked LLM for pipeline tests (no API charges).

## Project layout

```
src/main.py           # crawl + resume subcommands
src/matching.py       # master resume load + TF-IDF (unchanged algorithm)
src/export.py         # Excel write schema
src/workbook_jobs.py  # Excel read + job id lookup
src/resume/           # LLM, validation, PDF
data/jobs.xlsx        # crawler output
data/resumes/         # generated PDFs
```

## Crawler config reference

Edit `config.yaml` (copy from `config.example.yaml`). The crawler reads the `apify`, `search`, `matching`, and `export` sections.

### Apify actor

Default: [`bebity/linkedin-jobs-scraper`](https://apify.com/bebity/linkedin-jobs-scraper) — supports LinkedIn filters including date posted and experience level. Set `enrich_company: true` only if you want extra fields (extra cost per job).

| Key                         | Meaning                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------- |
| `apify.actor_id`            | Apify actor id (default above)                                                                          |
| `apify.published_at`        | How far back to search on LinkedIn (see table below)                                                    |
| `apify.max_rows_per_search` | Max jobs **per** title × location search (actor allows up to 1000; use `0` for all pages — higher cost) |
| `apify.company_profile`     | Company details on each job (on by default)                                                             |
| `apify.enrich_company`      | Extra hiring-contact / timestamp fields (paid add-on per job)                                           |

### Date posted (`apify.published_at`)

Sent to Apify as `publishedAt`:

| Value      | Meaning       |
| ---------- | ------------- |
| `r86400`   | Past 24 hours |
| `r604800`  | Past week     |
| `r2592000` | Past month    |

You can also tighten recency in `matching.max_hours_since_posted` / `max_hours_since_posted` (client-side filter after fetch).

### Search filters (`search` in `config.yaml`)

| Key                          | Meaning                                                 |
| ---------------------------- | ------------------------------------------------------- |
| `search.titles`              | Job titles / keywords (each title is a separate search) |
| `search.locations`           | Locations (each title × each location is one search)    |
| `search.work_types`          | On-site / remote / hybrid (see codes below)             |
| `search.contract_types`      | Job type, e.g. full-time (see codes below)              |
| `search.experience_levels`   | Seniority filter (see codes below)                      |
| `search.easy_apply`          | Only Easy Apply jobs                                    |
| `search.under_10_applicants` | Only jobs with fewer than 10 applicants                 |

Leave a list empty (`[]`) to skip that filter at search time. Resume TF-IDF scoring still ranks fit either way.

### Experience levels (`search.experience_levels`)

Use LinkedIn’s numeric codes (same as in a filtered search URL), for example:

| Code | Level            |
| ---- | ---------------- |
| `1`  | Internship       |
| `2`  | Entry level      |
| `3`  | Associate        |
| `4`  | Mid-Senior level |
| `5`  | Director         |
| `6`  | Executive        |

Example — mid-senior and director only:

```yaml
search:
  experience_levels: ["4", "5"]
```

### Work types (`search.work_types`)

| Code | Type    |
| ---- | ------- |
| `1`  | On-site |
| `2`  | Remote  |
| `3`  | Hybrid  |

Example — remote and hybrid:

```yaml
search:
  work_types: ["2", "3"]
```

Verify codes against a LinkedIn job search URL you care about if results look wrong.

### Contract types (`search.contract_types`)

Common Apify / LinkedIn values include:

| Code | Type       |
| ---- | ---------- |
| `F`  | Full-time  |
| `P`  | Part-time  |
| `C`  | Contract   |
| `T`  | Temporary  |
| `I`  | Internship |
| `V`  | Volunteer  |

Example:

```yaml
search:
  contract_types: ["F"]
```

### Match score (`matching` / `export`)

| Key                          | Meaning                                                                |
| ---------------------------- | ---------------------------------------------------------------------- |
| `matching.min_match_score`   | Minimum TF-IDF cosine similarity (0–1) to count as a match after crawl |
| `export.min_score_to_export` | Minimum score to write a row to Excel (often same as above)            |
| `matching.resume_path`       | Master resume for scoring (default `resume/resume.txt`)                |

Scores are **lexical** overlap between your resume and each job’s title + company + description — not years-of-experience logic. Start around `0.12` and raise if you get noise, or lower if you miss good roles.

### Excel export (`export`)

| Key                 | Meaning                                    |
| ------------------- | ------------------------------------------ |
| `export.excel_path` | Output workbook (default `data/jobs.xlsx`) |
| `export.sheet_name` | Worksheet name (default `jobs`)            |

Rows are deduped by job `id`; re-crawling updates existing ids. Close the file in Excel before running the crawler to avoid permission errors.

# Learning Analytics Toolkit

A data analyst pipeline that turns messy, multi-source data from a tutoring
business into one Excel workbook a non-technical reader can actually act on.

- **Cleans real-world messy data.** Tutoring session logs with inconsistent
  subject spellings and casing, duplicate rows, and duration outliers; daily
  web analytics with inconsistent source/medium casing and missing bounce
  rates; SEO keyword data where a missing ranking genuinely means "not yet
  ranked" rather than a value to guess at.
- **Scores students for academic support needs.** A transparent, explainable
  model combines each student's average performance, their score trend
  across sessions, and their engagement into a single 0-100 risk score and a
  support category (on track, monitor, needs support) — no black box.
- **Analyzes marketing and web performance.** Conversion rate by acquisition
  source and an SEO keyword opportunity score that rewards high search
  volume paired with a poor or absent ranking.
- **Reports it all in Excel.** A multi-tab workbook built with openpyxl: a
  student risk summary with a pandas pivot-table-style category breakdown,
  a color-scaled risk column, and a chart; a marketing overview with a
  conversion-rate chart and a color-scaled keyword opportunity table. See
  `output/learning_analytics_report.xlsx` for a generated sample.

## Project layout

```
app/
  synthetic_data.py        seeded, deliberately messy multi-source data generators
  cleaning.py                subject standardization, dedup, outlier handling, imputation
  risk_scoring.py             the academic-need scoring model
  marketing_analytics.py       conversion rate, keyword opportunity, traffic trend
  excel_report.py               builds the multi-tab Excel workbook
  pipeline.py                    runs the full pipeline end to end
tests/
output/
  learning_analytics_report.xlsx   a generated sample workbook
```

## Running it locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python3 -m app.pipeline
```

This writes `output/learning_analytics_report.xlsx`.

## Testing

```bash
pytest -v
```

## Design notes

The risk score is a weighted blend of average performance (40%), score
trend (30%), and engagement (30%), chosen so that a reader can see exactly
why a student was flagged rather than trusting an opaque model — appropriate
for a score that may inform how a human tutor spends their time. Missing
values are handled based on what they actually mean: a missing engagement
rating is imputed with the per-subject median, since it is plausibly just
unrecorded, while a missing keyword ranking is kept as an explicit "not
ranked" flag rather than imputed, since it is a real, meaningful state.

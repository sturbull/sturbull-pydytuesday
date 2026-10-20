# pydytuesday

Repo for storing [TidyTuesday](https://github.com/rfordatascience/tidytuesday) work and visualisations in Python.

Latest plot: [2026-10-20](final/2026-10-20-plot.png)

![2026-10-20 TidyTuesday plot](final/2026-10-20-plot.png)

## Setup

Install [uv](https://docs.astral.sh/uv/), then install the dependencies:

```
uv sync
```

## Starting a new week

`new_week.py` creates a [marimo](https://marimo.io/) notebook for a TidyTuesday week, similar to `tidytuesdayR::use_tidytemplate()` in R.

```
uv run new_week.py              # this week's Tuesday
uv run new_week.py 2025-01-08   # the week containing that date
uv run new_week.py --force      # overwrite an existing notebook
```

The notebook is written to `code/<year>/<date>/tt_<date>.py`. Open it with:

```
uv run marimo edit code/<year>/<date>/tt_<date>.py
```

On the first run, the notebook downloads the week's CSV files into a `data/` folder next to it. Later runs read from that folder, so they don't call the GitHub API again. `data/` folders are gitignored.

The notebook loads each CSV into the `tt` dictionary, keyed by file name, and shows a tab for each table. After those come an empty cell for wrangling and a Visualise cell where you assign your plotnine plot to `plot`.

The Visualise section also defines `caption`, a list of plotnine components that adds a caption with my name, the week's date, my website, GitHub and LinkedIn, and the data source. End the plot with `+ caption`. The data source comes from the week's `meta.yaml`; weeks without one show "TidyTuesday". The GitHub and LinkedIn icons come from the Font Awesome Brands font in `fonts/` (SIL OFL 1.1, see `fonts/LICENSE-fontawesome.txt`).

The Save image cell has a "Save to final/" button. It writes `plot` to `final/<date>-<FILENAME>`, for example `final/2025-01-07-rainfall.png`. Set `FILENAME` in that cell; its extension (`.png`, `.jpg`, `.svg`, `.pdf`) sets the format.

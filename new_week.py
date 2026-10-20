"""Create a marimo notebook for a TidyTuesday week.

The Python counterpart to tidytuesdayR::use_tidytemplate(). Run from the repo root:

    uv run new_week.py              # this week's Tuesday
    uv run new_week.py 2025-01-08   # the week containing that date

The notebook is written to code/<year>/<date>/tt_<date>.py. Open it with:

    uv run marimo edit code/<year>/<date>/tt_<date>.py
"""

import argparse
from pathlib import Path
from string import Template

import marimo
import pydytuesday

CODE_DIR = Path(__file__).resolve().parent / "code"

TEMPLATE = Template(r'''import marimo

__generated_with = "${marimo_version}"
app = marimo.App(width="medium")


@app.cell
def _():
    import contextlib

    import marimo as mo
    import polars as pl
    import pydytuesday
    return contextlib, mo, pl, pydytuesday


@app.cell
def _(mo):
    mo.md(r"""
    # TidyTuesday ${date}

    [Dataset on GitHub](https://github.com/rfordatascience/tidytuesday/tree/main/data/${year}/${date})
    """)
    return


@app.cell
def _(mo):
    DATE = "${date}"
    DATA_DIR = mo.notebook_dir() / "data"
    FINAL_DIR = mo.notebook_dir().parents[2] / "final"  # notebooks live in code/<year>/<date>/
    DATA_DIR
    return DATA_DIR, DATE, FINAL_DIR


@app.cell
def _(mo):
    mo.md(r"""
    ## Load the weekly data

    Downloads the CSVs into data/ on the first run, then reads them from disk.
    """)
    return


@app.cell
def _(DATA_DIR, DATE, contextlib, pl, pydytuesday):
    DATA_DIR.mkdir(exist_ok=True)
    if not any(DATA_DIR.glob("*.csv")):
        with contextlib.chdir(DATA_DIR):
            pydytuesday.get_date(DATE)

    # TidyTuesday CSVs are written from R, so missing values appear as "NA".
    # Polars infers types from the first 100 rows by default; scan the whole file instead.
    tt = {
        path.stem: pl.read_csv(path, null_values="NA", infer_schema_length=None)
        for path in sorted(DATA_DIR.glob("*.csv"))
    }
    list(tt)
    return (tt,)


@app.cell
def _(mo, tt):
    mo.ui.tabs(tt)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Wrangle
    """)
    return


@app.cell
def _():
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Visualise

    Assign the finished plotnine plot to `plot`.
    """)
    return


@app.cell
def _():
    plot = None
    return (plot,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Save image

    Saves `plot` to final/ as `<date>-<FILENAME>`. The extension in `FILENAME` sets the format.
    """)
    return


@app.cell
def _(mo):
    save_button = mo.ui.run_button(label="Save to final/")
    save_button
    return (save_button,)


@app.cell
def _(DATE, FINAL_DIR, mo, plot, save_button):
    FILENAME = "plot.png"

    mo.stop(plot is None or not save_button.value)

    FINAL_DIR.mkdir(exist_ok=True)
    plot.save(FINAL_DIR / f"{DATE}-{FILENAME}", dpi=300, verbose=False)
    mo.md(f"Saved final/{DATE}-{FILENAME}")
    return


if __name__ == "__main__":
    app.run()
''')


def main():
    parser = argparse.ArgumentParser(description="Create a marimo notebook for a TidyTuesday week.")
    parser.add_argument(
        "date",
        nargs="?",
        help="Any date in YYYY-MM-DD format; uses the Tuesday of that week. Defaults to today.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite an existing notebook.")
    args = parser.parse_args()

    date = pydytuesday.last_tuesday(args.date)
    week_dir = CODE_DIR / date[:4] / date
    notebook = week_dir / f"tt_{date}.py"
    if notebook.exists() and not args.force:
        parser.exit(1, f"{notebook} already exists. Use --force to overwrite it.\n")

    week_dir.mkdir(parents=True, exist_ok=True)
    notebook.write_text(
        TEMPLATE.substitute(date=date, year=date[:4], marimo_version=marimo.__version__),
        encoding="utf-8",
    )
    print(f"Created {notebook}")


if __name__ == "__main__":
    main()

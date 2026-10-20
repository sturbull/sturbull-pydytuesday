import marimo

__generated_with = "0.25.1"
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
    # TidyTuesday 2026-10-20

    [Dataset on GitHub](https://github.com/rfordatascience/tidytuesday/tree/main/data/2026/2026-10-20)
    """)
    return


@app.cell
def _(mo):
    DATE = "2026-10-20"
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
def _(pl):
    df = pl.read_csv("./data/major_occupations.csv")
    df

    #df.select(pl.col("field_of_study").n_unique())


    return (df,)


@app.cell
def _(df, pl):
    df2 = pl.read_csv("./data/ai_salary_majors.csv")
    df2

    df_complete = df2.join(df.select("cip4","occupation"),on="cip4")
    df_complete
    return (df_complete,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Visualise

    Assign the finished plotnine plot to `plot`.
    """)
    return


@app.cell
def _(mo):
    colour_option = mo.ui.dropdown(
        options = ["orange","red","green","blue"],
        allow_select_none=False,value="red",
        label="choose colour"
        )
    colour_option
    return (colour_option,)


@app.cell
def _(df_complete):
    import plotly.express as px

    plot_plotly = px.scatter_ternary(
        df_complete,
        color="broad_field_short",
        a="ai_exposure",
        b="ai_exposure_language",
        c="ai_exposure_image",
        hover_name="occupation",
    )

    plot_plotly
    return


@app.cell
def _(colour_option, df):
    import matplotlib.pyplot as plt
    import mpltern  # Essential to register the 'ternary' projection

    # 2. Initialize a Matplotlib figure with a ternary projection
    fig = plt.figure(figsize=(6, 5))
    ax = fig.add_subplot(projection="ternary")

    # 3. Pull columns directly out of Polars into the plot
    ax.scatter(df["ai_exposure"], df["ai_exposure_language"], df["ai_exposure_image"], color=colour_option.value, marker="o")

    # 4. Set labels for the corners
    ax.set_tlabel("AI Exposure")
    ax.set_llabel("AI Exposure Language")
    ax.set_rlabel("AI Exposure Image")

    ax.grid()
    plt.show()
    return


@app.cell
def _(colour_option, df):
    import plotnine as pn

    plot_plotnine= (
        pn.ggplot(
            df,
            pn.aes(
                x="ai_exposure_language",
                y = "ai_exposure_image",
                )
                ) +
        pn.geom_point(color = colour_option.value) +
        pn.geom_smooth()
    )
    return (plot_plotnine,)


@app.cell
def _(plot_plotnine):

    plot_plotnine
    return


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

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
    FINAL_DIR = (
        mo.notebook_dir().parents[2] / "final"
    )  # notebooks live in code/<year>/<date>/
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
    df = pl.read_csv("./data/major_occupations.csv", null_values="NA")
    df
    return (df,)


@app.cell
def _(df, pl):
    df2 = pl.read_csv("./data/ai_salary_majors.csv", null_values="NA")
    df2

    df_complete = (
        df2.join(df.select("cip4", "occupation"), on="cip4")
        # make new composite key for the rows
        .with_columns(
            occupation_field=pl.concat_str(
                "occupation", "field_of_study", separator=" | "
            )
        )
        .with_columns(pl.col("median_salary_4yr").cast(pl.Int64))
    )

    df_complete
    return df2, df_complete


@app.cell
def _(mo):
    mo.md(r"""
    ## Visualise

    Assign the finished plotnine plot to `plot`.
    """)
    return


@app.cell
def _(mo):
    from matplotlib import font_manager

    font_manager.fontManager.addfont(
        mo.notebook_dir().parents[2] / "fonts" / "fa-brands-400.ttf"
    )

    caption = (
        "Steven Turnbull | #PydyTuesday #TidyTuesday 2026-10-21\n"
        "sturbull.github.io   \uf09b sturbull   \uf08c steven-martin-turnbull\n"
        "Data: US Dept. of Education College Scorecard; AI Occupational Exposure (Felten, Raj & Seamans)"
    )

    return (caption,)


@app.cell
def _(mo):
    colour_option = mo.ui.dropdown(
        options=["orange", "red", "green", "blue"],
        allow_select_none=False,
        value="red",
        label="choose colour",
    )
    colour_option
    return (colour_option,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Plotly
    """)
    return


@app.cell
def _(df_complete):
    import plotly.express as px

    plot_plotly = px.scatter_ternary(
        df_complete,
        color="broad_field_short",
        a="ai_exposure",
        b="ai_exposure_language",
        c="ai_exposure_image",
        hover_name="occupation_field",
    )

    plot_plotly
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Matplotlib
    """)
    return


@app.cell
def _(colour_option, df):
    import matplotlib.pyplot as plt
    import mpltern  # Essential to register the 'ternary' projection

    # 2. Initialize a Matplotlib figure with a ternary projection
    fig = plt.figure(figsize=(6, 5))
    ax = fig.add_subplot(projection="ternary")

    # 3. Pull columns directly out of Polars into the plot
    ax.scatter(
        df["ai_exposure"],
        df["ai_exposure_language"],
        df["ai_exposure_image"],
        color=colour_option.value,
        marker="o",
    )

    # 4. Set labels for the corners
    ax.set_tlabel("AI Exposure")
    ax.set_llabel("AI Exposure Language")
    ax.set_rlabel("AI Exposure Image")

    ax.grid()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Plotnine
    """)
    return


@app.cell
def _(df2, pl):
    import plotnine as pn

    df_filtered = (
        df2.drop_nulls("median_salary_4yr")
        .filter(pl.col("median_starting_salary") > 50000)
        .with_columns(
            salary_diff=pl.col("median_salary_4yr") - pl.col("median_starting_salary")
        )
    )
    return df_filtered, pn


@app.cell
def _(df_filtered, pl):
    # get order of occupation_field for enum
    salary_order = (
        df_filtered.group_by("field_of_study")
        .agg(pl.col("median_starting_salary").median())
        .sort("median_starting_salary")
        .get_column("field_of_study")
        .to_list()
    )
    return (salary_order,)


@app.cell
def _(mo):
    top_n = mo.ui.slider(1, 30, value=6, label="Highlight Top N")
    top_n
    return (top_n,)


@app.cell
def _(df_filtered, top_n):

    big_diffs = (
        df_filtered.sort(by="salary_diff", descending=True)
        .head(top_n.value)
        .get_column("field_of_study")
        .to_list()
    )
    return (big_diffs,)


@app.cell
def _(df_filtered, pl, salary_order):

    df_complete_filtered = df_filtered.with_columns(
        pl.col("field_of_study").cast(pl.Enum(salary_order))
    )
    return (df_complete_filtered,)


@app.cell
def _(big_diffs, df_complete_filtered, pl):

    df_topN = df_complete_filtered.filter(pl.col("field_of_study").is_in(big_diffs))
    return (df_topN,)


@app.cell
def _(caption, df_complete_filtered, df_topN, pn):
    from mizani.labels import label_comma

    plot_plotnine = (
        pn.ggplot()
        + pn.geom_segment(
            pn.aes(
                x="median_starting_salary",
                xend="median_salary_4yr",
                y="field_of_study",
                yend="field_of_study",
                colour="salary_diff",
            ),
            df_complete_filtered,
        )
        + pn.geom_point(
            pn.aes(
                y="field_of_study",
                x="median_starting_salary",
                color="salary_diff",
            ),
            df_complete_filtered,
        )
        + pn.geom_text(
            pn.aes(x="median_salary_4yr", y="field_of_study", label="field_of_study"),
            df_topN,
            size=7,
            color="#E6E6E6",
            adjust_text={
                "arrowprops": {
                    "arrowstyle": "-",
                    "color": "grey",
                    "alpha": 0.4,
                    "lw": 0.5,
                }
            },
        )
        + pn.scale_x_continuous(name="Salary (Median $)", labels=label_comma())
        + pn.ggtitle(
            "Difference Between Starting Salary and Salary After 4 Years",
            subtitle=f"Top {df_topN.height} fields of study highlighted",
        )
        + pn.labs(caption=caption)
        + pn.theme(
            figure_size=(8, 10),
            axis_text_y=pn.element_blank(),
            axis_ticks_major_y=pn.element_blank(),
            panel_grid_major_y=pn.element_blank(),
            panel_grid_minor_y=pn.element_blank(),
            axis_title_y=pn.element_blank(),
            legend_position="none",
            dpi=600,
            plot_caption=pn.element_text(
                family=["DejaVu Sans", "Font Awesome 6 Brands"], size=7, ha="left"
            ),
            plot_caption_position="plot",
            plot_background=pn.element_rect(fill="#1E2130", colour="#1E2130"),
            panel_background=pn.element_rect(fill="#1E2130"),
            text=pn.element_text(colour="#E6E6E6"),
            panel_grid_major_x=pn.element_line(colour="#3A3F4F"),
            panel_grid_minor_x=pn.element_blank(),
        )
    )

    plot_plotnine
    return (plot_plotnine,)


@app.cell
def _(plot_plotnine):
    plot = plot_plotnine
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

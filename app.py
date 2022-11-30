from shiny import App, render, ui, reactive
from helper_function import get_slide, get_instrument, get_duration, loadtable, get_slideOB2
import pandas as pd
import asyncio


app_ui = ui.page_fluid(
    ui.h2({"style": "text-align: left;"}, "Apton Biosystems Timing workflow Dashboard"),
    ui.navset_tab_card(
        ui.nav("Slide report",
            ui.layout_sidebar(
                ui.panel_sidebar(
                    ui.input_select("s0", "Slides (OB2 from Rack4/FSS)", get_slideOB2()),
                    #ui.input_select("I0", "Instruments (Rack4/FSS)", ['OneBox-02', 'OneBox-03']),
                    #ui.input_select("s0", "Slides (OB2/OB3 from Rack4/FSS)", get_slide()),
                    width=3
                ),
                ui.panel_main(
                    ui.navset_tab_card(
                        ui.nav("Main",
                            ui.output_text_verbatim("get_Ins"),
                            ui.output_text_verbatim("get_ST"),
                            ui.output_table("get_maintable"),
                            ui.download_button("downloadData", "Download"),
                               ),
                        ui.nav("Loop Cycle-Biofluidics",
                               ui.output_table("get_fludictable"),
                               ),
                        ui.nav("Loop Cycle-Imaging",
                            ui.output_table("get_imagetable"),
                                ),
                        ui.nav("Loop Cycle-Statistics",
                               ui.output_text_verbatim("get_BioImagetime"),
                               ),
                                       )
                )
            )
               ),
        ui.nav("projection/prediction",
               ),
        ui.nav("timeline report",
               ),
        ui.nav("real time report",
            ui.layout_sidebar(
                ui.panel_sidebar(
                    ui.input_select("I0", "Instruments (Rack4/FSS)", ['OneBox-02', 'OneBox-03', 'OneBox-04', 'OneBox-05']),
                    width=3,
                ),
                ui.panel_main()
            )
               ),
    )
)


def server(input, output, session):
    @output
    @render.text()
    @reactive.event(input.s0)
    def get_Ins():
        return f"Instrument: {get_instrument(input.s0())} | Cycles: {get_duration(input.s0())[3]}"

    @output
    @render.text()
    @reactive.event(input.s0)
    def get_ST():
        return f"Duration start: {get_duration(input.s0())[4]} | Duration end:{get_duration(input.s0())[5]}"

    @session.download(filename="test.csv")
    async def downloadData():
        await asyncio.sleep(0.25)
        yield input.s0


    @output
    @render.table
    @reactive.event(input.s0)
    def get_maintable():
        endAll = loadtable(input.s0())
        main_table = endAll[(endAll['step_len'] == 1) & (endAll['main'] == 'main')][
            ['DATE_TIME', 'sub', 'sub2', 'steps', 'time_m', 'time_h']]
        return main_table

    @output
    @render.table
    @reactive.event(input.s0)
    def get_imagetable():
        endAll = loadtable(input.s0())
        df_lp = endAll[(endAll['step_len'] == 2) & (endAll['main'] == 'main')]
        grouped = df_lp.groupby('sub').sum().reset_index()
        MC = grouped['sub'].to_list()
        MC0 = [f for f in MC if 'Imag' in f][0]
        df_lp1 = df_lp[(df_lp['sub'] == MC0)][['DATE_TIME', 'sub', 'steps', 'time_m']]
        return df_lp1

    @output
    @render.table
    @reactive.event(input.s0)
    def get_fludictable():
        endAll = loadtable(input.s0())
        df_lp = endAll[(endAll['step_len'] == 2) & (endAll['main'] == 'main')]
        grouped = df_lp.groupby('sub').sum().reset_index()
        MC = grouped['sub'].to_list()
        MC1 = [f for f in MC if 'Fluidics' in f][0]
        if len([f for f in MC if 'Fluidics' in f]) > 1:
            MC2 = [f for f in MC if 'Fluidics' in f][1]
            df_lp2 = df_lp[(df_lp['sub'] == MC1) | (df_lp['sub'] == MC2)][['DATE_TIME', 'sub', 'steps', 'time_m']]
        else:
            df_lp2 = df_lp[(df_lp['sub'] == MC1)][['DATE_TIME', 'sub', 'steps', 'time_m']]
        return df_lp2

    @output
    @render.text()
    @reactive.event(input.s0)
    def get_BioImagetime():
        endAll = loadtable(input.s0())
        df_lp = endAll[(endAll['step_len'] == 2) & (endAll['main'] == 'main')]
        grouped = df_lp.groupby('sub').sum().reset_index()
        MC = grouped['sub'].to_list()
        MC0 = [f for f in MC if 'Imag' in f][0]
        MC1 = [f for f in MC if 'Fluidics' in f][0]
        AveImag = df_lp[(df_lp['sub'] == MC0)]['time_m'].mean()
        AveBio = df_lp[(df_lp['sub'] == MC1)]['time_m'].mean()

        return f"Ave Biofluidic time: {'%.2f' %AveBio} (min) | Ave Imaging time:{'%.2f' %AveImag} (min)"

app = App(app_ui, server)

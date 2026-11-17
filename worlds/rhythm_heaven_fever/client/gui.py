import asyncio

from kvui import GameManager


class RHFManager(GameManager):

    logging_pairs = [
        ("Client", "Archipelago"),
    ]

    base_title = "Archipelago Rhythm Heaven Fever Client"


def run_gui(ctx):

    ctx.ui = RHFManager(ctx)

    ctx.ui_task = asyncio.create_task(
        ctx.ui.async_run(),
        name="UI"
    )
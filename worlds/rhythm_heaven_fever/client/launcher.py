import asyncio

from CommonClient import (
    get_base_parser,
    server_loop,
)

from .RHFClient import RHFClient

def run_client(*launcher_args):

    parser = get_base_parser(
        description=(
            "Rhythm Heaven Fever "
            "Archipelago Client."
        )
    )

    args = parser.parse_args(launcher_args)

    async def _run():

        ctx = RHFClient(
            args.connect,
            args.password
        )

        ctx.server_task = asyncio.create_task(
            server_loop(ctx),
            name="ServerLoop"
        )

        ctx.run_gui()

        await ctx.exit_event.wait()
        await ctx.shutdown()

    asyncio.run(_run())


def main():
    run_client()


if __name__ == "__main__":
    main()
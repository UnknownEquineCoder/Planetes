from src import game
import asyncio


async def main() -> int:
    """
    Run the game

    :return: The exit code
    """
    await game.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

import sys
from .settings import *
from .level import Level, GameOver
import asyncio

# Initialize the pygame engine
pygame.init()

# Set screen size
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Planetes by @unknown_equine')

# init the level
level = Level(level_map, screen)


async def main():
    # Event loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill("black")
        try:
            await level.run()
        except GameOver:
            pygame.quit()
            raise SystemExit(0)

        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    asyncio.run(main())

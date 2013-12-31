import pygame, os, sys, math
import handler

from pygame.locals import *
from game import Game

def main():
  # Initialise stuff: Pygame, the clock..
  pygame.init()
  clock = pygame.time.Clock()
  game = Game()

  # Get the PyGame variables in to Game.
  game.screen = pygame.display.set_mode((game.xRes,game.yRes), DOUBLEBUF | HWSURFACE)
  pygame.display.set_caption('Hullet Bell')

  # Set up initial handler
  game.handler = handler.TitleScreenHandler(game)

  while True:
    # Cap the frame rate.
    clock.tick(60)

    # Run the game handler.
    if not game.handler.update():
      break

    # Show our hard work!
    pygame.display.flip()

  pygame.quit()


import cProfile as profile
if __name__ == "__main__":
  #profile.run('main()')
  main()
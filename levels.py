import math

import pygame
import scripting

# Levels are tuples of scripts and assets

# Assets are items that will be loaded by the game before the level starts
# Asset types include enemy types, bullet types, backgrounds, decorations, other destructables..
# Currently, you will have to provide a list of assets used in the level.
# In the future, we'll attempt to automatically extract all assets that have to be loaded.

# TODO notes here because why not:
# Animations - Include .load() function
# Sounds - Include .load() function
# Remember to write that load handler stuff, jeez

# Ultimate TO-DO: Introduce script designer program for visually construction level and entity scripts

class Asset(object):
  """Superclass for all assets"""
  def __init__(self, animations, sounds):
    super(Asset, self).__init__()
    self.animations = animations
    self.sounds = sounds
    
def level1():
  assets = []
  enemyScripter = scripting.EntityScripter()
  enemyScripter.addScript(enemyScripter.setSpeed(2))
  for i in range(360):
    if i % 30 == 0:
      enemyScripter.addScript(enemyScripter.setDirection(math.radians(360 - i)),
                              enemyScripter.shootAtPlayer(0, 2))
    else:
      enemyScripter.addScript(enemyScripter.setDirection(math.radians(360 - i)))
  enemyScripter.setLooping(True)
  
  scripter = scripting.Scripter()
  scripter.addWait(120)
  scripter.addScript(scripter.createEnemy(None, enemyScripter))
  scripter.setLooping(True)

  return (scripter, assets)
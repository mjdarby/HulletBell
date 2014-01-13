import pygame, math
import drawable, scripting
from constants import *

class Hitbox(pygame.Rect):
  """Basically just a rename of pygame.Rect"""
  def __init__(self, left, top, width, height):
    """Left, top is the offset from the logical center of the entity"""
    super(Hitbox, self).__init__(left, top, width, height)

class Bounds(pygame.Rect):
  """The bounds that the entity can't move out of"""
  def __init__(self, left, top, width, height):
    super(Bounds, self).__init__(left, top, width, height)    

class Entity(drawable.Drawable):
  """Base class for all entities that interact with each other via collisions"""
  def __init__(self, handler):
    super(Entity, self).__init__(60, 60)
    self.hitbox = None # TODO this should be a hitbox
    self.collidable = True # Entity can call 'collide' on others
    self.dead = False # Remove from screen on next update?
    self.xvel = 0
    self.yvel = 0
    self.angle = math.radians(315)
    self.speed = 2

    # Bounds stuff
    self.boundsChecked = True # Call die() if out of bounds
    self.bounds = Bounds(GAMEOFFSET, GAMEOFFSET, GAMEXWIDTH, GAMEYWIDTH)
    self.bounds.inflate_ip(50, 50) # Default bounds for non-players
    self.handler = handler
    self.scripter = scripting.EntityScripter(self)

  def update(self):
    self._runScript()
    self._updateMovement()
    self._special()

    # Kill on OOB
    if self.boundsChecked and not self.bounds.contains(self.hitbox):
      self.die()

  def isCollide(self, other):
    return self.collidable and other.hitbox.colliderect(self.hitbox)

  def collide(self, other):
    print "Collided!"

  def setScript(self, script):
    self.scripter = script

  def setX(self, x):
    self.x = x
    self.hitbox.x = x

  def setY(self, y):
    self.y = y
    self.hitbox.y = y

  def die(self):
    # Death logic, usually playing an animation and removing self from screen
    # TODO: Animation!
    self.collidable = False
    self.dead = True

  def _special(self):
    pass

  def _runScript(self):
    self.scripter.execute()

  def _updateMovement(self):
    # Update velocities according to angle and speed
    self.xvel = math.cos(self.angle) * self.speed
    self.yvel = -math.sin(self.angle) * self.speed

    self.x += self.xvel
    self.y += self.yvel

    # Move by X
    self.hitbox.x = math.floor(self.x)
    # Move by Y
    self.hitbox.y = math.floor(self.y)

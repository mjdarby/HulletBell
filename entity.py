import pygame, math
import drawable
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
  def __init__(self):
    super(Entity, self).__init__(60, 60)
    self.hitbox = None # TODO this should be a hitbox
    self.collidable = True
    self.xvel = 0
    self.yvel = 0
    self.angle = math.radians(315)
    self.speed = 2
    self.bounds = Bounds(GAMEOFFSET, GAMEOFFSET, GAMEXWIDTH, GAMEYWIDTH)

  def update(self):
    self._updateMovement()

  def isCollide(self, other):
    return self.collidable and other.hitbox.colliderect(self.hitbox)

  def collide(self, other):
    print "Collided!"

  def _updateMovement(self):
    # Update velocities according to angle and speed
    self.xvel = math.cos(self.angle) * self.speed
    self.yvel = -math.sin(self.angle) * self.speed

    # Move by X
    self.hitbox.x += self.xvel
    # Move by Y
    self.hitbox.y += self.yvel

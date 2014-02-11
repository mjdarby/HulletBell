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
    super(Entity, self).__init__(0, 0)

    # Set by script
    # NOTE: Also set in derived class inits as part of development and testing
    # Example: self.hp is set in Enemy and Boss, but won't be eventually
    self.x = 0
    self.y = 0
    self.angle = 0
    self.speed = 0
    self.hp = 1
    self.collisionDamage = 1 # TODO: Make this modifiable by script

    # Calculated by game logic
    self.hitbox = Hitbox(self.x, self.y, 5, 5)
    self.collidable = True # Entity can call 'collide' on others, also settable by script
    self.dead = False # Remove from screen on next update?
    self.xvel = 0
    self.yvel = 0

    # Bounds stuff
    self.boundsChecked = True # Call die() if out of bounds
    self.bounds = Bounds(GAMEOFFSET, GAMEOFFSET, GAMEXWIDTH, GAMEYWIDTH)
    self.bounds.inflate_ip(50, 50) # Default bounds for non-players

    # Reference to parent handler allowing for some crazy script stuff
    self.handler = handler

    # Scripting stuff
    self.scripter = scripting.EntityScripter()
    self.scripter.setEntity(self)

    # Graphical stuff
    # TODO: Do the animation stuff and remove this approach
    self.image = pygame.Surface((self.hitbox.w, self.hitbox.h))
    self.image.fill((0,255,0))


  def update(self):
    self._runScript()
    self._updateMovement()
    self._special()

    # Kill on OOB or no health
    if (self.boundsChecked and not self.bounds.contains(self.hitbox)) or self.hp <= 0:
      self.die()

  def isCollide(self, other):
    return self.collidable and other.collidable and other.hitbox.colliderect(self.hitbox)

  def collide(self, other):
    # TODO: This needs to be more generic, so you don't just necessarily
    # deal damage. Also, takeDamage? At least we're not directly
    # modifying variables, geez.
    other.takeDamage(self.collisionDamage)

  def takeDamage(self, damage):
    self.hp -= damage

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
    # TODO: Animation before setting self.dead! Also stop the script from 
    # continuing if necessary
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

class Player(Entity):
  def __init__(self, handler):
    super(Player, self).__init__(handler)
    self.x = 0
    self.y = 0
    self.hitbox = Hitbox(0, 0, 20, 20)
    self.image = pygame.Surface((self.hitbox.w, self.hitbox.h))
    self.image.fill((0,255,0))

    self.collisionDamage = 0

    # Players are more strictly bounded than other entities
    self.bounds = Bounds(GAMEOFFSET, GAMEOFFSET, GAMEXWIDTH, GAMEYWIDTH)

  def _updateMovement(self):
    # Move by X
    self.x += self.xvel
    self.hitbox.x = math.floor(self.x)
    # Move by Y
    self.y += self.yvel
    self.hitbox.y = math.floor(self.y)

    if not self.bounds.contains(self.hitbox):
      # The hitbox has left the area! Put it back!
      self.hitbox.clamp_ip(self.bounds)
      (self.x, self.y) = (self.hitbox.x, self.hitbox.y)

    # Reset velocity
    self.xvel = 0
    self.yvel = 0

class Enemy(Entity):
  def __init__(self, handler):
    super(Enemy, self).__init__(handler)
    self.x = 60
    self.y = 60
    self.hitbox = Hitbox(self.x, self.y, 20, 20)
    self.angle = 0
    self.image = pygame.Surface((self.hitbox.w, self.hitbox.h))
    self.image.fill((255,0,0))

    self.hp = 4

class Bullet(Entity):
  def __init__(self, handler):
    super(Bullet, self).__init__(handler)
    self.x = 300
    self.y = 300
    self.hitbox = Hitbox(self.x, self.y, 5, 5)
    self.angle = math.radians(1)
    self.speed = 2
    self.image = pygame.Surface((self.hitbox.w, self.hitbox.h))
    self.image.fill((223,0,255))

  def collide(self, other):
    super(Bullet, self).collide(other)
    # Bullets (always?) die on impact
    # Usually they're be killed due to collision damage with enemy
    # but the player may not do damage on collision.
    self.die()

class Boss(Enemy):
  def __init__(self, handler):
    super(Boss, self).__init__(handler)
    self.image = pygame.Surface((self.hitbox.w, self.hitbox.h))
    self.image.fill((225,255,0))
    self.boundsChecked = False
    self.hp = 0
    self.scriptHp = None

    # While technically any entity will be able to have any number
    # of scripters (by virtue of chaining them, eventually),
    # we can simplify things for bosses because they will regularly have to
    # change scripts at certain HP values and times.
    self.scripters = []
    # If a script should stop running at a certain HP value, set a positive value
    self.scriptHps = []
    # If a script should time out after a certain amount of time, set a positive value
    self.scriptTimeouts = []

    # Timing and script counters
    self.currentFrame = 0
    self.currentScripter = 0
    self.totalScripters = 0

  def takeDamage(self, damage):
    if self.hp is not None:
      self.hp -= damage
    if self.scriptHp is not None:
      self.scriptHp -= damage

  def checkScripterChange(self):
    if self.scripters:
      timer = self.scriptTimeouts[self.currentScripter]
      hp = self.scriptHp
      if (timer is not None and self.currentFrame > timer) \
        or (hp is not None and hp <= 0):
        try:
          self.currentScripter += 1
          self.scripter = self.scripters[self.currentScripter]
          self.scriptHp = self.scriptHps[self.currentScripter]
        except IndexError:
          self.die() # Kill this boss if he has nothing left

  def addScripter(self, bossAttack):
    scripter = bossAttack.scripter
    scripter.setEntity(self)
    self.scripters.append(scripter)
    self.totalScripters += 1
    self.scriptHps.append(bossAttack.hp)
    self.scriptTimeouts.append(bossAttack.timeout)

    # If the boss has a large health bar rather than several small ones
    # or if it would just be nice to have the total health available
    if self.hp is not None:
      self.hp += bossAttack.hp

    # If this is the first script, set up the initial variables
    if self.totalScripters == 1:
      self.scripter = scripter
      self.scriptHp = bossAttack.hp

  def update(self):
    self._runScript()
    self._updateMovement()
    self._special()

    if self.hp and self.hp <= 0:
      self.die()

    self.checkScripterChange()
    self.currentFrame += 1
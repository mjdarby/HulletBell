import math, copy

class Script(object):
  """Script item superclass"""
  def __init__(self):
    super(Script, self).__init__()

  def execute(self, entity):
    pass

class SetX(Script):
  def __init__(self, entity, x):
    super(SetX, self).__init__()
    self.x = x

  def execute(self, entity):
    entity.x = self.x

class SetY(Script):
  def __init__(self, y):
    super(SetY, self).__init__()
    self.y = y

  def execute(self, entity):
    entity.y = self.y

class Wait(Script):
  def __init__(self):
    super(Wait, self).__init__()

  def execute(self, entity):
    pass

class SetXVel(Script):
  def __init__(self, xvel):
    super(SetXVel, self).__init__()
    self.xvel = xvel

  def execute(self, entity):
    entity.xvel = self.xvel

class SetYVel(Script):
  def __init__(self, yvel):
    super(SetYVel, self).__init__()
    self.yvel = yvel

  def execute(self, entity):
    entity.yvel = self.yvel

class SetDirection(Script):
  def __init__(self, angle):
    super(SetDirection, self).__init__()
    self.angle = angle

  def execute(self, entity):
    entity.angle = self.angle

class SetSpeed(Script):
  def __init__(self, speed):
    super(SetSpeed, self).__init__()
    self.speed = speed

  def execute(self, entity):
    entity.speed = self.speed

class Shoot(Script):
  def __init__(self, angle, speed, bulletScripter = None):
    super(Shoot, self).__init__()
    self.angle = angle
    self.speed = speed
    self.bulletScripter = bulletScripter

  def execute(self, entity):
    handler = entity.handler
    bullet = handler.createBullet()
    bullet.angle = self.angle
    bullet.speed = self.speed
    bullet.hitbox.centerx = entity.hitbox.centerx # TODO: Should be an offset from the center
    bullet.hitbox.centery = entity.hitbox.centery # TODO: Should be an offset from the center
    bullet.x = bullet.hitbox.x
    bullet.y = bullet.hitbox.y
    if self.bulletScripter is not None:
      # Copy in the passed script because it may be used by other entities
      # Sharing a script = BAD!
      bullet.scripter = copy.copy(self.bulletScripter)
      bullet.scripter.setEntity(bullet)

class ShootAtPlayer(Script):
  def __init__(self, angleOffset, speed, bulletScripter = None):
    super(ShootAtPlayer, self).__init__()
    self.angleOffset = angleOffset
    self.speed = speed
    self.bulletScripter = bulletScripter

  def execute(self, entity):
    handler = entity.handler
    bullet = handler.createBullet()
    # Calculate the angle between the entity and player, if it exists
    # If it doesn't, aim down the screen
    player = handler.player
    if (player):
      deltaX = player.hitbox.centerx - entity.hitbox.centerx
      deltaY = entity.hitbox.centery - player.hitbox.centery
      bullet.angle = math.atan2(deltaY, deltaX) + self.angleOffset
    else:
      bullet.angle = math.PI / 3 + self.angleOffset
    bullet.speed = self.speed
    bullet.hitbox.centerx = entity.hitbox.centerx # TODO: Should be an offset from the center
    bullet.hitbox.centery = entity.hitbox.centery # TODO: Should be an offset from the center
    bullet.x = bullet.hitbox.x
    bullet.y = bullet.hitbox.y
    if self.bulletScripter is not None:
      bullet.scripter = copy.copy(self.bulletScripter)
      bullet.scripter.setEntity(bullet)

# Level stuff
class LevelScript(object):
  def __init__(self, handler):
    super(LevelScript, self).__init__()
    self.handler = handler

  def execute(self):
    pass

class CreateEnemy(LevelScript):
  def __init__(self, handler, enemyScripter = None): # TODO: Take position and script
    super(CreateEnemy, self).__init__(handler)
    # TODO: Populate these
    self.enemyType = None
    self.enemyScripter = enemyScripter

  def execute(self, handler):
    # Create an enemy of type enemyType
    # Give him script enemyScripter
    enemy = handler.createEnemy()
    enemy.setY(200)
    enemy.setX(300)
    enemy.speed = 0
    if self.enemyScripter is not None:
      # Copy in the passed script because it may be used by other entities
      # Sharing a script = BAD!
      enemy.scripter = copy.copy(self.enemyScripter)
      enemy.scripter.setEntity(enemy)

class Scripter(object):
  """Builds scripts for level"""
  def __init__(self):
    super(Scripter, self).__init__()
    self.handler = None
    self.looping = False # Does the script loop?
    self.loopIndex = 0 # Where to loop from
    self.script = []
    self.scriptIndex = 0

  def setLooping(self, looping):
    self.looping = looping

  def setLoopIndex(self, index):
    sellf.loopIndex = index

  def setHandler(self, handler):
    self.handler = handler

  def execute(self):
    if self.scriptIndex < len(self.script):
      for script in self.script[self.scriptIndex]:
        script.execute(self.handler)
      self.scriptIndex += 1
    elif self.looping:
      self.scriptIndex = 0

  # Script creation functions
  def addWait(self, frames):
    for _ in range(frames):
      self.script.append((Wait(),))

  def addScript(self, *scripts):
    """Add scripts to be parsed on frame (len(handler.scripts))"""
    self.script.append(scripts)

  def createEnemy(self, enemyType, enemyScripter):
    return CreateEnemy(self.handler, enemyScripter)


class EntityScripter(object):
  """Builds and manages script objects for Entities"""
  def __init__(self):
    super(EntityScripter, self).__init__()
    self.entity = None
    self.looping = False # Does the script loop?
    self.loopIndex = 0 # Where to loop from
    self.script = []
    self.scriptIndex = 0

  def setEntity(self, entity):
    self.entity = entity

  def setLooping(self, looping):
    self.looping = looping

  def setLoopIndex(self, index):
    sellf.loopIndex = index

  def execute(self):
    if self.scriptIndex < len(self.script):
      for script in self.script[self.scriptIndex]:
        script.execute(self.entity)
      self.scriptIndex += 1
    elif self.looping:
      self.scriptIndex = 0

  def addScript(self, *scripts):
    """Add scripts to be parsed on frame (len(entity.scripts))"""
    self.script.append(scripts)

  def addWait(self, frames):
    for _ in range(frames):
      self.script.append((Wait(),))

  def setX(self, x):
    return SetX(x)

  def setY(self, y):
    return SetY(y)

  def setXVel(self, xvel):
    return SetXVel(xvel)

  def setYVel(self, yvel):
    return SetYVel(yvel)

  def setDirection(self, angle):
    return SetDirection(angle)

  def setSpeed(self, speed):
    return SetSpeed(speed)

  def shoot(self, angle, speed, bulletScripter = None):
    return Shoot(angle, speed, bulletScripter)

  def shootAtPlayer(self, offsetAngle, speed, bulletScripter = None):
    return ShootAtPlayer(offsetAngle, speed, bulletScripter)

import math

class Script(object):
  """Script item superclass"""
  def __init__(self, entity):
    super(Script, self).__init__()
    self.entity = entity

  def execute(self):
    pass

class SetX(Script):
  def __init__(self, entity, x):
    super(SetX, self).__init__(entity)
    self.x = x

  def execute(self):
    self.entity.x = self.x

class SetY(Script):
  def __init__(self, entity, y):
    super(SetY, self).__init__(entity)
    self.y = y

  def execute(self):
    self.entity.y = self.y

class Wait(Script):
  def __init__(self, entity):
    super(Wait, self).__init__(entity)

  def execute(self):
    pass

class SetXVel(Script):
  def __init__(self, entity, xvel):
    super(SetXVel, self).__init__(entity)
    self.xvel = xvel

  def execute(self):
    self.entity.xvel = self.xvel

class SetYVel(Script):
  def __init__(self, entity, yvel):
    super(SetYVel, self).__init__(entity)
    self.yvel = yvel

  def execute(self):
    self.entity.yvel = self.yvel

class SetDirection(Script):
  def __init__(self, entity, angle):
    super(SetDirection, self).__init__(entity)
    self.angle = angle

  def execute(self):
    self.entity.angle = self.angle

class SetSpeed(Script):
  def __init__(self, entity, speed):
    super(SetSpeed, self).__init__(entity)
    self.speed = speed

  def execute(self):
    self.entity.speed = self.speed

class Shoot(Script):
  def __init__(self, entity, angle, speed):
    super(Shoot, self).__init__(entity)
    self.handler = entity.handler
    self.angle = angle
    self.speed = speed

  def execute(self):
    bullet = self.handler.createBullet()
    bullet.angle = self.angle
    bullet.speed = self.speed
    bullet.x = self.entity.x # TODO: Should be an offset from the center
    bullet.y = self.entity.y # TODO: Should be an offset from the center

# Level stuff
class LevelScript(object):
  def __init__(self, handler):
    super(LevelScript, self).__init__()
    self.handler = handler

  def execute(self):
    pass

class CreateEnemy(LevelScript):
  def __init__(self, handler): # TODO: Take position and script
    super(CreateEnemy, self).__init__(handler)
    # TODO: Populate these
    self.enemyType = None
    self.enemyScripter = None

  def execute(self):
    # Create an enemy of type enemyType
    # Give him script enemyScripter
    enemy = self.handler.createEnemy()
    enemy.setY(200)

    # TEST SCRIPT
    scripter = EntityScripter(enemy)
    scripter.setLooping(True)
    # TODO REMOVE: Test code for scripting!
    for i in range(360):
      if i % 2 == 0:
        scripter.addScript(scripter.setDirection(math.radians(i)))
    scripter.addScript(scripter.shoot(enemy.angle, 2))
    scripter.addWait(60)
    enemy.scripter = scripter

class Scripter(object):
  """Builds scripts for level"""
  def __init__(self, handler):
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

  def addScript(self, *scripts):
    """Add scripts to be parsed on frame (len(handler.scripts))"""
    self.script.append(scripts)

  def execute(self):
    if self.scriptIndex < len(self.script):
      for script in self.script[self.scriptIndex]:
        script.execute()
      self.scriptIndex += 1
    elif self.looping:
      self.scriptIndex = 0

  def createEnemy(self, enemyType, enemyScripter):
    return CreateEnemy(self.handler)


class EntityScripter(object):
  """Builds and manages script objects for Entities"""
  def __init__(self, entity):
    super(EntityScripter, self).__init__()
    self.entity = entity
    self.looping = False # Does the script loop?
    self.loopIndex = 0 # Where to loop from
    self.script = []
    self.scriptIndex = 0

  def setLooping(self, looping):
    self.looping = looping

  def setLoopIndex(self, index):
    sellf.loopIndex = index

  def execute(self):
    if self.scriptIndex < len(self.script):
      for script in self.script[self.scriptIndex]:
        script.execute()
      self.scriptIndex += 1
    elif self.looping:
      self.scriptIndex = 0

  def addScript(self, *scripts):
    """Add scripts to be parsed on frame (len(entity.scripts))"""
    self.script.append(scripts)

  def addWait(self, frames):
    for _ in range(frames):
      self.script.append((Wait(self.entity),))

  def setX(self, x):
    return SetX(self.entity, x)

  def setY(self, y):
    return SetY(self.entity, y)

  def setXVel(self, xvel):
    return SetXVel(self.entity, xvel)

  def setYVel(self, yvel):
    return SetYVel(self.entity, yvel)

  def setDirection(self, angle):
    return SetDirection(self.entity, angle)

  def setSpeed(self, speed):
    return SetSpeed(self.entity, speed)

  def shoot(self, angle, speed):
    return Shoot(self.entity, angle, speed)

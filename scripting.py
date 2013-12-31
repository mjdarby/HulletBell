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
    super(SetX, self).__init__(entity)
    
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
    super(SetYVel, self).__init__(entity)
    self.angle = angle
    
  def execute(self):
    self.entity.angle = self.angle

class SetSpeed(Script):
  def __init__(self, entity, speed):
    super(SetSpeed, self).__init__(entity)
    self.speed = speed
    
  def execute(self):
    self.entity.speed = self.speed
    
class Scripter(object):
  """Builds script objects for Entities"""
  def __init__(self, entity):
    super(Scripter, self).__init__()
    self.entity = entity

  def setX(self, x):
    return SetX(self.entity, x)

  def setY(self, y):
    return SetY(self.entity, y)

  def setXVel(self, xvel):
    return SetXVel(self.entity, xvel)

  def setYVel(self, yvel):
    return SetYVel(self.entity, yvel)
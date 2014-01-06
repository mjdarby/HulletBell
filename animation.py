import pygame

# Need to code
# Animation frames
# Animation advancement
# Reset animations

class Frame(object):
  def __init__(self, arg):
    super(Frame, self).__init__()
    self.topY = 0
    self.leftX = 0

class Animation(object):
  def __init__(self):
    self.frames = None
    self.currentFrame = 0
    self.totalFrames = 50
    self.looping = False
    self.loopFrame = 0

    # Size of one frame
    self.width = 50
    self.height = 50

  def advanceFrame(self):
    self.currentFrame += 1
    if self.totalFrames < self.currentFrame:
      if self.looping:
        self.currentFrame = self.loopFrame
      else: # Undo frame change
        self.currentFrame -= 1
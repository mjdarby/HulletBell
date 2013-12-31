import pygame

class InputCallback:
  def __init__(self, key, callback):
    self.key = key
    self.callback = callback

class InputHandler:
  def __init__(self):
    self.keydownCallbacks = []
    self.keyupCallbacks = []
    self.perframeCallbacks = []
    self.quitCallback = None

  def update(self):
    # Run event-based callbacks
    events = pygame.event.get()
    for event in events:
      if event.type == pygame.KEYDOWN:
        for keydownCallback in self.keydownCallbacks:
          if keydownCallback.key == event.key:
            keydownCallback.callback()
      elif event.type == pygame.KEYUP:
        for keyupCallback in self.keyupCallbacks:
          if keyupCallback.key == event.key:
            keyupCallback.callback()
      elif event.type == pygame.QUIT:
        if self.quitCallback:
          self.quitCallback.callback()

    # Run keystate-based callbacks
    keystates = pygame.key.get_pressed()
    for perframeCallback in self.perframeCallbacks:
      if keystates[perframeCallback.key]:
        perframeCallback.callback()

  def addEventCallback(self, callback, key, event):
    inputCallback = InputCallback(key, callback)
    if event == pygame.KEYDOWN:
      self.keydownCallbacks.append(inputCallback)
    elif event == pygame.KEYUP:
      self.keyupCallbacks.append(inputCallback)

  def setQuitCallback(self, callback):
    inputCallback = InputCallback(None, callback)
    self.quitCallback = inputCallback

  def addPerFrameCallback(self, callback, key):
    inputCallback = InputCallback(key, callback)
    self.perframeCallbacks.append(inputCallback)
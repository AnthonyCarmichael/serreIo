import board
import digitalio


class relai:
    
    def __init__(self):
        self = digitalio.DigitalInOut(board.IO13)
        self.direction = digitalio.Direction.OUTPUT
        self.value = True #True = fermé

    def setState(self,state):
        self.value = state

    def alternateState(self):
        self.value = not self.value

    def state(self):
        return self.value
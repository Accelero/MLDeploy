from abc import ABC, abstractmethod
import time
import math
import random
import keyboard

"""
Sampler have to implement the sample() method, which takes atleast the a unix time stamp and returns a sample.  
"""

class Sampler(ABC):

    @abstractmethod
    def sample(self):
        pass

class SineSampler(Sampler):
    def __init__(self, ampl=1, freq=1, phase=0, offset=0, noise=0):
        self.ampl = ampl
        self.freq = freq
        self.base_freq = freq
        self.phase = phase
        self.offset = offset
        self.noise = noise
        self.prev_state = (0, phase)
        self.attack = 10
        self.strength = 2

    def sample(self, time):
        
        if keyboard.is_pressed('a'):
            self.freq = min(self.freq + self.attack * (time - self.prev_state[0]), self.strength * self.base_freq)
        else: 
            self.freq = max(self.freq - self.attack * (time - self.prev_state[0]), self.base_freq)

        '''
        Move the signal interval up/down by pressing the "u"/"d" key.
        '''
        if keyboard.is_pressed('u'):
            self.offset = self.offset + 2

        if keyboard.is_pressed('d'):
            self.offset = self.offset - 2

        phase = (time - self.prev_state[0]) * 2 * math.pi * self.freq + self.prev_state[1]
        self.prev_state = (time, phase)
        signal = self.ampl * math.sin(phase) + self.offset
        noise = random.uniform(-self.noise, self.noise)
        sample_value = signal + noise
        return sample_value





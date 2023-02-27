import math
import numpy as np
from rsa import sign
from effects.base import BaseEffect

class TremoloEffect(BaseEffect):
    def __init__(self, sample_rate=44100, freq=10, min_amp=0.5):
        super().__init__(sample_rate)
        self.tremolo_frequency = freq
        self.tremolo_min_amp=min_amp
        self.tremolo_max_amp=1.0

        self._iteration = 0
        self._step = (2 * math.pi * self.tremolo_frequency) / self._sample_rate

    def apply(self, signal):
        processed_signal = signal.copy()
        processed_signal /= np.max(np.abs(processed_signal), axis=0)
        for i in range(processed_signal.shape[0]):
            tremolo_val = math.cos(self._iteration)
            tremolo_val = (tremolo_val + 1.0) / 2 * (self.tremolo_max_amp - self.tremolo_min_amp) + self.tremolo_min_amp
            self._iteration += self._step
            processed_signal[i] *= tremolo_val
        return processed_signal

    def get_tremolo_wave(self, N):
        tremolo_wave = np.zeros(N)
        for i in range(tremolo_wave.shape[0]):
            tremolo_val = math.cos(self._iteration)
            tremolo_val = (tremolo_val + 1.0) / 2 * (self.tremolo_max_amp - self.tremolo_min_amp) + self.tremolo_min_amp
            self._iteration += self._step
            tremolo_wave[i] = tremolo_val
        return tremolo_wave
             


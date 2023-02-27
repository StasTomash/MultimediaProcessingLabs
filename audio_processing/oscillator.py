from abc import abstractmethod
import math


class BaseOscillator:
    def __init__(self, frequency=440.0, phase=0.0, amplitude=1.0, sample_rate=44100):
        self.initial_frequency = frequency
        self.initial_phase = phase
        self.initial_amplitude = amplitude
        self.sample_rate = sample_rate

        self._freq = frequency
        self._phase = phase
        self._amp = amplitude

    @abstractmethod
    def _initialize_oscillation():
        pass

    @abstractmethod
    def __next__(self) -> float:
        return 0.0

    def __iter__(self):
        self._freq = self.initial_frequency
        self._phase = self.initial_phase
        self._amp = self.initial_amplitude
        self._initialize_oscillation()
        return self

class SineOscillator(BaseOscillator):
    def __init__(self, frequency=440.0, phase=0.0, amplitude=1.0, sample_rate=44100):
        super().__init__(frequency=frequency, phase=phase, amplitude=amplitude, sample_rate=sample_rate)
        
        self._iteration = 0
        self._step = 0

    def _initialize_oscillation(self):
        self._iteration = 0
        self._step = (2 * math.pi * self.initial_frequency) / self.sample_rate
        self._phase = (self.initial_phase / 360) * 2 * math.pi

    def __next__(self):
        val = math.sin(self._iteration + self._phase)
        self._iteration += self._step
        return val * self._amp


class SquareOscillator(SineOscillator):
    def __init__(self, frequency=440.0, phase=0.0, amplitude=1.0, sample_rate=44100, threshold=0):
        super().__init__(frequency=frequency, phase=phase, amplitude=amplitude, sample_rate=sample_rate)
        
        self._threshold = threshold

    def __next__(self):
        val = math.sin(self._iteration + self._phase)
        self._iteration += self._step
        if val < self._threshold:
            val = -1
        else:
            val = 1
        return val * self._amp
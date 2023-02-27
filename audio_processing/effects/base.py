import rir_generator as rir
from abc import abstractmethod
from typing import Iterator, List, Optional
from oscillator import BaseOscillator

class BaseEffect:
    def __init__(self, sample_rate=44100):
        self._sample_rate = sample_rate

    @abstractmethod
    def apply(self, signal):
        pass
    
    @abstractmethod
    def get_one_val(self, signal) -> float:
        return 0.0

class OscillatorWithEffects:
    def __init__(self, base_oscillator: BaseOscillator) -> None:
        self._oscillator: BaseOscillator = base_oscillator
        self._oscillator_iterator: Optional[Iterator] = None
        self._effects: List[BaseEffect] = []
        self._memory: List[List[float]] = []

    def add_effect(self, effect: BaseEffect) -> None:
        self._effects.append(effect)
        self._memory.append([])

    def __next__(self) -> float:
        if self._oscillator_iterator is None:
            raise ValueError
        val: float = next(self._oscillator_iterator)
        for effect, effect_memory in zip(self._effects, self._memory):
            effect_memory.append(val)
            val = effect.get_one_val(effect_memory)
        return val

    def __iter__(self):
        self._oscillator_iterator = iter(self._oscillator)
        return self
from abc import abstractmethod
from typing import List

import scipy
import scipy.signal
from effects.base import BaseEffect
import rir_generator as rir
import numpy as np

class ReverbSource:
    def __init__(self):
        pass
    
    @abstractmethod
    def get_impulse_response_signal(self, reverb_time, sample_rate) -> np.ndarray:
        raise NotImplementedError

class ReverbRoom(ReverbSource):
    def __init__(
        self,
        microphone_position: List[float],   # [x, y, z]
        source_position: List[float],        # [x, y, z]
        room_dimensions: List[float],        # [x, y, z]
        sound_speed: float = 343.0,
    ):
        self._microphone_positions = [microphone_position]
        self._source_positions = source_position
        self._room_dimensions = room_dimensions
        self._sound_speed = sound_speed

    def get_impulse_response_signal(self, reverb_time, sample_rate) -> np.ndarray:
        return rir.generate(
            c=self._sound_speed,
            fs=sample_rate,
            r=self._microphone_positions,
            s=self._source_positions,
            L=self._room_dimensions,
            reverberation_time=reverb_time
        )

SMALL_ROOM_REVERB = ReverbRoom([1, 1, 1], [1, 0.1, 1], [2, 2, 2])
MEDIUM_ROOM_REVERB = ReverbRoom([4, 4, 1.5], [4.2, 0.1, 1.5], [8, 6, 2.5])
LARGE_ROOM_REVERB = ReverbRoom([10, 10, 2], [10, 0.1, 2], [20, 25, 5])
ARENA_REVERB = ReverbRoom([30, 15, 4], [32, 0.1, 4], [50, 50, 10])

class ReverbEffect(BaseEffect):
    def __init__(self, reverb_source: ReverbSource, sample_rate=44100, reverb_time=0.1):
        super().__init__(sample_rate=sample_rate)
        self._reverb_time = reverb_time
        self._impulse_response: np.ndarray = reverb_source.get_impulse_response_signal(self._reverb_time, self._sample_rate)

    def apply(self, signal):
        reverbed_signal = scipy.signal.convolve(self._impulse_response[:, None, :], signal[:, :, None])
        reverbed_signal = np.squeeze(reverbed_signal)
        reverbed_signal /= np.max(np.abs(reverbed_signal), axis=0)
        return reverbed_signal
    
    def get_one_val(self, signal) -> float:
        raise NotImplementedError
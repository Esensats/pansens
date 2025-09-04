#!/usr/bin/env python3
from abc import ABC, abstractmethod
from typing import override
import argparse


# Neutral representation
class IntermediateSensitivity:
    def __init__(self, multiplier: float):
        self.multiplier: float = multiplier

    @override
    def __repr__(self):
        return f"IntermediateSensitivity(multiplier={self.multiplier})"


# Sensitivity value interface
class Sensitivity(ABC):
    @abstractmethod
    @override
    def __repr__(self) -> str: ...


# Platform interface
class SensitivityPlatform(ABC):
    @abstractmethod
    def to_intermediate(self, sensitivity: Sensitivity) -> IntermediateSensitivity: ...

    @abstractmethod
    def from_intermediate(
        self, sensitivity: IntermediateSensitivity
    ) -> Sensitivity: ...


# --- Windows implementation ---
class WindowsSensitivity(Sensitivity):
    def __init__(self, tick: int):
        if not (1 <= tick <= 20):
            raise ValueError("Windows tick must be 1–20")
        self.tick: int = tick

    @override
    def __repr__(self):
        return f"WindowsSensitivity(tick={self.tick})"


class WindowsPlatform(SensitivityPlatform):
    # Mapping from tick → multiplier (as per Windows spec)
    _tick_map: dict[int, float] = {
        1: 1 / 32,
        2: 1 / 16,
        3: 1 / 8,
        4: 2 / 8,
        5: 3 / 8,
        6: 4 / 8,
        7: 5 / 8,
        8: 6 / 8,
        9: 7 / 8,
        10: 1.0,
        11: 1.25,
        12: 1.5,
        13: 1.75,
        14: 2.0,
        15: 2.25,
        16: 2.5,
        17: 2.75,
        18: 3.0,
        19: 3.25,
        20: 3.5,
    }

    @override
    def to_intermediate(self, sensitivity: Sensitivity) -> IntermediateSensitivity:
        if not isinstance(sensitivity, WindowsSensitivity):
            raise TypeError("Expected WindowsSensitivity")
        return IntermediateSensitivity(self._tick_map[sensitivity.tick])

    @override
    def from_intermediate(
        self, sensitivity: IntermediateSensitivity
    ) -> WindowsSensitivity:
        # Pick closest tick to multiplier
        closest = min(
            self._tick_map.items(), key=lambda kv: abs(kv[1] - sensitivity.multiplier)
        )
        return WindowsSensitivity(closest[0])


# --- KDE implementation ---
class KDESensitivity(Sensitivity):
    def __init__(self, value: float):
        if not (-1.0 <= value <= 1.0):
            raise ValueError("KDE/libinput pointerAcceleration must be in [-1.0, 1.0]")
        self.value: float = value

    @override
    def __repr__(self):
        return f"KDESensitivity(value={self.value})"


class KDEPlatform(SensitivityPlatform):
    @override
    def to_intermediate(self, sensitivity: Sensitivity) -> IntermediateSensitivity:
        if not isinstance(sensitivity, KDESensitivity):
            raise TypeError("Expected KDESensitivity")
        # Approximate: KDE –1.0→0x, 0→1x, +1.0→2x scaling
        multiplier = 1.0 + sensitivity.value
        return IntermediateSensitivity(multiplier)

    @override
    def from_intermediate(self, sensitivity: IntermediateSensitivity) -> KDESensitivity:
        # Invert the mapping: multiplier ∈ [0, 2]
        val = sensitivity.multiplier - 1.0
        val = max(-1.0, min(1.0, val))  # clamp
        return KDESensitivity(val)


# --- Conversion function ---
def convert_sensitivity(
    from_platform: SensitivityPlatform,
    to_platform: SensitivityPlatform,
    sensitivity: Sensitivity,
) -> Sensitivity:
    intermediate = from_platform.to_intermediate(sensitivity)
    return to_platform.from_intermediate(intermediate)

def main():
    parser = argparse.ArgumentParser(description="Convert mouse sensitivity between platforms.")
    _ = parser.add_argument("from_platform", choices=["windows", "kde"], help="Source platform")
    _ = parser.add_argument("to_platform", choices=["windows", "kde"], help="Target platform")
    _ = parser.add_argument("value", type=float, help="Sensitivity value (tick for Windows, float for KDE)")

    args = parser.parse_args()

    # Initialize platforms
    platforms = {
        "windows": WindowsPlatform(),
        "kde": KDEPlatform(),
    }

    from_platform = platforms[args.from_platform]
    to_platform = platforms[args.to_platform]

    # Create sensitivity object based on input
    if args.from_platform == "windows":
        sensitivity = WindowsSensitivity(int(args.value))
    else:  # kde
        sensitivity = KDESensitivity(args.value)

    # Perform conversion
    converted = convert_sensitivity(from_platform, to_platform, sensitivity)
    print(f"Converted sensitivity: {converted}")

if __name__ == "__main__":
    main()

# # --- Example usage ---
# if __name__ == "__main__":
#     windows = WindowsPlatform()
#     kde = KDEPlatform()
#
#     w_sens = WindowsSensitivity(12)  # Windows tick 12 (1.5x)
#     print("Windows input:", w_sens)
#
#     kde_equiv = convert_sensitivity(windows, kde, w_sens)
#     print("Converted to KDE:", kde_equiv)
#
#     back_to_windows = convert_sensitivity(kde, windows, kde_equiv)
#     print("Back to Windows:", back_to_windows)

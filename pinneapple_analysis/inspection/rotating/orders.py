"""Order tracking from a once-per-revolution tachometer: shaft angle, speed and the complex phasor of each order.

The tachometer gives one pulse per revolution. The shaft angle is ``2 pi i`` at the ``i``-th rising edge (edge times
refined by linear interpolation between samples) and is interpolated linearly in between, so the angle follows the
small speed fluctuations of the run. The phasor of order ``k`` on a channel ``x(t)`` is the synchronous demodulation

    X_k = (2 / N) sum_n x(t_n) exp(-i k theta(t_n))

over the samples between the first and the last pulse (a whole number of revolutions, so a component that is
periodic in the shaft angle at order ``k`` is captured without leakage, whatever the speed). Its phase is referred to
the tachometer pulse, which is what lets responses of different runs be added and subtracted as vectors (the
influence-coefficient method of rotor balancing).

Resolution: a record of ``R`` revolutions separates orders that differ by more than about ``1 / R``. For five
seconds at 30 Hz (150 revolutions) that is 0.007 orders, so a bearing order of 2.998 cannot be told apart from 3X
by a phasor or an FFT of the record; :func:`order_resolution` reports it.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class ShaftAngle:
    """Shaft angle of every sample inside the revolutions spanned by the pulses."""
    theta: np.ndarray          # rad, one value per sample in [first, last)
    first: int                 # index of the first sample used
    last: int                  # index one past the last sample used
    pulse_times_s: np.ndarray
    speed_hz: float            # mean shaft speed over the whole revolutions
    speed_cv: float            # coefficient of variation of the revolution periods
    revolutions: int


def pulse_times(tach: np.ndarray, fs: float, threshold: float | None = None) -> np.ndarray:
    """Rising-edge times (s) of a pulse tachometer, refined by linear interpolation; ``threshold`` defaults to the
    middle of the signal's range."""
    tach = np.asarray(tach, float)
    th = 0.5 * (np.max(tach) + np.min(tach)) if threshold is None else float(threshold)
    i = np.flatnonzero((tach[:-1] < th) & (tach[1:] >= th))
    frac = (th - tach[i]) / np.maximum(tach[i + 1] - tach[i], 1e-300)
    return (i + frac) / fs


def shaft_angle(tach: np.ndarray, fs: float, threshold: float | None = None) -> ShaftAngle:
    """Shaft angle from a once-per-revolution tachometer (see the module docstring)."""
    tp = pulse_times(tach, fs, threshold)
    if len(tp) < 3:
        raise ValueError(f"only {len(tp)} tachometer pulses: cannot track the shaft angle")
    periods = np.diff(tp)
    t = np.arange(len(tach)) / fs
    first = int(np.ceil(tp[0] * fs))
    last = int(np.floor(tp[-1] * fs)) + 1
    theta = np.interp(t[first:last], tp, 2 * np.pi * np.arange(len(tp)))
    return ShaftAngle(theta=theta, first=first, last=last, pulse_times_s=tp, speed_hz=float(1.0 / periods.mean()),
                      speed_cv=float(periods.std() / periods.mean()), revolutions=len(tp) - 1)


def order_phasors(x: np.ndarray, angle: ShaftAngle, orders=(1, 2, 3)) -> np.ndarray:
    """Complex phasors (amplitude in the channel's unit, phase against the pulse) of each order on each channel:
    ``x`` (n_samples,) or (n_samples, n_channels); returns (len(orders), n_channels)."""
    x = np.asarray(x, float)
    x = x[:, None] if x.ndim == 1 else x
    seg = x[angle.first:angle.last]
    seg = seg - seg.mean(0)
    out = np.empty((len(orders), x.shape[1]), complex)
    for j, k in enumerate(orders):
        out[j] = 2.0 / len(seg) * (np.exp(-1j * k * angle.theta) @ seg)
    return out


def order_resolution(angle: ShaftAngle) -> float:
    """Smallest order separation a record of this length resolves (about 1 / revolutions)."""
    return 1.0 / angle.revolutions

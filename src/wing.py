"""Hình học cánh hình thang và tích phân kép diện tích.

Phần Trương Thanh Vĩ. Hệ tọa độ: x theo dây cung, y theo sải, z hướng lên.
# AI-assisted: xem AI_DECLARATION.md
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
from scipy import integrate

from .airfoil import (naca4_camber, naca4_thickness,
                      naca4_thickness_derivative, parse_naca4)


def _dimensions(b: float, c_root: float, c_tip: float) -> None:
    if b <= 0 or c_root <= 0 or c_tip <= 0:
        raise ValueError("Sải cánh và hai dây cung phải dương.")


def chord_distribution(y: np.ndarray | float, b: float, c_root: float,
                       c_tip: float) -> np.ndarray | float:
    """Dây cung c(y) [m] ở tọa độ sải y [m], -b/2 <= y <= b/2."""
    _dimensions(b, c_root, c_tip)
    v = np.asarray(y, dtype=float)
    if np.any(np.abs(v) > b / 2 + 1e-10):
        raise ValueError("y nằm ngoài sải cánh.")
    c = c_root - (c_root - c_tip) * np.abs(v) / (b / 2)
    return float(c) if c.ndim == 0 else c


def wing_surface(
    u: np.ndarray | float, v: np.ndarray | float, b: float,
    c_root: float, c_tip: float, naca_code: str = "2412",
    surface_type: str = "upper"
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Trả về (X,Y,Z) [m] trên mặt cánh tại u=x/c∈[0,1], v=y∈[-b/2,b/2]."""
    if surface_type not in ("upper", "lower"):
        raise ValueError("surface_type phải là 'upper' hoặc 'lower'.")
    m, p, t = parse_naca4(naca_code)
    u_arr, v_arr = np.broadcast_arrays(np.asarray(u, float), np.asarray(v, float))
    if np.any((u_arr < 0) | (u_arr > 1)):
        raise ValueError("u phải nằm trong [0,1].")
    chord = chord_distribution(v_arr, b, c_root, c_tip)
    camber, _ = naca4_camber(u_arr, m, p)
    sign = 1 if surface_type == "upper" else -1
    z = (camber + sign * naca4_thickness(u_arr, t)) * chord
    return u_arr * chord, v_arr, z


@dataclass(frozen=True)
class WingModel:
    """Bộ chuyển tiếp hình học cánh cho giao diện khí động của Hà Ngọc Khải."""

    span: float
    chord_root: float
    chord_tip: float
    naca_code: str = "2412"

    def __post_init__(self) -> None:
        _dimensions(self.span, self.chord_root, self.chord_tip)
        parse_naca4(self.naca_code)

    @property
    def semi_span(self) -> float:
        return self.span / 2

    def surface(self, u: np.ndarray, v: np.ndarray, side: int):
        """Giao diện aero: side=+1 mặt trên, side=-1 mặt dưới."""
        if side not in (+1, -1):
            raise ValueError("side phải là +1 hoặc -1.")
        return wing_surface(u, v, self.span, self.chord_root,
                            self.chord_tip, self.naca_code,
                            "upper" if side == +1 else "lower")


def calculate_projected_area(b: float, c_root: float, c_tip: float,
                             method: str = "analytical") -> float:
    """Diện tích chiếu S [m²]; 'numerical' tính ∬ c(y) du dy bằng dblquad."""
    _dimensions(b, c_root, c_tip)
    if method == "analytical":
        return (c_root + c_tip) * b / 2
    if method == "numerical":
        value, _ = integrate.dblquad(
            lambda u, y: chord_distribution(y, b, c_root, c_tip),
            -b / 2, b / 2, lambda y: 0.0, lambda y: 1.0,
            epsabs=1e-9, epsrel=1e-9,
        )
        return float(value)
    raise ValueError("method phải là 'analytical' hoặc 'numerical'.")


def _gauss(n: int, a: float, b: float) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.legendre.leggauss(n)
    return (b - a) * nodes / 2 + (a + b) / 2, (b - a) * weights / 2


def calculate_surface_area(
    b: float, c_root: float, c_tip: float, naca_code: str = "2412",
    n_u: int = 200, n_v: int = 100
) -> Dict[str, float]:
    """Diện tích mặt trên/dưới [m²] qua ∬|r_u×r_v|du dv.

    Dùng θ với u=(1-cosθ)/2 để xử lý dốc vô hạn tại mép trước.
    Gauss-Legendre lấy n_u nút theo θ và n_v nút trên nửa sải; nhân đôi.
    """
    _dimensions(b, c_root, c_tip)
    if n_u < 8 or n_v < 8:
        raise ValueError("n_u và n_v phải >= 8.")
    m, p, t = parse_naca4(naca_code)
    theta, w_theta = _gauss(n_u, 0.0, math.pi)
    v, w_v = _gauss(n_v, 0.0, b / 2)
    u = 0.5 * (1 - np.cos(theta))[:, None]
    du_dtheta = 0.5 * np.sin(theta)[:, None]
    chord = chord_distribution(v, b, c_root, c_tip)[None, :]
    chord_prime = -2 * (c_root - c_tip) / b
    yc, dyc = naca4_camber(u, m, p)
    yt = naca4_thickness(u, t)
    dyt = naca4_thickness_derivative(u, t)
    results = {}
    for key, sign in (("area_upper", 1), ("area_lower", -1)):
        z, dz = yc + sign * yt, dyc + sign * dyt
        jac = chord * np.sqrt(1 + dz**2 + chord_prime**2 * (u * dz - z)**2)
        results[key] = float(2 * np.sum(jac * du_dtheta * w_theta[:, None] * w_v[None, :]))
    results["total_surface_area"] = results["area_upper"] + results["area_lower"]
    return results


# ==============================================================================
# BỔ SUNG (Hà Ngọc Khải, 19/11/2026) - cần Vĩ review
# Thể tích khối cánh bằng tích phân bội ba, dùng ở Chương 4 (mục 4.1).
# # AI-assisted: xem AI_DECLARATION.md
# ==============================================================================

def calculate_wing_volume(b: float, c_root: float, c_tip: float, naca_code: str = "2412",
                          method: str = "iterated") -> float:
    """Thể tích khối cánh W [m³] = ∭_W dV, W nằm giữa mặt dưới và mặt trên.

    Với x = u·c(y), z giữa c·z_l(u) và c·z_u(u):
        V = ∫∫∫ dz dx dy = ∫_{-b/2}^{b/2} c(y)² ∫_0^1 (z_u - z_l) du dy
          = ∫ c(y)² dy · 2∫_0^1 y_t(u) du.
    method='iterated'  : tách như trên, mỗi tích phân 1D tính bằng quad.
    method='triple'    : scipy.integrate.tplquad trực tiếp theo (z, x, y).
    """
    _dimensions(b, c_root, c_tip)
    m, p, t = parse_naca4(naca_code)
    if method == "iterated":
        chord_sq = integrate.quad(lambda y: chord_distribution(y, b, c_root, c_tip) ** 2,
                                  -b / 2, b / 2, points=[0.0])[0]
        thick = integrate.quad(lambda u: 2 * naca4_thickness(u, t), 0, 1, limit=200)[0]
        return float(chord_sq * thick)
    if method == "triple":
        def z_bounds(y, x, sign):
            c = chord_distribution(y, b, c_root, c_tip)
            u = min(max(x / c, 0.0), 1.0)
            yc, _ = naca4_camber(u, m, p)
            return c * (yc + sign * naca4_thickness(u, t))
        total = 0.0
        for lo, hi in ((-b / 2, 0.0), (0.0, b / 2)):
            total += integrate.tplquad(
                lambda z, x, y: 1.0, lo, hi,
                lambda y: 0.0, lambda y: chord_distribution(y, b, c_root, c_tip),
                lambda y, x: z_bounds(y, x, -1), lambda y, x: z_bounds(y, x, +1),
                epsabs=1e-7, epsrel=1e-6)[0]
        return float(total)
    raise ValueError("method phải là 'iterated' hoặc 'triple'.")

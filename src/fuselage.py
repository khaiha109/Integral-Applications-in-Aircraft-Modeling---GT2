"""Thân tròn xoay: bán kính, mô hình 3D, thể tích và khối lượng.

Phần Trương Thanh Vĩ. Xem docs/assumptions.md về dạng mũi/đuôi và vỏ.
# AI-assisted: xem AI_DECLARATION.md
"""

from __future__ import annotations

import math
from typing import Dict, Tuple

import numpy as np
from scipy import integrate


def _lengths(length: float, radius_max: float, nose_length: float | None,
             tail_length: float | None) -> tuple[float, float]:
    if length <= 0 or radius_max <= 0:
        raise ValueError("Chiều dài và bán kính thân phải dương.")
    nose = 0.2 * length if nose_length is None else float(nose_length)
    tail = 0.3 * length if tail_length is None else float(tail_length)
    if nose < 0 or tail < 0 or nose + tail > length:
        raise ValueError("Chiều dài mũi/đuôi phải không âm và tổng không vượt quá thân.")
    return nose, tail


def fuselage_radius(x: np.ndarray | float, length: float, radius_max: float,
                    nose_length: float | None = None,
                    tail_length: float | None = None) -> np.ndarray | float:
    """Bán kính r(x) [m] trên [0,L]: mũi sin, thân trụ, đuôi cosine thu về 0."""
    nose, tail = _lengths(length, radius_max, nose_length, tail_length)
    u = np.asarray(x, dtype=float)
    if np.any((u < -1e-12) | (u > length + 1e-12)):
        raise ValueError("x nằm ngoài chiều dài thân.")
    r = np.full_like(u, radius_max)
    if nose > 0:
        r = np.where(u < nose, radius_max * np.sin(math.pi * u / (2 * nose)), r)
    if tail > 0:
        start = length - tail
        r = np.where(u > start, radius_max * (1 + np.cos(math.pi * (u - start) / tail)) / 2, r)
    return float(r) if r.ndim == 0 else r


def fuselage_surface_3d(length: float, radius_max: float, n_x: int = 100,
                        n_theta: int = 60, nose_length: float | None = None,
                        tail_length: float | None = None
                        ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Lưới (X,Y,Z) [m] cho mặt thân tròn xoay; shape=(n_theta,n_x)."""
    if n_x < 3 or n_theta < 8:
        raise ValueError("Cần n_x >= 3 và n_theta >= 8.")
    _lengths(length, radius_max, nose_length, tail_length)
    x = np.linspace(0, length, n_x)
    theta = np.linspace(0, 2 * math.pi, n_theta)
    X, TH = np.meshgrid(x, theta)
    R = fuselage_radius(X, length, radius_max, nose_length, tail_length)
    return X, R * np.cos(TH), R * np.sin(TH)


def analytical_fuselage_volume(length: float, radius_max: float,
                               nose_length: float | None = None,
                               tail_length: float | None = None) -> float:
    """Thể tích thân đặc [m³] theo tích phân đóng của ba đoạn hình học."""
    nose, tail = _lengths(length, radius_max, nose_length, tail_length)
    middle = length - nose - tail
    return math.pi * radius_max**2 * (nose / 2 + middle + 3 * tail / 8)


def calculate_fuselage_volume(
    length: float, radius_max: float, skin_thickness: float = 0.0,
    method: str = "single_integral", nose_length: float | None = None,
    tail_length: float | None = None
) -> Dict[str, float]:
    """Thể tích thân đặc/vỏ [m³] bằng tích phân 1D hoặc tích phân bội ba.

    V_đặc=∭s ds dθ dx; V_vỏ dùng s∈[max(r(x)-t,0),r(x)].
    Khi t=0, volume_skin=0. `triple_integral` dùng scipy.tplquad thật.
    """
    nose, tail = _lengths(length, radius_max, nose_length, tail_length)
    if not 0 <= skin_thickness < radius_max:
        raise ValueError("skin_thickness phải trong [0, radius_max).")
    if method not in ("single_integral", "triple_integral"):
        raise ValueError("method phải là 'single_integral' hoặc 'triple_integral'.")
    bounds = sorted(set((0.0, nose, length - tail, length)))

    def radius(x: float) -> float:
        return fuselage_radius(x, length, radius_max, nose, tail)

    if method == "single_integral":
        solid = sum(integrate.quad(lambda x: math.pi * radius(x)**2, a, b,
                                   epsabs=1e-9)[0]
                    for a, b in zip(bounds[:-1], bounds[1:]))
        skin = 0.0
        if skin_thickness > 0:
            skin = sum(integrate.quad(
                lambda x: math.pi * (radius(x)**2 - max(radius(x) - skin_thickness, 0)**2),
                a, b, epsabs=1e-8, limit=200,
            )[0] for a, b in zip(bounds[:-1], bounds[1:]))
    else:
        def triple(a: float, b: float, inner) -> float:
            return integrate.tplquad(
                lambda s, theta, x: s,
                a, b, lambda x: 0.0, lambda x: 2 * math.pi,
                lambda x, theta: inner(x), lambda x, theta: radius(x),
                epsabs=1e-7, epsrel=1e-7,
            )[0]

        solid = sum(triple(a, b, lambda x: 0.0)
                    for a, b in zip(bounds[:-1], bounds[1:]))
        skin = (sum(triple(a, b, lambda x: max(radius(x) - skin_thickness, 0.0))
                    for a, b in zip(bounds[:-1], bounds[1:]))
                if skin_thickness > 0 else 0.0)
    return {"volume_solid": float(solid), "volume_skin": float(skin)}


def calculate_fuselage_mass(
    length: float, radius_max: float, density: float,
    skin_thickness: float = 0.003, is_hollow: bool = True,
    nose_length: float | None = None, tail_length: float | None = None
) -> float:
    """Khối lượng thân [kg] = mật độ [kg/m³] × thể tích đặc hoặc vỏ [m³]."""
    if density <= 0:
        raise ValueError("density phải dương.")
    volumes = calculate_fuselage_volume(
        length, radius_max, skin_thickness if is_hollow else 0.0,
        nose_length=nose_length, tail_length=tail_length,
    )
    return density * volumes["volume_skin" if is_hollow else "volume_solid"]


# ==============================================================================
# BỔ SUNG (Hà Ngọc Khải, 19/11/2026) - cần Vĩ review
# Diện tích mặt ngoài thân bằng tích phân mặt loại 1, dùng ở Chương 3 (3.13)
# và Chương 4 (mục 4.2). # AI-assisted: xem AI_DECLARATION.md
# ==============================================================================

def fuselage_radius_derivative(x: np.ndarray | float, length: float, radius_max: float,
                               nose_length: float | None = None,
                               tail_length: float | None = None) -> np.ndarray | float:
    """Đạo hàm R'(x) [-] của bán kính thân theo x (giải tích, từng đoạn)."""
    nose, tail = _lengths(length, radius_max, nose_length, tail_length)
    u = np.asarray(x, dtype=float)
    d = np.zeros_like(u)
    if nose > 0:
        d = np.where(u < nose, radius_max * math.pi / (2 * nose)
                     * np.cos(math.pi * u / (2 * nose)), d)
    if tail > 0:
        start = length - tail
        d = np.where(u > start, -radius_max * math.pi / (2 * tail)
                     * np.sin(math.pi * (u - start) / tail), d)
    return float(d) if d.ndim == 0 else d


def calculate_fuselage_surface_area(length: float, radius_max: float,
                                    nose_length: float | None = None,
                                    tail_length: float | None = None,
                                    method: str = "surface_integral") -> float:
    """Diện tích mặt ngoài thân [m²].

    Mặt r(x,θ) = (x, R cosθ, R sinθ) có |r_x × r_θ| = R(x)·sqrt(1 + R'(x)²), nên
        A = ∬ R sqrt(1+R'²) dx dθ = 2π ∫_0^L R sqrt(1+R'²) dx.
    method='surface_integral': dblquad theo (x, θ) đúng định nghĩa tích phân mặt;
    method='single_integral' : quad 1D sau khi đã tích phân θ (để đối chiếu).
    """
    nose, tail = _lengths(length, radius_max, nose_length, tail_length)
    bounds = sorted(set((0.0, nose, length - tail, length)))

    def integrand(x: float) -> float:
        r = fuselage_radius(x, length, radius_max, nose, tail)
        dr = fuselage_radius_derivative(x, length, radius_max, nose, tail)
        return r * math.sqrt(1.0 + dr * dr)

    if method == "single_integral":
        return float(sum(2 * math.pi * integrate.quad(integrand, a, b, epsabs=1e-10)[0]
                         for a, b in zip(bounds[:-1], bounds[1:])))
    if method == "surface_integral":
        return float(sum(integrate.dblquad(lambda theta, x: integrand(x), a, b,
                                           0.0, 2 * math.pi, epsabs=1e-9)[0]
                         for a, b in zip(bounds[:-1], bounds[1:])))
    raise ValueError("method phải là 'surface_integral' hoặc 'single_integral'.")

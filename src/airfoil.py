"""Biên dạng NACA 4 chữ số, tọa độ chuẩn hóa theo dây cung.

Phần hình học do Trương Thanh Vĩ phụ trách. Độ dày được đặt theo phương z
(xấp xỉ thiết diện mỏng), thống nhất với mô hình cánh và tích phân khí động.
# AI-assisted: xem AI_DECLARATION.md
"""

from __future__ import annotations

from typing import Tuple

import numpy as np


def parse_naca4(naca_code: str = "2412") -> Tuple[float, float, float]:
    """Trả về (độ cong m, vị trí cong p, độ dày t), đều theo tỉ lệ dây cung."""
    if not isinstance(naca_code, str) or len(naca_code) != 4 or not naca_code.isascii() or not naca_code.isdigit():
        raise ValueError("Mã NACA phải gồm đúng 4 chữ số ASCII, ví dụ '2412'.")
    m, p, t = int(naca_code[0]) / 100, int(naca_code[1]) / 10, int(naca_code[2:]) / 100
    if t <= 0 or (m > 0 and not 0 < p < 1):
        raise ValueError("Độ dày phải dương; airfoil có độ cong cần 0 < p < 1.")
    return m, p, t


def naca4_thickness(x: np.ndarray | float, t: float = 0.12) -> np.ndarray | float:
    """Nửa độ dày NACA y_t(x), với x và kết quả theo dây cung chuẩn hóa."""
    if t <= 0:
        raise ValueError("t phải dương.")
    u = np.clip(np.asarray(x, dtype=float), 0.0, 1.0)
    y = 5 * t * (0.2969 * np.sqrt(u) - 0.1260 * u - 0.3516 * u**2
                 + 0.2843 * u**3 - 0.1036 * u**4)
    return float(y) if y.ndim == 0 else y


def naca4_thickness_derivative(x: np.ndarray | float, t: float = 0.12) -> np.ndarray | float:
    """Đạo hàm dy_t/dx; mép trước dùng giới hạn x→0+ để tích phân số."""
    if t <= 0:
        raise ValueError("t phải dương.")
    u = np.clip(np.asarray(x, dtype=float), 1e-15, 1.0)
    dy = 5 * t * (0.14845 / np.sqrt(u) - 0.1260 - 0.7032 * u
                  + 0.8529 * u**2 - 0.4144 * u**3)
    return float(dy) if dy.ndim == 0 else dy


def naca4_camber(
    x: np.ndarray | float, m: float = 0.02, p: float = 0.4
) -> Tuple[np.ndarray | float, np.ndarray | float]:
    """Trả về (độ cao camber, đạo hàm theo x) theo dây cung chuẩn hóa."""
    if m < 0 or (m > 0 and not 0 < p < 1):
        raise ValueError("Cần m >= 0 và 0 < p < 1 khi m > 0.")
    u = np.clip(np.asarray(x, dtype=float), 0.0, 1.0)
    if m == 0:
        y = np.zeros_like(u)
        dy = np.zeros_like(u)
    else:
        y = np.where(u < p, m / p**2 * (2 * p * u - u**2),
                     m / (1 - p)**2 * (1 - 2 * p + 2 * p * u - u**2))
        dy = np.where(u < p, 2 * m / p**2 * (p - u),
                      2 * m / (1 - p)**2 * (p - u))
    if y.ndim == 0:
        return float(y), float(dy)
    return y, dy


def get_airfoil_coordinates(
    x: np.ndarray, naca_code: str = "2412"
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Trả về (x_trên, z_trên, x_dưới, z_dưới), chuẩn hóa theo dây cung.

    Cả hai mặt dùng cùng x; cách đặt độ dày theo z khớp với wing_surface().
    """
    m, p, t = parse_naca4(naca_code)
    u = np.clip(np.asarray(x, dtype=float), 0.0, 1.0)
    camber, _ = naca4_camber(u, m, p)
    thickness = naca4_thickness(u, t)
    return u, camber + thickness, u, camber - thickness

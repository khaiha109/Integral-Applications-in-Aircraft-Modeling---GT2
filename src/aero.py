"""
aero.py - Lực nâng và lực cản khí động bằng TÍCH PHÂN MẶT.

    F = - ∬ (p - p_inf) n dS  +  ∬ tau t dS
        (áp suất)               (ma sát bề mặt)

    Nâng  L = F . l_hat ,   Cản  D = F . d_hat
    d_hat = (cos a, 0, sin a)   hướng dòng tự do trong hệ tọa độ cánh
    l_hat = (-sin a, 0, cos a)  vuông góc dòng tự do, hướng lên

Hệ tọa độ cánh: x dọc dây cung (mép trước -> mép sau), y theo sải, z hướng lên.

------------------------------------------------------------------------
GIAO DIỆN VỚI wing.py (Vĩ)
------------------------------------------------------------------------
aero.py chỉ cần một đối tượng `wing` có:

    wing.semi_span : float                     # nửa sải cánh [m]
    wing.surface(u, v, side) -> (X, Y, Z)      # tọa độ điểm trên mặt cánh [m]

  u    : phân số theo dây cung, 0 (mép trước) .. 1 (mép sau)   (mảng numpy)
  v    : tọa độ theo sải y, 0 (gốc) .. semi_span                (mảng numpy, cùng shape với u)
  side : +1 mặt trên, -1 mặt dưới
  X, Y, Z : mảng numpy cùng shape với u, v (hàm phải hỗ trợ vector hóa)

Chỉ tính nửa cánh (v >= 0) rồi nhân đôi do đối xứng. Pháp tuyến và dS được tính
bằng sai phân số từ surface(), nên không cần Vĩ viết sẵn pháp tuyến.

------------------------------------------------------------------------
MÔ HÌNH ÁP SUẤT (giả thiết của bài tập, KHÔNG phải CFD)
------------------------------------------------------------------------
Lý thuyết thiết diện mỏng cho tấm phẳng:
    Delta_Cp(x) = Cp_dưới - Cp_trên = 4 * alpha_e * sqrt((1-x/c)/(x/c))
nên  Cl = 2*pi*alpha_e  với  alpha_e = alpha - alpha_L0.
Cp_trên = -Delta_Cp/2,  Cp_dưới = +Delta_Cp/2 (áp suất dư so với p_inf).
Kỳ dị ở mép trước được khử bằng phép đổi biến u = (1 - cos(theta))/2.

Hiệu chỉnh cho cánh hữu hạn (tùy chọn):  a = a0 / (1 + a0/(pi*e*AR)),  a0 = 2*pi.
Phân bố tải theo sải (tùy chọn): elliptic hoặc đều.
Ma sát: Cf = 1.328/sqrt(Re) (tầng) hoặc 0.074/Re^0.2 (rối), Re theo dây cung cục bộ.
Bỏ qua: hiệu ứng độ dày lên áp suất, nén được, tách dòng, tương tác cánh-thân.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Protocol

import numpy as np

from .config import Params, load_params, TABLES_DIR, ensure_output_dirs


class WingGeometry(Protocol):
    semi_span: float

    def surface(self, u: np.ndarray, v: np.ndarray, side: int):  # -> (X, Y, Z)
        ...


# --------------------------------------------------------------------------
# Tiện ích số
# --------------------------------------------------------------------------
def _gauss(n: int, a: float, b: float) -> tuple[np.ndarray, np.ndarray]:
    """Nút và trọng số Gauss-Legendre trên [a, b]."""
    x, w = np.polynomial.legendre.leggauss(n)
    return 0.5 * (b - a) * x + 0.5 * (b + a), 0.5 * (b - a) * w


def _position(wing: WingGeometry, theta: np.ndarray, v: np.ndarray, side: int) -> np.ndarray:
    """r(theta, v) với u = (1 - cos theta)/2; trả về mảng (..., 3)."""
    u = 0.5 * (1.0 - np.cos(theta))
    x, y, z = wing.surface(u, v, side)
    return np.stack([np.asarray(x, float), np.asarray(y, float), np.asarray(z, float)], axis=-1)


def _surface_element(wing: WingGeometry, theta: np.ndarray, v: np.ndarray, side: int):
    """
    Vector phần tử mặt  dS_vec = side * (r_theta x r_v)  (hướng ra ngoài cánh).
    Đạo hàm theo theta (không theo u) nên hữu hạn ngay cả ở mép trước.
    """
    semi = float(wing.semi_span)
    h_t, h_v = 1e-6, 1e-6 * semi
    t_p, t_m = np.clip(theta + h_t, 0.0, math.pi), np.clip(theta - h_t, 0.0, math.pi)
    v_p, v_m = np.clip(v + h_v, 0.0, semi), np.clip(v - h_v, 0.0, semi)

    r_theta = (_position(wing, t_p, v, side) - _position(wing, t_m, v, side)) / (t_p - t_m)[..., None]
    r_v = (_position(wing, theta, v_p, side) - _position(wing, theta, v_m, side)) / (v_p - v_m)[..., None]
    return side * np.cross(r_theta, r_v)


# --------------------------------------------------------------------------
# Mô hình áp suất và ma sát
# --------------------------------------------------------------------------
def planform_area(wing: WingGeometry, n: int = 64) -> float:
    """Diện tích hình chiếu S = 2 * ∫ c(y) dy với c(y) = X(u=1) - X(u=0)."""
    v, w = _gauss(n, 0.0, float(wing.semi_span))
    x_le = wing.surface(np.zeros_like(v), v, +1)[0]
    x_te = wing.surface(np.ones_like(v), v, +1)[0]
    return 2.0 * float(np.sum((np.asarray(x_te) - np.asarray(x_le)) * w))


def lift_slope(p: Params, aspect_ratio: float) -> float:
    """Độ dốc lực nâng a [1/rad]: 2*pi (2D) hoặc đã hiệu chỉnh cánh hữu hạn."""
    a0 = 2.0 * math.pi
    if not p.aero.finite_wing_correction:
        return a0
    return a0 / (1.0 + a0 / (math.pi * p.aero.oswald_e * aspect_ratio))


def delta_cp(theta: np.ndarray, v: np.ndarray, semi_span: float, alpha_eff: float,
             slope_ratio: float, span_loading: str) -> np.ndarray:
    """Delta_Cp(theta, v) = 4*alpha_e*(a/2pi)*cot(theta/2)*g(v)."""
    cot = 1.0 / np.tan(0.5 * theta)
    if span_loading == "elliptic":
        eta = np.clip(v / semi_span, 0.0, 1.0)
        g = (4.0 / math.pi) * np.sqrt(1.0 - eta ** 2)   # trung bình theo sải = 1
    else:
        g = 1.0
    return 4.0 * alpha_eff * slope_ratio * cot * g


def skin_friction_coeff(p: Params, chord: np.ndarray) -> np.ndarray:
    """Cf trung bình theo dây cung cục bộ (tấm phẳng)."""
    re = np.maximum(p.reynolds(chord), 1.0)
    laminar = 1.328 / np.sqrt(re)
    turbulent = 0.074 / re ** 0.2
    mode = p.aero.boundary_layer
    if mode == "laminar":
        return laminar
    if mode == "turbulent":
        return turbulent
    return np.where(re < p.aero.transition_re, laminar, turbulent)


# --------------------------------------------------------------------------
# Kết quả
# --------------------------------------------------------------------------
@dataclass
class AeroResult:
    L: float                    # lực nâng tổng [N]
    L_pressure: float           # phần lực nâng do áp suất [N]
    L_friction: float           # phần lực nâng do ma sát (nhỏ, do tấm nghiêng góc tới) [N]
    D_pressure_raw: float       # cản áp suất thô từ tích phân mặt [N]
    D_suction_correction: float # hiệu chỉnh hút mép trước [N]
    D_pressure: float           # cản áp suất sau hiệu chỉnh [N]
    D_friction: float           # cản ma sát từ tích phân mặt [N]
    D_induced_ref: float        # cản cảm ứng tham chiếu (công thức, KHÔNG từ tích phân) [N]
    D_total: float              # tổng lực cản [N]
    CL: float
    CD: float
    L_over_D: float
    S_ref: float                # diện tích hình chiếu [m^2]
    AR: float                   # độ giãn dài
    lift_slope: float           # a [1/rad]
    alpha_eff_deg: float
    q_inf: float                # [Pa]

    def as_rows(self) -> list[tuple[str, float, str, str]]:
        return [
            ("L", self.L, "N", "Lực nâng tổng (tích phân mặt)"),
            ("L_pressure", self.L_pressure, "N", "Lực nâng do áp suất"),
            ("L_friction", self.L_friction, "N", "Lực nâng do ma sát (nhỏ)"),
            ("D_pressure_raw", self.D_pressure_raw, "N", "Cản áp suất thô (chưa tính hút mép trước)"),
            ("D_suction_correction", self.D_suction_correction, "N", "Hiệu chỉnh hút mép trước"),
            ("D_pressure", self.D_pressure, "N", "Cản áp suất sau hiệu chỉnh"),
            ("D_friction", self.D_friction, "N", "Cản ma sát bề mặt (tích phân mặt)"),
            ("D_induced_ref", self.D_induced_ref, "N", "Cản cảm ứng tham chiếu CL^2/(pi e AR), không phải tích phân mặt"),
            ("D_total", self.D_total, "N", "Tổng lực cản"),
            ("CL", self.CL, "-", "L / (q S)"),
            ("CD", self.CD, "-", "D / (q S)"),
            ("L/D", self.L_over_D, "-", "Độ lướt"),
            ("S_ref", self.S_ref, "m^2", "Diện tích hình chiếu"),
            ("AR", self.AR, "-", "b^2 / S"),
            ("lift_slope", self.lift_slope, "1/rad", "Độ dốc lực nâng a"),
            ("alpha_eff", self.alpha_eff_deg, "deg", "alpha - alpha_L0"),
            ("q_inf", self.q_inf, "Pa", "Áp suất động 1/2 rho V^2"),
        ]

    def save_csv(self, path: str | Path | None = None) -> Path:
        ensure_output_dirs()
        path = Path(path) if path else TABLES_DIR / "aero_results.csv"
        with open(path, "w", newline="", encoding="utf-8-sig") as fh:
            writer = csv.writer(fh)
            writer.writerow(["quantity", "value", "unit", "description"])
            for name, val, unit, desc in self.as_rows():
                writer.writerow([name, f"{val:.6g}", unit, desc])
        return path

    def print_table(self) -> None:
        print(f"{'Đại lượng':<22}{'Giá trị':>14}  {'Đơn vị':<7} Mô tả")
        print("-" * 78)
        for name, val, unit, desc in self.as_rows():
            print(f"{name:<22}{val:>14.5g}  {unit:<7} {desc}")


# --------------------------------------------------------------------------
# Hàm chính
# --------------------------------------------------------------------------
def compute_aero_forces(wing: WingGeometry, p: Params | None = None) -> AeroResult:
    """Tính lực nâng/cản của cánh bằng tích phân mặt (hai mặt trên/dưới, nửa cánh x 2)."""
    p = p or load_params()
    semi = float(wing.semi_span)
    q = p.q_inf
    alpha = p.alpha_rad
    alpha_eff = alpha - p.alpha_L0_rad

    S = planform_area(wing, p.aero.n_span)
    AR = (2.0 * semi) ** 2 / S
    a = lift_slope(p, AR)
    slope_ratio = a / (2.0 * math.pi)

    d_hat = np.array([math.cos(alpha), 0.0, math.sin(alpha)])
    l_hat = np.array([-math.sin(alpha), 0.0, math.cos(alpha)])
    x_hat = np.array([1.0, 0.0, 0.0])

    # lưới Gauss theo (theta, v)
    th_nodes, th_w = _gauss(p.aero.n_theta, 0.0, math.pi)
    v_nodes, v_w = _gauss(p.aero.n_span, 0.0, semi)
    TH, V = np.meshgrid(th_nodes, v_nodes, indexing="ij")
    W = th_w[:, None] * v_w[None, :]

    # dây cung cục bộ -> Cf theo sải
    x_le = np.asarray(wing.surface(np.zeros_like(v_nodes), v_nodes, +1)[0])
    x_te = np.asarray(wing.surface(np.ones_like(v_nodes), v_nodes, +1)[0])
    cf = skin_friction_coeff(p, x_te - x_le)[None, :]          # (1, n_span)

    dcp = delta_cp(TH, V, semi, alpha_eff, slope_ratio, p.aero.span_loading)

    F_p = np.zeros(3)
    F_f = np.zeros(3)
    for side in (+1, -1):
        dS_vec = _surface_element(wing, TH, V, side)           # (n_th, n_sp, 3)
        dS = np.linalg.norm(dS_vec, axis=-1)
        n_hat = dS_vec / np.maximum(dS, 1e-300)[..., None]

        cp = -side * 0.5 * dcp                                  # trên: -Δ/2, dưới: +Δ/2
        F_p += np.sum(-q * cp[..., None] * dS_vec * W[..., None], axis=(0, 1))

        # ma sát: hướng theo thành phần tiếp tuyến của dòng tự do
        t = d_hat - np.sum(d_hat * n_hat, axis=-1, keepdims=True) * n_hat
        t /= np.maximum(np.linalg.norm(t, axis=-1, keepdims=True), 1e-12)
        F_f += np.sum(q * cf[..., None] * t * (dS * W)[..., None], axis=(0, 1))

    # đối xứng qua mặt phẳng y = 0: nhân đôi, thành phần y triệt tiêu
    F_p *= 2.0
    F_f *= 2.0
    F_p[1] = F_f[1] = 0.0

    D_raw = float(F_p @ d_hat)

    # lực hút mép trước T (dọc -x) sao cho tổng lực áp suất vuông góc dòng (thiết diện mỏng)
    suction = np.zeros(3)
    if p.aero.leading_edge_suction:
        suction = -D_raw / float(x_hat @ d_hat) * x_hat
    F_p_corr = F_p + suction

    L_pressure = float(F_p_corr @ l_hat)
    L_friction = float(F_f @ l_hat)
    L = L_pressure + L_friction
    D_pressure = float(F_p_corr @ d_hat)
    D_friction = float(F_f @ d_hat)
    CL = L / (q * S)
    D_induced = (q * S * CL ** 2 / (math.pi * p.aero.oswald_e * AR)
                 if p.aero.include_induced_drag else 0.0)
    D_total = D_pressure + D_friction + D_induced

    return AeroResult(
        L=L, L_pressure=L_pressure, L_friction=L_friction, D_pressure_raw=D_raw, D_suction_correction=float(suction @ d_hat),
        D_pressure=D_pressure, D_friction=D_friction, D_induced_ref=D_induced,
        D_total=D_total, CL=CL, CD=D_total / (q * S),
        L_over_D=L / D_total if D_total != 0 else float("inf"),
        S_ref=S, AR=AR, lift_slope=a, alpha_eff_deg=math.degrees(alpha_eff), q_inf=q,
    )


def analytic_reference(wing: WingGeometry, result: AeroResult, p: Params) -> dict[str, float]:
    """
    Đáp án giải tích để kiểm chứng (cho cánh tấm phẳng, không độ dày):
        N = q * a * alpha_e * 2 * ∫ g(y) c(y) dy      (lực pháp tuyến)
        L (phần do áp suất) = N / cos(alpha) nếu có hút mép trước, ngược lại N cos(alpha)
        D_pressure_raw = N sin(alpha)
    trong đó g(y) là hệ số phân bố tải theo sải (elliptic hoặc đều).
    """
    semi = float(wing.semi_span)
    v, w = _gauss(400, 0.0, semi)
    c = np.asarray(wing.surface(np.ones_like(v), v, +1)[0]) - np.asarray(wing.surface(np.zeros_like(v), v, +1)[0])
    if p.aero.span_loading == "elliptic":
        g = (4.0 / math.pi) * np.sqrt(1.0 - (v / semi) ** 2)
    else:
        g = np.ones_like(v)
    weighted_area = 2.0 * float(np.sum(g * c * w))
    N = result.q_inf * result.lift_slope * math.radians(result.alpha_eff_deg) * weighted_area
    a = p.alpha_rad
    L = N / math.cos(a) if p.aero.leading_edge_suction else N * math.cos(a)
    return {"N": N, "L": L, "D_pressure_raw": N * math.sin(a)}


# --------------------------------------------------------------------------
# Cánh thử nghiệm (CHỈ để test aero.py độc lập; dùng wing.py của Vĩ khi ghép)
# --------------------------------------------------------------------------
class FlatTaperedWing:
    """Tấm phẳng thon, không độ dày: x = u*c(y), y = v, z = 0."""

    def __init__(self, span: float, chord_root: float, chord_tip: float):
        self.semi_span = span / 2.0
        self.c_root, self.c_tip = chord_root, chord_tip

    def chord(self, v):
        return self.c_root - (self.c_root - self.c_tip) * np.asarray(v) / self.semi_span

    def surface(self, u, v, side):
        u, v = np.asarray(u, float), np.asarray(v, float)
        return u * self.chord(v), v, np.zeros_like(u)


def _selftest() -> None:
    p = load_params()
    print("=" * 78)
    print("TỰ KIỂM TRA aero.py (tấm phẳng thử nghiệm, chưa dùng wing.py của Vĩ)")
    print("=" * 78)
    wing = FlatTaperedWing(p.wing.span, p.wing.chord_root, p.wing.chord_tip)
    res = compute_aero_forces(wing, p)
    res.print_table()

    ref = analytic_reference(wing, res, p)
    err_L = abs(res.L_pressure - ref["L"]) / abs(ref["L"])
    err_D = abs(res.D_pressure_raw - ref["D_pressure_raw"]) / abs(ref["D_pressure_raw"])
    print("\nSo sánh với giải tích:")
    print(f"  L(áp suất) giải tích = {ref['L']:.4f} N | số = {res.L_pressure:.4f} N | sai số tương đối = {err_L:.2e}")
    print(f"  D_raw giải tích = {ref['D_pressure_raw']:.4f} N | số = {res.D_pressure_raw:.4f} N | sai số tương đối = {err_D:.2e}")
    print("  Kiểm tra diện tích: S số = %.5f, S giải tích = %.5f"
          % (res.S_ref, 0.5 * (p.wing.chord_root + p.wing.chord_tip) * p.wing.span))
    print("  ĐẠT" if max(err_L, err_D) < 1e-3 else "  CHƯA ĐẠT: kiểm tra lại tham số/lưới")

    path = res.save_csv()
    print(f"\nĐã lưu bảng kết quả: {path}")


if __name__ == "__main__":
    _selftest()
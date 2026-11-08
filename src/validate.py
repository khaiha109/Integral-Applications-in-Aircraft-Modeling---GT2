"""
Module validate.py: Kiểm chứng kết quả tính toán số trị với công thức giải tích và lý thuyết.
Người phụ trách chính:
- Trương Thanh Vĩ: Phần diện tích và thể tích/khối lượng
- Hà Ngọc Khải: Phần lực khí động (lực nâng, lực cản)
Review: Nhóm trưởng

Chạy riêng phần khí động (từ thư mục gốc repo):
    python -m src.validate

Ghi chú tích hợp:
- `config` trong phần của Khải là đối tượng Params từ `src.config.load_params()`
  (hoặc None / đường dẫn params.yaml), không phải dict.
- Lực tính bằng `src.aero.compute_aero_forces(wing, params)`.
- `wing` là đối tượng có `semi_span` và `surface(u, v, side)` (xem docstring aero.py).
  Nếu không truyền, dùng cánh tấm phẳng thử nghiệm FlatTaperedWing.
"""
from __future__ import annotations

import copy
import math
import time
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .config import Params, load_params, TABLES_DIR, ensure_output_dirs
from .aero import (
    FlatTaperedWing,
    analytic_reference,
    compute_aero_forces,
    skin_friction_coeff,
    _gauss,
)

# NOTE: src.wing / src.fuselage được import bên trong hàm của Vĩ (khi các module đó có sẵn)
# để validate.py của phần khí động chạy được độc lập.


# ==============================================================================
# PHẦN VIỆC CỦA TRƯƠNG THANH VĨ (Kiểm chứng hình học, diện tích, thể tích)
# ==============================================================================

def validate_geometry(config: Dict[str, Any]) -> pd.DataFrame:
    """
    Kiểm chứng độ chính xác của các thuật toán tích phân hình học:
    1. Diện tích hình chiếu cánh: So sánh tích phân số với công thức hình thang giải tích S = (c_root + c_tip)/2 * b.
    2. Thể tích thân máy bay: So sánh tích phân số với khối hình mẫu (hình trụ V = pi*R^2*L hoặc ellipsoid 4/3*pi*a*b*c).

    Parameters
    ----------
    config : dict
        Tham số cấu hình từ params.yaml

    Returns
    -------
    pd.DataFrame
        Bảng so sánh: [Đại lượng, Giải tích, Tích phân số, Sai số tuyệt đối, Sai số tương đối (%)]

    TODO (Trương Thanh Vĩ):
    - Tính diện tích hình chiếu giải tích vs số trị.
    - Tính thể tích thân theo 2 phương pháp (quad vs tplquad/trapezoid).
    - Tính sai số tương đối: error (%) = |val_num - val_exact| / val_exact * 100%.
    - Đóng gói kết quả thành DataFrame để xuất ra bảng báo cáo.
    """
    # TODO (Trương Thanh Vĩ): Hoàn thiện hàm kiểm chứng hình học
    # from .wing import calculate_projected_area, calculate_surface_area
    # from .fuselage import calculate_fuselage_volume
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm validate_geometry")


def check_mesh_convergence(config: Dict[str, Any]) -> pd.DataFrame:
    """
    Khảo sát sự hội tụ của tích phân diện tích bề mặt cánh theo độ mịn lưới (n_chord, n_span).

    Parameters
    ----------
    config : dict
        Tham số cấu hình

    Returns
    -------
    pd.DataFrame
        Bảng kết quả với các kích thước lưới khác nhau (vd: 50x25, 100x50, 200x100, 400x200).

    TODO (Trương Thanh Vĩ):
    - Chạy vòng lặp qua các bộ kích thước lưới tăng dần.
    - Ghi lại giá trị diện tích và thời gian tính toán.
    """
    # TODO (Trương Thanh Vĩ): Hoàn thiện kiểm tra hội tụ lưới
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm check_mesh_convergence")


# ==============================================================================
# PHẦN VIỆC CỦA HÀ NGỌC KHẢI (Kiểm chứng lực nâng, lực cản và bậc độ lớn)
# ==============================================================================

COLUMNS = [
    "Hạng mục", "Đại lượng", "Tích phân số", "Tham chiếu",
    "Sai số tuyệt đối", "Sai số tương đối (%)", "Dung sai (%)", "Đánh giá", "Ghi chú",
]


def _resolve_params(config) -> Params:
    if config is None:
        return load_params()
    if isinstance(config, Params):
        return config
    if isinstance(config, (str, Path)):
        return load_params(config)
    raise TypeError("config phải là Params (src.config.load_params()), đường dẫn params.yaml hoặc None.")


def _default_wing(p: Params):
    return FlatTaperedWing(p.wing.span, p.wing.chord_root, p.wing.chord_tip)


def _row(group: str, name: str, num: float, ref: float, tol_pct: float, note: str = "") -> dict:
    abs_err = abs(num - ref)
    rel = abs_err / abs(ref) * 100.0 if ref != 0 else float("nan")
    if math.isnan(rel):
        status = "XEM LẠI"
    elif rel <= tol_pct:
        status = "ĐẠT"
    elif rel <= 3 * tol_pct:
        status = "CHÚ Ý"
    else:
        status = "KHÔNG ĐẠT"
    return dict(zip(COLUMNS, [group, name, num, ref, abs_err, rel, tol_pct, status, note]))


def _range_row(group: str, name: str, value: float, lo: float, hi: float, note: str = "") -> dict:
    ok = lo <= value <= hi
    return dict(zip(COLUMNS, [group, name, value, f"[{lo:g}, {hi:g}]", float("nan"), float("nan"),
                              float("nan"), "ĐẠT" if ok else "NGOÀI KHOẢNG", note]))


def validate_aerodynamics(config=None, wing=None, tol_theory_pct: float = 10.0,
                          tol_numeric_pct: float = 0.1) -> pd.DataFrame:
    """
    Kiểm chứng lực nâng và lực cản tính bằng tích phân mặt so với lý thuyết:
    1. So sánh lực nâng với Lý thuyết thiết diện mỏng (Thin Airfoil Theory):
       C_L_wing ≈ 2*pi*alpha_e / (1 + 2/AR),  AR = b^2 / S,  alpha_e = alpha - alpha_L0
       L_theory = 0.5 * rho * V_inf^2 * S * C_L_wing
    2. Kiểm tra tính nhất quán của tích phân mặt (cùng mô hình, so với công thức đóng).
    3. Kiểm tra hành vi vật lý: tuyến tính theo alpha, L = 0 tại alpha_L0, L ~ V^2,
       cản ma sát so với công thức tấm phẳng.
    4. Kiểm tra bậc độ lớn: L ~ 10^3 - 10^4 N, C_D ~ 0.01 - 0.05.

    Parameters
    ----------
    config : Params | str | Path | None
        Tham số (mặc định đọc params.yaml).
    wing : đối tượng cánh (semi_span, surface(u, v, side)); mặc định cánh tấm phẳng thử nghiệm.
    tol_theory_pct : dung sai khi so với công thức lý thuyết của đề (khác mô hình nhẹ: e, tải theo sải).
    tol_numeric_pct : dung sai khi so tích phân số với công thức đóng cùng mô hình.

    Returns
    -------
    pd.DataFrame
        Bảng đối chiếu kết quả tích phân mặt và lý thuyết giải tích.
    """
    p = _resolve_params(config)
    wing = wing or _default_wing(p)
    res = compute_aero_forces(wing, p)
    rows: list[dict] = []
    q, S, AR = res.q_inf, res.S_ref, res.AR
    alpha_e = math.radians(res.alpha_eff_deg)
    cos_a = math.cos(p.alpha_rad)

    # ---- 1. So với lý thuyết thiết diện mỏng (công thức trong đề) ----------
    CL_spec = 2.0 * math.pi * alpha_e / (1.0 + 2.0 / AR)
    L_spec = q * S * CL_spec
    rows.append(_row("1. Lý thuyết thiết diện mỏng", "Lực nâng L [N]", res.L, L_spec, tol_theory_pct,
                     "L_theory = q S 2π α_e/(1+2/AR). Chênh lệch do: e=%.2f (≠1), tải elliptic trên cánh thon, "
                     "hút mép trước (1/cosα), thành phần ma sát." % p.aero.oswald_e))
    rows.append(_row("1. Lý thuyết thiết diện mỏng", "Hệ số nâng C_L [-]", res.CL, CL_spec, tol_theory_pct,
                     "C_L = L/(q S)"))

    # cấu hình đồng bộ giả thiết đề: e=1, tải đều, không hút mép -> L_pressure/cosα = N phải trùng L_spec
    p_sync = copy.deepcopy(p)
    p_sync.aero.oswald_e, p_sync.aero.span_loading = 1.0, "uniform"
    p_sync.aero.leading_edge_suction = False
    r_sync = compute_aero_forces(wing, p_sync)
    CL_sync = 2.0 * math.pi * alpha_e / (1.0 + 2.0 / r_sync.AR)
    rows.append(_row("1. Lý thuyết thiết diện mỏng", "Lực pháp tuyến N (cấu hình đồng bộ giả thiết đề) [N]",
                     r_sync.L_pressure / cos_a, r_sync.q_inf * r_sync.S_ref * CL_sync, tol_numeric_pct,
                     "e=1, tải đều, tắt hút mép: tích phân mặt phải trùng công thức đề (lực pháp tuyến N = L_p/cosα)."))

    # ---- 2. Nhất quán tích phân mặt vs công thức đóng (cùng mô hình) -------
    ref = analytic_reference(wing, res, p)
    rows.append(_row("2. Tích phân mặt vs công thức đóng", "Lực nâng do áp suất L_p [N]", res.L_pressure,
                     ref["L"], tol_numeric_pct, "Cùng mô hình áp suất; đo sai số cầu phương."))
    rows.append(_row("2. Tích phân mặt vs công thức đóng", "Cản áp suất thô D_raw [N]", res.D_pressure_raw,
                     ref["D_pressure_raw"], tol_numeric_pct, "D_raw = N sinα (chưa tính hút mép trước)."))
    if p.aero.leading_edge_suction:
        rows.append(_range_row("2. Tích phân mặt vs công thức đóng", "Cản áp suất sau hút mép D_pressure [N]",
                               res.D_pressure, -1e-6 * res.L, 1e-6 * res.L,
                               "Thiết diện mỏng: cản áp suất 2D = 0 (nghịch lý d'Alembert)."))

    # ---- 3. Hành vi vật lý ---------------------------------------------------
    # 3a. quét góc tới: L_p tuyến tính theo alpha_e, trùng công thức đóng
    max_err = 0.0
    for a_deg in (p.aero.alpha_L0_deg + d for d in (1.0, 3.0, 6.0, 9.0, 12.0)):
        pa = copy.deepcopy(p)
        pa.flow.alpha_deg = a_deg
        ra = compute_aero_forces(wing, pa)
        refa = analytic_reference(wing, ra, pa)
        max_err = max(max_err, abs(ra.L_pressure - refa["L"]) / abs(refa["L"]))
    rows.append(dict(zip(COLUMNS, ["3. Hành vi vật lý", "Quét α (α_L0+1..12°): sai số tương đối lớn nhất của L_p [%]",
                                  max_err * 100.0, 0.0, max_err * 100.0, max_err * 100.0, tol_numeric_pct,
                                  "ĐẠT" if max_err * 100.0 <= tol_numeric_pct else "KHÔNG ĐẠT",
                                  "5 góc tới; L_p phải tuyến tính theo α_e."])))

    # 3b. L = 0 tại alpha_L0
    p0 = copy.deepcopy(p)
    p0.flow.alpha_deg = p.aero.alpha_L0_deg
    r0 = compute_aero_forces(wing, p0)
    rows.append(_row("3. Hành vi vật lý", "Lực nâng do áp suất tại α = α_L0 [N]", r0.L_pressure, 0.0, 1.0,
                     "Phải bằng 0 (so với L tại α hiện tại: %.2e)." % (abs(r0.L_pressure) / abs(res.L_pressure))))
    rows[-1]["Sai số tương đối (%)"] = abs(r0.L_pressure) / abs(res.L_pressure) * 100.0
    rows[-1]["Đánh giá"] = "ĐẠT" if rows[-1]["Sai số tương đối (%)"] < 1e-3 else "KHÔNG ĐẠT"
    rows[-1]["Dung sai (%)"] = 1e-3

    # 3c. L ~ V^2
    pv = copy.deepcopy(p)
    pv.flow.V_inf = 2.0 * p.flow.V_inf
    rv = compute_aero_forces(wing, pv)
    rows.append(_row("3. Hành vi vật lý", "Tỉ số L_p(2V)/L_p(V) [-]", rv.L_pressure / res.L_pressure, 4.0,
                     tol_numeric_pct, "Lực áp suất tỉ lệ V²."))

    # 3d. cản ma sát vs công thức tấm phẳng (tham chiếu dùng diện tích hình chiếu x2)
    semi = float(wing.semi_span)
    v, w = _gauss(400, 0.0, semi)
    chord = np.asarray(wing.surface(np.ones_like(v), v, +1)[0]) - np.asarray(wing.surface(np.zeros_like(v), v, +1)[0])
    D_f_ref = q * cos_a * 2.0 * 2.0 * float(np.sum(skin_friction_coeff(p, chord) * chord * w))
    rows.append(_row("3. Hành vi vật lý", "Cản ma sát D_f [N]", res.D_friction, D_f_ref, 5.0,
                     "So với q·Cf·(2 mặt)·S·cosα của tấm phẳng; cánh có độ dày sẽ lớn hơn do diện tích ướt."))

    # ---- 4. Bậc độ lớn -------------------------------------------------------
    rows.append(_range_row("4. Bậc độ lớn", "Lực nâng L [N]", res.L, 1e3, 1e5,
                           "Máy bay cỡ nhỏ ~ 10^3–10^4 N (L/g ≈ %.0f kg)." % (res.L / 9.81)))
    rows.append(_range_row("4. Bậc độ lớn", "Hệ số cản C_D [-]", res.CD, 0.01, 0.05,
                           "Bay bằng ổn định thường 0.01–0.05."))
    rows.append(_range_row("4. Bậc độ lớn", "Hệ số nâng C_L [-]", res.CL, 0.1, 1.5,
                           "Dải C_L điển hình khi bay hành trình."))
    rows.append(_range_row("4. Bậc độ lớn", "Độ lướt L/D [-]", res.L_over_D, 5.0, 30.0,
                           "Máy bay cánh nhỏ điển hình ~ 8–20; >20 thường do bỏ qua cản của thân/đuôi."))

    return pd.DataFrame(rows, columns=COLUMNS)


def check_aero_convergence(config=None, wing=None,
                           grids=((8, 8), (16, 16), (32, 32), (64, 48), (96, 64), (192, 128))) -> pd.DataFrame:
    """
    Khảo sát hội tụ của tích phân mặt theo số nút Gauss (n_theta x n_span).
    Lưới mịn nhất được dùng làm tham chiếu.

    Returns
    -------
    pd.DataFrame
        [n_theta, n_span, L, D_friction, sai số L (%), sai số D_f (%), thời gian (ms)]
    """
    p = _resolve_params(config)
    wing = wing or _default_wing(p)
    recs = []
    for n_th, n_sp in grids:
        pg = copy.deepcopy(p)
        pg.aero.n_theta, pg.aero.n_span = n_th, n_sp
        t0 = time.perf_counter()
        r = compute_aero_forces(wing, pg)
        dt = (time.perf_counter() - t0) * 1e3
        recs.append((n_th, n_sp, r.L, r.D_friction, dt))
    L_ref, Df_ref = recs[-1][2], recs[-1][3]
    out = pd.DataFrame(recs, columns=["n_theta", "n_span", "L [N]", "D_friction [N]", "Thời gian [ms]"])
    out["Sai số L (%)"] = (out["L [N]"] - L_ref).abs() / abs(L_ref) * 100.0
    out["Sai số D_f (%)"] = (out["D_friction [N]"] - Df_ref).abs() / abs(Df_ref) * 100.0
    return out[["n_theta", "n_span", "L [N]", "D_friction [N]", "Sai số L (%)", "Sai số D_f (%)", "Thời gian [ms]"]]


def save_aero_validation(config=None, wing=None) -> tuple[Path, Path]:
    """Chạy kiểm chứng khí động, lưu 2 bảng CSV vào results/tables/ và trả về đường dẫn."""
    ensure_output_dirs()
    t1, t2 = validate_aerodynamics(config, wing), check_aero_convergence(config, wing)
    p1, p2 = TABLES_DIR / "validation_aero.csv", TABLES_DIR / "convergence_aero.csv"
    t1.to_csv(p1, index=False, encoding="utf-8-sig")
    t2.to_csv(p2, index=False, encoding="utf-8-sig")
    return p1, p2


if __name__ == "__main__":
    pd.set_option("display.width", 250, "display.max_columns", None, "display.max_colwidth", 60,
                  "display.float_format", lambda x: f"{x:.5g}")
    print("=" * 100)
    print("KIỂM CHỨNG KHÍ ĐỘNG (cánh tấm phẳng thử nghiệm; thay bằng wing.py của Vĩ khi ghép)")
    print("=" * 100)
    df = validate_aerodynamics()
    print(df.drop(columns=["Ghi chú"]).to_string(index=False))
    print("\nKhảo sát hội tụ lưới tích phân:")
    print(check_aero_convergence().to_string(index=False))
    a, b = save_aero_validation()
    print(f"\nĐã lưu: {a}\n        {b}")
    bad = df[df["Đánh giá"].isin(["KHÔNG ĐẠT", "NGOÀI KHOẢNG"])]
    print("\nTẤT CẢ ĐẠT" if bad.empty else f"\nCÓ {len(bad)} HẠNG MỤC CẦN XEM LẠI:\n{bad[['Đại lượng','Đánh giá']].to_string(index=False)}")
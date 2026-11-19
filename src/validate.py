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

def validate_geometry(config=None) -> pd.DataFrame:
    """So tích phân số cánh/thân với công thức đóng và trường hợp hình trụ.

    Input là Params, đường dẫn params.yaml hoặc None. Đầu ra là DataFrame;
    các hàng thể tích vỏ đối chiếu 1D với bội ba, không gọi là giải tích.
    # AI-assisted: xem AI_DECLARATION.md
    """
    from .wing import calculate_projected_area, calculate_surface_area
    from .fuselage import (analytical_fuselage_volume,
                           calculate_fuselage_volume)

    p = _resolve_params(config)
    w, f = p.wing, p.fuselage
    cols = ["Đại lượng", "Tích phân số", "Tham chiếu", "Đơn vị",
            "Sai số tuyệt đối", "Sai số tương đối (%)", "Đánh giá", "Phương pháp"]
    rows = []

    def add(name, num, ref, unit, method, tol=0.01):
        err = abs(num - ref)
        pct = err / abs(ref) * 100 if ref else 0.0
        rows.append([name, num, ref, unit, err, pct,
                     "ĐẠT" if pct <= tol else "KHÔNG ĐẠT", method])

    b, cr, ct = w.span, w.chord_root, w.chord_tip
    s_exact = calculate_projected_area(b, cr, ct)
    s_num = calculate_projected_area(b, cr, ct, "numerical")
    add("Diện tích hình chiếu cánh", s_num, s_exact, "m²", "dblquad vs hình thang")

    kw = dict(nose_length=f.nose_length, tail_length=f.tail_length)
    v_1d = calculate_fuselage_volume(f.length, f.radius_max, f.skin_thickness,
                                     method="single_integral", **kw)
    v_3d = calculate_fuselage_volume(f.length, f.radius_max, f.skin_thickness,
                                     method="triple_integral", **kw)
    v_exact = analytical_fuselage_volume(f.length, f.radius_max, **kw)
    add("Thể tích thân đặc (1D)", v_1d["volume_solid"], v_exact, "m³",
        "quad vs công thức ba đoạn")
    add("Thể tích thân đặc (bội ba)", v_3d["volume_solid"], v_exact, "m³",
        "tplquad vs công thức ba đoạn")
    add("Thể tích vỏ thân (bội ba)", v_3d["volume_skin"], v_1d["volume_skin"], "m³",
        "tplquad vs quad")

    cylinder = calculate_fuselage_volume(f.length, f.radius_max, 0,
                                         nose_length=0, tail_length=0)
    add("Thân hình trụ kiểm tra", cylinder["volume_solid"],
        math.pi * f.radius_max**2 * f.length, "m³", "quad vs πR²L")

    # Bổ sung (Khải, 19/11/2026, cần Vĩ review): thể tích khối cánh (tích phân bội ba)
    from .wing import calculate_wing_volume
    add("Thể tích khối cánh", calculate_wing_volume(b, cr, ct, p.airfoil.naca, "triple"),
        calculate_wing_volume(b, cr, ct, p.airfoil.naca, "iterated"), "m³",
        "tplquad vs tích phân lặp ∫c²dy·2∫y_t du")

    # Bổ sung (Khải, 19/11/2026, cần Vĩ review): diện tích mặt ngoài thân
    from .fuselage import calculate_fuselage_surface_area
    a_fus_2d = calculate_fuselage_surface_area(f.length, f.radius_max, **kw)
    a_fus_1d = calculate_fuselage_surface_area(f.length, f.radius_max, **kw,
                                               method="single_integral")
    add("Diện tích mặt thân (tích phân mặt)", a_fus_2d, a_fus_1d, "m²",
        "dblquad(x,θ) vs 2π∫R√(1+R'²)dx")
    a_cyl = calculate_fuselage_surface_area(f.length, f.radius_max, 0, 0)
    add("Mặt bên thân hình trụ kiểm tra", a_cyl, 2 * math.pi * f.radius_max * f.length,
        "m²", "tích phân mặt vs 2πRL")

    area = calculate_surface_area(b, cr, ct, p.airfoil.naca,
                                  w.n_chord, w.n_span)["total_surface_area"]
    rows.append(["Diện tích bề mặt cánh", area, 2 * s_exact, "m²",
                 float("nan"), float("nan"), "ĐẠT" if area > 2 * s_exact else "KHÔNG ĐẠT",
                 "Kiểm tra cận dưới A > 2S; 2S không phải đáp án giải tích"])
    return pd.DataFrame(rows, columns=cols)


def check_mesh_convergence(config=None) -> pd.DataFrame:
    """Khảo sát hội tụ diện tích cánh; hàng cuối là tham chiếu số mịn nhất.

    Mỗi lưới dùng Gauss-Legendre theo θ và nửa sải; sai số tính so hàng cuối.
    # AI-assisted: xem AI_DECLARATION.md
    """
    from .wing import calculate_surface_area

    p = _resolve_params(config)
    grids = [(16, 8), (32, 16), (64, 32),
             (max(128, p.wing.n_chord), max(64, p.wing.n_span))]
    rows = []
    for n_u, n_v in grids:
        t0 = time.perf_counter()
        area = calculate_surface_area(p.wing.span, p.wing.chord_root,
                                      p.wing.chord_tip, p.airfoil.naca,
                                      n_u, n_v)["total_surface_area"]
        rows.append([n_u, n_v, area, (time.perf_counter() - t0) * 1000])
    out = pd.DataFrame(rows, columns=["n_u", "n_v", "Diện tích [m²]", "Thời gian [ms]"])
    reference = out["Diện tích [m²]"].iloc[-1]
    out["Sai số so lưới mịn nhất (%)"] = abs(out["Diện tích [m²]"] - reference) / reference * 100
    return out


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


def independent_checks(config=None, n_mc: int = 2_000_000, seed: int = 1,
                       n_tri: tuple[int, int] = (1500, 300)) -> pd.DataFrame:
    """Đối chiếu kết quả của chương trình với phương pháp số ĐỘC LẬP (Khải, mục 4.5).

    - Diện tích mặt trên/dưới cánh: chia mặt thành lưới tam giác phẳng (n_tri), cộng diện tích
      tam giác; không dùng công thức |r_u × r_v| nên độc lập với calculate_surface_area().
    - Thể tích thân đặc: Monte Carlo n_mc điểm đều trong hộp [0,L]×[-R,R]², đếm điểm có
      sqrt(y²+z²) <= R(x); kèm khoảng tin cậy 95 %.
    - Thể tích vỏ thân: xấp xỉ vỏ mỏng A_thân·t_v (diện tích mặt × độ dày); sai lệch vài %
      là do vỏ có bề dày đo theo bán kính, không theo pháp tuyến (xem docs/assumptions.md).
    # AI-assisted: xem AI_DECLARATION.md
    """
    from .wing import calculate_surface_area, wing_surface
    from .fuselage import (analytical_fuselage_volume, calculate_fuselage_surface_area,
                           calculate_fuselage_volume, fuselage_radius)
    p = _resolve_params(config)
    w, f = p.wing, p.fuselage
    kw = dict(nose_length=f.nose_length, tail_length=f.tail_length)

    def tri_area(side: str) -> float:
        th = np.linspace(0, math.pi, n_tri[0])
        u = (1 - np.cos(th)) / 2
        y = np.linspace(-w.semi_span, w.semi_span, n_tri[1])
        U, Y = np.meshgrid(u, y, indexing="ij")
        P = np.stack(wing_surface(U, Y, w.span, w.chord_root, w.chord_tip, p.airfoil.naca, side), -1)
        a, b_, c, d = P[:-1, :-1], P[1:, :-1], P[1:, 1:], P[:-1, 1:]
        return float((0.5 * np.linalg.norm(np.cross(b_ - a, c - a), axis=-1)
                      + 0.5 * np.linalg.norm(np.cross(c - a, d - a), axis=-1)).sum())

    A = calculate_surface_area(w.span, w.chord_root, w.chord_tip, p.airfoil.naca, w.n_chord, w.n_span)
    rng = np.random.default_rng(seed)
    Rm, L = f.radius_max, f.length
    x = rng.uniform(0, L, n_mc); y = rng.uniform(-Rm, Rm, n_mc); z = rng.uniform(-Rm, Rm, n_mc)
    hit = float((np.sqrt(y ** 2 + z ** 2) <= fuselage_radius(x, L, Rm, **kw)).mean())
    box = L * (2 * Rm) ** 2
    v_mc, v_ci = hit * box, 1.96 * math.sqrt(hit * (1 - hit) / n_mc) * box
    v_skin = calculate_fuselage_volume(L, Rm, f.skin_thickness, **kw)["volume_skin"]
    a_fus = calculate_fuselage_surface_area(L, Rm, **kw)

    rows = [
        ("Diện tích mặt trên cánh", A["area_upper"], tri_area("upper"), "m²",
         f"Lưới tam giác {n_tri[0]} × {n_tri[1]}"),
        ("Diện tích mặt dưới cánh", A["area_lower"], tri_area("lower"), "m²",
         f"Lưới tam giác {n_tri[0]} × {n_tri[1]}"),
        ("Thể tích thân đặc", analytical_fuselage_volume(L, Rm, **kw), v_mc, "m³",
         f"Monte Carlo {n_mc:,} điểm (±{v_ci:.3f} m³, 95 %)"),
        ("Thể tích vỏ thân", v_skin, a_fus * f.skin_thickness, "m³", "Xấp xỉ vỏ mỏng A_thân · t_v"),
    ]
    df = pd.DataFrame(rows, columns=["Đại lượng", "Chương trình", "Độc lập", "Đơn vị", "Phương pháp độc lập"])
    df["Sai lệch (%)"] = (df["Chương trình"] - df["Độc lập"]).abs() / df["Độc lập"].abs() * 100
    return df


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

"""
Module visualize.py: Trực quan hóa hình học 3D, vẽ đồ thị phân bố áp suất và xuất kết quả.
Người phụ trách:
- Trương Thanh Vĩ: Trực quan hóa 3D (Matplotlib 3D, Plotly Interactive 3D HTML, xuất ảnh mô hình 3D)
- Hà Ngọc Khải: Biểu đồ khí động học 2D (phân bố Cp, đường đặc tuyến nâng/cản theo alpha, xuất đồ thị kết quả)
"""

from pathlib import Path
from typing import Dict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from src.config import FIGURES_DIR, Params, load_params
from src.airfoil import get_airfoil_coordinates
from src.wing import wing_surface
from src.fuselage import fuselage_surface_3d, fuselage_radius


def _params(config: Params | None) -> Params:
    if config is None:
        return load_params()
    if not isinstance(config, Params):
        raise TypeError("config phải là Params từ load_params().")
    return config


def _path(save_path: Path | str | None, name: str) -> Path:
    path = Path(save_path) if save_path else FIGURES_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


# ==============================================================================
# PHẦN VIỆC CỦA TRƯƠNG THANH VĨ (Trực quan hóa 3D)
# ==============================================================================

def plot_airfoil_2d(naca_code: str = "2412", save_path: Path | str | None = None) -> None:
    """Lưu PNG biên dạng và camber NACA, 300 dpi. # AI-assisted"""
    x = (1 - np.cos(np.linspace(0, np.pi, 401))) / 2
    xu, zu, xl, zl = get_airfoil_coordinates(x, naca_code)
    fig, ax = plt.subplots(figsize=(9, 3.5))
    ax.plot(xu, zu, label="Mặt trên", color="#146C94", linewidth=2)
    ax.plot(xl, zl, label="Mặt dưới", color="#E38B29", linewidth=2)
    ax.plot(x, (zu + zl) / 2, "--", label="Đường camber", color="#5B6470")
    ax.fill_between(x, zl, zu, color="#56B6C2", alpha=0.18)
    ax.set(title=f"Biên dạng NACA {naca_code}", xlabel="x/c", ylabel="z/c")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(_path(save_path, "airfoil_profile.png"), dpi=300)
    plt.close(fig)


def plot_wing_3d_matplotlib(config: Params | None = None,
                            save_path: Path | str | None = None) -> None:
    """Lưu PNG cánh 3D hai mặt, 300 dpi. # AI-assisted"""
    p = _params(config)
    u = (1 - np.cos(np.linspace(0, np.pi, min(p.wing.n_chord, 100)))) / 2
    v = np.linspace(-p.wing.semi_span, p.wing.semi_span, min(p.wing.n_span, 60))
    U, V = np.meshgrid(u, v)
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection="3d")
    for side, color in (("upper", "#2E86AB"), ("lower", "#B7DCE8")):
        X, Y, Z = wing_surface(U, V, p.wing.span, p.wing.chord_root,
                               p.wing.chord_tip, p.airfoil.naca, side)
        ax.plot_surface(X, Y, Z, color=color, alpha=0.95, linewidth=0,
                        antialiased=True)
    ax.set(xlabel="x [m]", ylabel="y [m]", zlabel="z [m]", title="Cánh NACA " + p.airfoil.naca)
    ax.set_box_aspect((p.wing.chord_root, p.wing.span, 0.8))
    ax.view_init(elev=28, azim=-57)
    fig.tight_layout()
    fig.savefig(_path(save_path, "wing_3d.png"), dpi=300)
    plt.close(fig)


def plot_fuselage_3d_matplotlib(config: Params | None = None,
                                save_path: Path | str | None = None) -> None:
    """Lưu PNG thân 3D, 300 dpi. # AI-assisted"""
    p = _params(config)
    f = p.fuselage
    X, Y, Z = fuselage_surface_3d(f.length, f.radius_max, 120, 64,
                                  f.nose_length, f.tail_length)
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(X, Y, Z, color="#D9A441", alpha=0.95, linewidth=0)
    ax.set(xlabel="x [m]", ylabel="y [m]", zlabel="z [m]", title="Thân máy bay")
    ax.set_box_aspect((f.length, 2 * f.radius_max, 2 * f.radius_max))
    ax.view_init(elev=23, azim=-60)
    fig.tight_layout()
    fig.savefig(_path(save_path, "fuselage_3d.png"), dpi=300)
    plt.close(fig)


def render_full_aircraft_plotly(config: Params | None = None,
                                output_html_path: Path | str | None = None) -> None:
    """Lưu mô hình 3D tương tác HTML tự chứa. # AI-assisted"""
    build_aircraft_figure(_params(config)).write_html(
        _path(output_html_path, "aircraft_model.html"), include_plotlyjs=True)


def build_aircraft_figure(config: Params | None = None, *, show_wing: bool = True,
                          show_fuselage: bool = True, show_grid: bool = True,
                          resolution: int = 64, wing_offset: float | None = None) -> go.Figure:
    """Tạo Plotly Figure tương tác; cánh và thân được hiển thị cùng đơn vị mét.

    `wing_offset` chỉ dịch cánh dọc x để lắp ghép trực quan, không ảnh hưởng tích phân.
    # AI-assisted: xem AI_DECLARATION.md
    """
    p = _params(config)
    n = max(16, min(int(resolution), 160))
    offset = 0.35 * p.fuselage.length if wing_offset is None else wing_offset
    fig = go.Figure()
    if show_fuselage:
        f = p.fuselage
        X, Y, Z = fuselage_surface_3d(f.length, f.radius_max, n * 2, n,
                                      f.nose_length, f.tail_length)
        fig.add_trace(go.Surface(x=X, y=Y, z=Z, name="Thân",
                                 colorscale=[[0, "#C78F35"], [1, "#F2D18A"]],
                                 showscale=False, opacity=0.92))
    if show_wing:
        u = (1 - np.cos(np.linspace(0, np.pi, n))) / 2
        v = np.linspace(-p.wing.semi_span, p.wing.semi_span, n)
        U, V = np.meshgrid(u, v)
        for side, color in (("upper", "#247BA0"), ("lower", "#8CC7DA")):
            X, Y, Z = wing_surface(U, V, p.wing.span, p.wing.chord_root,
                                   p.wing.chord_tip, p.airfoil.naca, side)
            fig.add_trace(go.Surface(x=X + offset, y=Y, z=Z,
                                     name="Cánh " + ("trên" if side == "upper" else "dưới"),
                                     colorscale=[[0, color], [1, color]],
                                     showscale=False, opacity=0.98))
    fig.update_layout(
        title="Mô hình máy bay — hình học minh họa",
        scene=dict(xaxis=dict(title="x [m]", showgrid=show_grid),
                   yaxis=dict(title="y [m]", showgrid=show_grid),
                   zaxis=dict(title="z [m]", showgrid=show_grid),
                   aspectmode="data", camera=dict(eye=dict(x=1.5, y=1.7, z=0.9))),
        margin=dict(l=0, r=0, t=42, b=0),
        paper_bgcolor="white", font=dict(family="Arial", color="#233341"),
    )
    return fig


def build_wing_figure(config: Params | None = None, *, resolution: int = 64,
                      show_grid: bool = True) -> go.Figure:
    """Tạo mô hình cánh riêng để xoay/zoom trên dashboard."""
    fig = build_aircraft_figure(config, show_fuselage=False, show_grid=show_grid,
                                resolution=resolution, wing_offset=0.0)
    fig.update_layout(title="Cánh máy bay 3D")
    return fig


def build_fuselage_figure(config: Params | None = None, *, resolution: int = 64,
                          show_grid: bool = True) -> go.Figure:
    """Tạo mô hình thân riêng để xoay/zoom trên dashboard."""
    fig = build_aircraft_figure(config, show_wing=False, show_grid=show_grid,
                                resolution=resolution)
    fig.update_layout(title="Thân máy bay 3D")
    return fig


# ==============================================================================
# BỔ SUNG HÌNH 2D CHO BÁO CÁO (Hà Ngọc Khải bổ sung 19/11/2026, cần Vĩ review)
# Báo cáo Chương 3 dùng hình 2D; hình 3D ở trên để dành cho Chương 5.
# # AI-assisted: xem AI_DECLARATION.md
# ==============================================================================

# Bảng màu chung với hình của Vĩ (README: dùng chung bảng màu, cỡ chữ)
BLUE, ORANGE, GREEN, GRAY = "#146C94", "#E38B29", "#279B80", "#5B6470"


def _finish(fig, ax_list, path: Path) -> None:
    for ax in ax_list:
        ax.grid(alpha=0.25)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_wing_planform_2d(config: Params | None = None,
                          save_path: Path | str | None = None) -> None:
    """Hình chiếu bằng của cánh: miền D = {0 <= x <= c(y), |y| <= b/2} (Hình 3.2)."""
    from src.wing import chord_distribution
    p = _params(config)
    w = p.wing
    y = np.linspace(-w.semi_span, w.semi_span, 401)
    c = chord_distribution(y, w.span, w.chord_root, w.chord_tip)
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ax.fill_between(y, 0, c, color="#56B6C2", alpha=0.25, label="Miền D (hình chiếu cánh)")
    ax.plot(y, np.zeros_like(y), color=BLUE, lw=2, label="Mép trước x = 0")
    ax.plot(y, c, color=ORANGE, lw=2, label="Mép sau x = c(y)")
    for yy in (-w.semi_span, w.semi_span):
        ax.plot([yy, yy], [0, w.chord_tip], color=GRAY, lw=1.5)
    ax.annotate(f"$c_r$ = {w.chord_root:g} m", (0, w.chord_root), xytext=(0.6, w.chord_root + 0.25),
                fontsize=9, arrowprops=dict(arrowstyle="->", color=GRAY, lw=0.8))
    ax.annotate(f"$c_t$ = {w.chord_tip:g} m", (w.semi_span, w.chord_tip),
                xytext=(w.semi_span - 1.4, w.chord_tip + 1.0), fontsize=9,
                arrowprops=dict(arrowstyle="->", color=GRAY, lw=0.8))
    ax.set(xlabel="y [m] (theo sải)", ylabel="x [m] (theo dây cung)",
           title=f"Hình chiếu bằng của cánh (b = {w.span:g} m, S = "
                 f"{(w.chord_root + w.chord_tip) * w.span / 2:g} m²)")
    ax.set_ylim(w.chord_root + 0.9, -0.3)   # x hướng về sau: vẽ ngược trục cho giống nhìn từ trên
    ax.set_aspect("equal", adjustable="box")
    ax.legend(loc="lower center", ncol=3, fontsize=8.5, frameon=False, bbox_to_anchor=(0.5, -0.02))
    _finish(fig, [ax], _path(save_path, "wing_planform_2d.png"))


def plot_fuselage_profile_2d(config: Params | None = None,
                             save_path: Path | str | None = None) -> None:
    """Mặt cắt dọc của thân theo R(x) ba đoạn (mũi sin, trụ, đuôi cos) (Hình 3.3)."""
    p = _params(config)
    f = p.fuselage
    x = np.linspace(0, f.length, 600)
    r = fuselage_radius(x, f.length, f.radius_max, f.nose_length, f.tail_length)
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.fill_between(x, -r, r, color="#D9A441", alpha=0.30, lw=0)
    ax.plot(x, r, color="#8A5A12", lw=2, label="r = R(x)")
    ax.plot(x, -r, color="#8A5A12", lw=2)
    ax.axhline(0, color=GRAY, lw=0.8, ls="--")
    marks = [(0, "0"), (f.nose_length, "$L_1$"), (f.length - f.tail_length, "$L-L_3$"), (f.length, "$L$")]
    for xv, lab in marks:
        ax.axvline(xv, color="#BBBBBB", lw=0.8, zorder=0)
        ax.text(xv, -f.radius_max - 0.32, lab, ha="center", fontsize=9, color=GRAY)
    mids = [(f.nose_length / 2, "Mũi\n(sin)"),
            ((f.nose_length + f.length - f.tail_length) / 2, "Thân giữa (trụ, r = R)"),
            (f.length - f.tail_length / 2, "Đuôi\n(cos)")]
    for xm, lab in mids:
        ax.text(xm, 0.08, lab, ha="center", fontsize=9, color="#333333")
    ax.set(xlabel="x [m] (mũi → đuôi)", ylabel="r [m]",
           title=f"Mặt cắt dọc thân: L = {f.length:g} m, R = {f.radius_max:g} m")
    ax.set_ylim(-f.radius_max - 0.45, f.radius_max + 0.25)
    ax.set_aspect("equal", adjustable="box")
    _finish(fig, [ax], _path(save_path, "fuselage_profile_2d.png"))


def plot_skin_mass_vs_thickness(config: Params | None = None,
                                save_path: Path | str | None = None,
                                thicknesses_mm=(1, 2, 3, 4, 5, 6)) -> None:
    """Khối lượng vỏ thân (tích phân bội ba) theo độ dày vỏ, nhôm và composite (mục 4.2)."""
    from src.fuselage import calculate_fuselage_mass
    p = _params(config)
    f = p.fuselage
    t = np.asarray(thicknesses_mm, float)
    fig, ax = plt.subplots(figsize=(7.5, 4))
    for rho, name, color in ((f.density, f"Nhôm (ρ = {f.density:g} kg/m³)", BLUE),
                             (1600.0, "Composite (ρ = 1600 kg/m³)", ORANGE)):
        m = [calculate_fuselage_mass(f.length, f.radius_max, rho, ti / 1000, True,
                                     f.nose_length, f.tail_length) for ti in t]
        ax.plot(t, m, marker="o", lw=2, color=color, label=name)
        if rho == f.density:
            for ti, mi in zip(t, m):
                ax.annotate(f"{mi:.0f}", (ti, mi), xytext=(0, 7), textcoords="offset points",
                            ha="center", fontsize=8, color=color)
    ax.set(xlabel="Độ dày vỏ $t_v$ [mm]", ylabel="Khối lượng vỏ thân [kg]",
           title=f"Khối lượng vỏ thân theo độ dày (R = {f.radius_max:g} m)")
    ax.legend(frameon=False)
    _finish(fig, [ax], _path(save_path, "skin_mass_vs_thickness.png"))


# ==============================================================================
# PHẦN VIỆC CỦA HÀ NGỌC KHẢI (Biểu đồ khí động học 2D & Kết quả lực)
# # AI-assisted: xem AI_DECLARATION.md
# ==============================================================================

def _wing(config: Params, wing=None):
    """Cánh dùng cho khí động: mặc định là cánh NACA thật của Vĩ (WingModel)."""
    if wing is not None:
        return wing
    from src.wing import WingModel
    w = config.wing
    return WingModel(w.span, w.chord_root, w.chord_tip, config.airfoil.naca)


def sweep_alpha(config: Params | None, alpha_range_deg, wing=None) -> Dict[str, np.ndarray]:
    """Gọi compute_aero_forces() lần lượt cho từng góc tới (độ); trả về các mảng kết quả."""
    import copy
    from src.aero import compute_aero_forces
    p0 = _params(config)
    wg = _wing(p0, wing)
    out = {k: [] for k in ("alpha", "L", "D", "D_friction", "D_induced", "CL", "CD", "LD")}
    for a in np.asarray(alpha_range_deg, float):
        p = copy.deepcopy(p0)
        p.flow.alpha_deg = float(a)
        r = compute_aero_forces(wg, p)
        for k, v in (("alpha", a), ("L", r.L), ("D", r.D_total), ("D_friction", r.D_friction),
                     ("D_induced", r.D_induced_ref), ("CL", r.CL), ("CD", r.CD), ("LD", r.L_over_D)):
            out[k].append(v)
    return {k: np.asarray(v) for k, v in out.items()}


def sweep_velocity(config: Params | None, velocities, wing=None) -> Dict[str, np.ndarray]:
    """Gọi compute_aero_forces() cho từng vận tốc V_inf [m/s] (góc tới giữ nguyên)."""
    import copy
    from src.aero import compute_aero_forces
    p0 = _params(config)
    wg = _wing(p0, wing)
    L, D = [], []
    for v in np.asarray(velocities, float):
        p = copy.deepcopy(p0)
        p.flow.V_inf = float(v)
        r = compute_aero_forces(wg, p)
        L.append(r.L)
        D.append(r.D_total)
    return {"V": np.asarray(velocities, float), "L": np.asarray(L), "D": np.asarray(D)}


def plot_cp_distribution(
    config: Params | None = None,
    save_path: Path | str | None = None,
    wing=None,
    y_station: float | None = None,
) -> None:
    """
    Vẽ phân bố -C_p của mặt trên/mặt dưới dọc dây cung x/c tại vị trí sải y (mặc định b/4).

    Dùng trực tiếp delta_cp() của aero.py với đúng AR và độ dốc a của cánh thật
    (WingModel của Vĩ), C_p,trên = -ΔC_p/2, C_p,dưới = +ΔC_p/2. Lý thuyết cánh mỏng cho
    C_p -> -∞ tại mép trước, nên trục tung được cắt ở mức đọc được và có ghi chú.
    """
    from src.aero import delta_cp, lift_slope, planform_area
    p = _params(config)
    wg = _wing(p, wing)
    semi = float(wg.semi_span)
    S = planform_area(wg, p.aero.n_span)
    a = lift_slope(p, (2 * semi) ** 2 / S)
    alpha_eff = p.alpha_rad - p.alpha_L0_rad
    y0 = semi / 2 if y_station is None else float(y_station)

    theta = np.linspace(0.06, np.pi - 1e-3, 500)
    u = 0.5 * (1.0 - np.cos(theta))
    c0 = float(np.asarray(wg.surface(np.ones(1), np.full(1, y0), +1)[0])[0]
               - np.asarray(wg.surface(np.zeros(1), np.full(1, y0), +1)[0])[0])
    dcp = delta_cp(theta, np.full_like(theta, y0), semi, alpha_eff, a / (2 * np.pi),
                   p.aero.span_loading, chord=c0, mean_chord=S / (2 * semi))
    cp_up, cp_lo = -0.5 * dcp, 0.5 * dcp

    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.plot(u, -cp_up, color=BLUE, lw=2, label="Mặt trên")
    ax.plot(u, -cp_lo, color=ORANGE, lw=2, ls="--", label="Mặt dưới")
    ax.fill_between(u, -cp_up, -cp_lo, color="#56B6C2", alpha=0.20,
                    label=r"$\Delta C_p$ (tạo lực nâng)")
    ax.axhline(0, color=GRAY, lw=0.8)
    cap = float(np.interp(0.03, u, -cp_up))
    ax.set_ylim(-1.5, 1.12 * cap)
    ax.annotate("Mép trước: lý thuyết cánh mỏng\ncho $C_p \\to -\\infty$ (giới hạn mô hình)",
                xy=(0.012, 0.85 * cap), xytext=(0.30, 0.60 * cap), fontsize=8.5, color=GRAY,
                arrowprops=dict(arrowstyle="->", color=GRAY, lw=0.8))
    ax.set(xlabel="x/c", ylabel=r"$-C_p$",
           title=f"Phân bố hệ số áp suất tại y = {y0:.2f} m, α = {p.flow.alpha_deg:g}°")
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    _finish(fig, [ax], _path(save_path, "cp_distribution.png"))


def plot_lift_drag_polar(
    alpha_range_deg: np.ndarray,
    lifts: np.ndarray,
    drags: np.ndarray,
    save_path: Path | str | None = None,
    q_S: float | None = None,
) -> None:
    """
    Ba đồ thị: L theo α, cực khí động (C_L theo C_D, hoặc L theo D nếu không có q·S),
    và L/D theo α. Dữ liệu lấy từ sweep_alpha() (tức compute_aero_forces() của aero.py).
    """
    alpha = np.asarray(alpha_range_deg, float)
    L, D = np.asarray(lifts, float), np.asarray(drags, float)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
    axes[0].plot(alpha, L / 1000, marker="o", color=BLUE, lw=2)
    axes[0].set(xlabel="Góc tới α [độ]", ylabel="L [kN]", title="Lực nâng theo góc tới")
    if q_S:
        axes[1].plot(D / q_S, L / q_S, marker="o", color=ORANGE, lw=2)
        axes[1].set(xlabel="$C_D$", ylabel="$C_L$", title="Cực khí động")
    else:
        axes[1].plot(D, L, marker="o", color=ORANGE, lw=2)
        axes[1].set(xlabel="D [N]", ylabel="L [N]", title="Cực khí động")
    ld = np.divide(L, D, out=np.full_like(L, np.nan), where=np.abs(D) > 1e-12)
    axes[2].plot(alpha, ld, marker="o", color=GREEN, lw=2)
    i = int(np.nanargmax(ld))
    axes[2].annotate(f"max L/D ≈ {ld[i]:.1f}\ntại α = {alpha[i]:g}°", (alpha[i], ld[i]),
                     xytext=(alpha[i] + 3.0, 0.45 * ld[i]), fontsize=9,
                     arrowprops=dict(arrowstyle="->", color=GRAY, lw=0.8))
    axes[2].set(xlabel="Góc tới α [độ]", ylabel="L/D", title="Độ lướt theo góc tới")
    _finish(fig, axes, _path(save_path, "lift_drag_polar.png"))


def plot_span_loading(config: Params | None = None, save_path: Path | str | None = None,
                      wing=None) -> None:
    """Tải nâng theo sải dL/dy = q·a·α_e·g(η)·c(y) (tính lại từ delta_cp) so với elip chuẩn."""
    from src.aero import lift_slope, planform_area
    p = _params(config)
    wg = _wing(p, wing)
    semi = float(wg.semi_span)
    S = planform_area(wg, p.aero.n_span)
    a = lift_slope(p, (2 * semi) ** 2 / S)
    alpha_eff = p.alpha_rad - p.alpha_L0_rad
    y = np.linspace(0, semi, 300)
    x_le = np.asarray(wg.surface(np.zeros_like(y), y, +1)[0])
    x_te = np.asarray(wg.surface(np.ones_like(y), y, +1)[0])
    c = x_te - x_le
    eta = y / semi
    # ∫ΔC_p du theo dây cung = (ΔC_p/cot) * π/2 (xem (4.16)), nên dL/dy = q · c · ∫ΔC_p du
    from src.aero import delta_cp
    th = np.full_like(y, np.pi / 2)          # cot(π/4·2/2) = 1 tại θ = π/2
    dcp_per_cot = delta_cp(th, y, semi, alpha_eff, a / (2 * np.pi), p.aero.span_loading,
                           chord=c, mean_chord=S / (2 * semi))
    load = p.q_inf * c * dcp_per_cot * (np.pi / 2)
    ell = p.q_inf * a * alpha_eff * (S / (2 * semi)) * (4 / np.pi) * np.sqrt(np.clip(1 - eta ** 2, 0, None))
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.plot(y, load, color=BLUE, lw=2.4, label="Mô hình (từ ΔC$_p$ của aero.py)")
    ax.plot(y, ell, color=ORANGE, lw=1.6, ls="--", label="Elip chuẩn: q·a·α$_e$·$\\bar{c}$·(4/π)√(1-η²)")
    ax.set(xlabel="y [m] (gốc → mút)", ylabel="dL/dy [N/m]",
           title=f"Phân bố tải nâng theo sải (α = {p.flow.alpha_deg:g}°)")
    ax.legend(frameon=False, fontsize=9)
    _finish(fig, [ax], _path(save_path, "span_loading.png"))


def plot_lift_vs_velocity(config: Params | None = None, save_path: Path | str | None = None,
                          wing=None, mass_kg: float = 1160.0,
                          velocities=(30, 40, 50, 60, 70, 80)) -> None:
    """Lực nâng theo vận tốc (α cố định) so với trọng lượng W = m·g (mục 4.4)."""
    r = sweep_velocity(config, velocities, wing)
    W = mass_kg * 9.81
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.plot(r["V"], r["L"] / 1000, marker="o", lw=2, color=BLUE,
            label=f"Lực nâng L (α = {_params(config).flow.alpha_deg:g}°)")
    ax.axhline(W / 1000, color=ORANGE, ls="--", lw=1.8,
               label=f"Trọng lượng W = {mass_kg:g} kg × 9,81")
    ax.set(xlabel="Vận tốc bay $V_\\infty$ [m/s]", ylabel="Lực [kN]",
           title="Lực nâng tăng theo $V^2$ so với trọng lượng")
    ax.legend(frameon=False, fontsize=9)
    _finish(fig, [ax], _path(save_path, "lift_vs_velocity.png"))


def plot_convergence(geometry_table, aero_table, save_path: Path | str | None = None) -> None:
    """Sai số tương đối theo độ mịn lưới: diện tích mặt cánh và lực nâng (mục 4.5).

    Nhận hai DataFrame từ validate.check_mesh_convergence() và
    validate.check_aero_convergence(); bỏ hàng cuối (lưới tham chiếu, sai số 0).
    """
    def series(df):
        err_col = [c for c in df.columns if "%" in c or "err" in c.lower() or "Sai" in c][0]
        d = df.iloc[:-1]
        n = d.iloc[:, 0].astype(float) * d.iloc[:, 1].astype(float)
        e = np.maximum(d[err_col].astype(float).abs(), 1e-12)
        return n.to_numpy(), e.to_numpy()

    fig, ax = plt.subplots(figsize=(7.5, 4))
    for df, lab, color in ((geometry_table, "Diện tích bề mặt cánh", BLUE),
                           (aero_table, "Lực nâng L", ORANGE)):
        n, e = series(df)
        ax.loglog(n, e, marker="o", lw=2, color=color, label=lab)
    ax.set(xlabel="Số nút lưới (n₁ × n₂)", ylabel="Sai số tương đối [%]",
           title="Hội tụ theo độ mịn lưới (so với lưới mịn nhất)")
    ax.legend(frameon=False, fontsize=9)
    _finish(fig, [ax], _path(save_path, "convergence.png"))

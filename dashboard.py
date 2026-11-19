r"""Dashboard Streamlit cho bài tập tích phân và mô hình máy bay.

Chạy: .venv\Scripts\python.exe -m streamlit run dashboard.py
# AI-assisted: xem AI_DECLARATION.md
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.aero import compute_aero_forces
from src.airfoil import get_airfoil_coordinates
from src.config import load_params
from src.fuselage import (calculate_fuselage_mass, calculate_fuselage_volume,
                          fuselage_radius)
from src.validate import (check_aero_convergence, check_mesh_convergence,
                          validate_aerodynamics, validate_geometry)
from src.visualize import (build_aircraft_figure, build_fuselage_figure,
                           build_wing_figure)
from src.wing import (WingModel, calculate_projected_area,
                      calculate_surface_area, chord_distribution)


ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "results"
st.set_page_config(page_title="GT2 | Tích phân & máy bay", page_icon="✈️",
                   layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
    .block-container {padding-top: 1.5rem; max-width: 1500px;}
    h1, h2, h3 {color: #18364A;}
    div[data-testid="stMetric"] {background: #F2F7F9; border: 1px solid #DFE9ED;
        border-radius: 12px; padding: 16px;}
    div[data-testid="stSidebar"] {background: #F7FAFB;}
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def calculate(span: float, root_chord: float, tip_chord: float,
              body_length: float, body_radius: float, resolution: int):
    """Tính lại kết quả từ điều khiển; không ghi đè params.yaml."""
    p = load_params()
    p.wing.span, p.wing.chord_root, p.wing.chord_tip = span, root_chord, tip_chord
    p.fuselage.length, p.fuselage.radius_max = body_length, body_radius
    p.wing.n_chord, p.wing.n_span = 2 * resolution, resolution
    wing = WingModel(span, root_chord, tip_chord, p.airfoil.naca)
    S = calculate_projected_area(span, root_chord, tip_chord)
    surface = calculate_surface_area(span, root_chord, tip_chord,
                                     p.airfoil.naca, 2 * resolution, resolution)
    f = p.fuselage
    volumes = calculate_fuselage_volume(body_length, body_radius, f.skin_thickness,
                                        nose_length=f.nose_length,
                                        tail_length=f.tail_length)
    mass = calculate_fuselage_mass(body_length, body_radius, f.density,
                                   f.skin_thickness, True, f.nose_length, f.tail_length)
    aero = compute_aero_forces(wing, p)
    geometry_checks = validate_geometry(p)
    geometry_convergence = check_mesh_convergence(p)
    aero_checks = validate_aerodynamics(p)  # cánh phẳng tham chiếu của Khải
    aero_convergence = check_aero_convergence(p)
    return (p, S, surface, volumes, mass, aero,
            geometry_checks, geometry_convergence, aero_checks, aero_convergence)


def progress_table() -> pd.DataFrame:
    """Đọc tiến độ từ PROGRESS.md mỗi lần dashboard chạy lại."""
    rows = []
    for line in (ROOT / "PROGRESS.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        parts = [part.strip() for part in line.strip("| ").split("|")]
        if len(parts) == 3 and parts[0].isdigit():
            rows.append(parts)
    return pd.DataFrame(rows, columns=["Giai đoạn", "Công việc", "Trạng thái"])


def test_status() -> dict | None:
    path = OUTPUTS / "test_results.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


base = load_params()
with st.sidebar:
    st.header("Điều khiển mô hình")
    st.caption("Thay đổi ở đây chỉ áp dụng trên dashboard; params.yaml vẫn giữ nguyên.")
    span = st.slider("Sải cánh b [m]", 6.0, 20.0, float(base.wing.span), 0.5, key="span")
    root_chord = st.number_input("Dây cung gốc [m]", 0.5, 5.0,
                                 float(base.wing.chord_root), 0.1, key="root_chord")
    tip_chord = st.number_input("Dây cung mút [m]", 0.2, 5.0,
                                float(base.wing.chord_tip), 0.1, key="tip_chord")
    body_length = st.slider("Chiều dài thân [m]", 4.0, 16.0,
                            float(base.fuselage.length), 0.5, key="body_length")
    body_radius = st.slider("Bán kính thân [m]", 0.3, 1.5,
                            float(base.fuselage.radius_max), 0.05, key="body_radius")
    resolution = st.slider("Độ phân giải lưới", 16, 120, 100, 4, key="resolution")
    st.divider()
    st.subheader("Hiển thị 3D")
    show_wing = st.checkbox("Cánh", value=True, key="show_wing")
    show_fuselage = st.checkbox("Thân", value=True, key="show_fuselage")
    show_grid = st.checkbox("Lưới tọa độ", value=True, key="show_grid")
    st.caption(f"NACA {base.airfoil.naca}, mật độ vỏ {base.fuselage.density:g} kg/m³ và các giả thiết khí động giữ theo đề.")

if tip_chord > root_chord:
    st.error("Dây cung mút phải nhỏ hơn hoặc bằng dây cung gốc.")
    st.stop()

with st.spinner("Đang tính tích phân và cập nhật mô hình..."):
    (p, S, surface, volumes, mass, aero,
     geometry_checks, geometry_convergence, aero_checks, aero_convergence) = calculate(
        span, root_chord, tip_chord, body_length, body_radius, resolution)

wing = WingModel(span, root_chord, tip_chord, p.airfoil.naca)
bad_geo = geometry_checks[geometry_checks["Đánh giá"] != "ĐẠT"]
bad_aero = aero_checks[aero_checks["Đánh giá"] != "ĐẠT"]

st.title("✈️ GT2 · Tích phân trong mô hình máy bay")
st.caption("Mô hình học tập: hình học NACA 2412, tích phân kép/bội ba và ước lượng lực khí động.")
if not bad_geo.empty:
    st.error(f"Có {len(bad_geo)} mục kiểm chứng hình học chưa đạt. Xem tab Kiểm chứng.")
if not bad_aero.empty:
    st.warning(f"Có {len(bad_aero)} mục kiểm chứng khí động tham chiếu cần xem lại.")
if not math.isfinite(aero.L) or not math.isfinite(aero.D_total) or aero.D_total <= 0:
    st.warning("Kết quả khí động không hợp lý; hãy kiểm tra tham số.")

overview, wing_tab, body_tab, integral_tab, aircraft_tab, checks_tab = st.tabs(
    ["Tổng quan", "Mô hình cánh", "Mô hình thân", "Tích phân", "Máy bay 3D", "Kiểm chứng"])

with overview:
    st.subheader("Kết quả theo tham số đang chọn")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Diện tích chiếu cánh", f"{S:.3f} m²")
    c2.metric("Diện tích hai mặt", f"{surface['total_surface_area']:.3f} m²")
    c3.metric("Thể tích thân đặc", f"{volumes['volume_solid']:.3f} m³")
    c4.metric("Khối lượng vỏ", f"{mass:.1f} kg")
    c5, c6, c7 = st.columns(3)
    c5.metric("Lực nâng ước lượng", f"{aero.L:,.0f} N")
    c6.metric("Lực cản ước lượng", f"{aero.D_total:,.0f} N")
    c7.metric("Kiểm chứng", f"{len(geometry_checks)-len(bad_geo)}/{len(geometry_checks)} hình học")
    st.info("Bộ kiểm chứng khí động của Khải đạt "
            f"{len(aero_checks)-len(bad_aero)}/{len(aero_checks)} mục trên cánh phẳng tham chiếu. "
            "Lực bên trên được tính trên cánh NACA dày, nên không xem đây là chứng minh khí động đầy đủ.")
    col_a, col_b = st.columns([1, 1.5])
    with col_a:
        st.markdown("#### Thông số đầu vào")
        st.dataframe(pd.DataFrame([
            ("NACA", p.airfoil.naca, "-"), ("Sải cánh", span, "m"),
            ("Dây cung gốc/mút", f"{root_chord:g} / {tip_chord:g}", "m"),
            ("Thân dài", body_length, "m"), ("Bán kính thân", body_radius, "m"),
            ("Vận tốc dòng", p.flow.V_inf, "m/s"), ("Góc tới", p.flow.alpha_deg, "độ"),
        ], columns=["Tham số", "Giá trị", "Đơn vị"], dtype=str), hide_index=True)
    with col_b:
        st.markdown("#### Tiến độ")
        progress = progress_table()
        st.progress((progress["Trạng thái"] == "Hoàn thành").mean() if not progress.empty else 0.0)
        st.dataframe(progress, hide_index=True)
        st.caption("Nguồn: PROGRESS.md. Bấm nút hoặc thay tham số để cập nhật tiến độ mới nhất.")
        if st.button("Làm mới tiến độ"):
            st.rerun()

with wing_tab:
    st.subheader("Biên dạng NACA 2412")
    x = (1 - np.cos(np.linspace(0, np.pi, 300))) / 2
    xu, zu, xl, zl = get_airfoil_coordinates(x, p.airfoil.naca)
    profile = go.Figure()
    profile.add_scatter(x=xu, y=zu, name="Mặt trên", line_color="#247BA0")
    profile.add_scatter(x=xl, y=zl, name="Mặt dưới", line_color="#E38B29")
    profile.add_scatter(x=x, y=(zu+zl)/2, name="Camber", line=dict(color="#687A87", dash="dash"))
    profile.update_layout(xaxis_title="x/c", yaxis_title="z/c", height=340,
                          margin=dict(l=10, r=10, t=20, b=20))
    profile.update_yaxes(scaleanchor="x", scaleratio=1)
    st.plotly_chart(profile, width="stretch")
    st.caption("Hàm NACA trả tọa độ chuẩn hóa; nhân với dây cung c(y) để tạo cánh 3D.")
    st.plotly_chart(build_wing_figure(p, resolution=resolution, show_grid=show_grid),
                    width="stretch")
    st.metric("Diện tích bề mặt (hai mặt)", f"{surface['total_surface_area']:.4f} m²")

with body_tab:
    st.subheader("Bán kính thân theo trục x")
    xs = np.linspace(0, body_length, 300)
    rs = fuselage_radius(xs, body_length, body_radius,
                         p.fuselage.nose_length, p.fuselage.tail_length)
    radius_fig = go.Figure()
    radius_fig.add_scatter(x=xs, y=rs, fill="tozeroy", line_color="#C78F35",
                           name="Bán kính r(x)")
    radius_fig.update_layout(xaxis_title="x [m]", yaxis_title="r(x) [m]", height=300,
                             margin=dict(l=10, r=10, t=20, b=20))
    st.plotly_chart(radius_fig, width="stretch")
    st.plotly_chart(build_fuselage_figure(p, resolution=resolution, show_grid=show_grid),
                    width="stretch")
    st.dataframe(pd.DataFrame([
        ("Thể tích thân đặc", volumes["volume_solid"], "m³"),
        ("Thể tích vỏ", volumes["volume_skin"], "m³"),
        ("Khối lượng vỏ", mass, "kg"),
    ], columns=["Đại lượng", "Giá trị", "Đơn vị"]), hide_index=True)

with integral_tab:
    st.subheader("Từ hình dạng đến tích phân")
    left, right = st.columns(2)
    with left:
        st.markdown("**Diện tích hình chiếu cánh**")
        st.latex(r"S=\int_{-b/2}^{b/2}\int_0^1 c(y)\,du\,dy=\frac{b(c_{root}+c_{tip})}{2}")
        st.write(f"Kết quả: **{S:.4f} m²**. `dblquad` kiểm tra công thức hình thang.")
        st.markdown("**Diện tích bề mặt cánh**")
        st.latex(r"A=\sum_{\pm}\iint\|\mathbf r_u\times\mathbf r_y\|\,du\,dy")
        st.write(f"Kết quả: **{surface['total_surface_area']:.4f} m²**. "
                 "Python lấy điểm Gauss và cộng `giá trị × trọng số` trên hai mặt.")
        st.markdown("**Thể tích và khối lượng thân**")
        st.latex(r"V=\int_0^L\int_0^{2\pi}\int_0^{r(x)} s\,ds\,d\theta\,dx")
        st.latex(r"m=\rho_{mat}\,V_{skin}")
        st.write(f"Thân đặc **{volumes['volume_solid']:.4f} m³**; "
                 f"vỏ **{volumes['volume_skin']:.4f} m³**; khối lượng **{mass:.2f} kg**.")
    with right:
        st.markdown("**Miền tích phân cánh nhìn từ trên**")
        ys = np.linspace(-span/2, span/2, 200)
        chords = chord_distribution(ys, span, root_chord, tip_chord)
        domain = go.Figure()
        domain.add_scatter(x=ys, y=chords, fill="tozeroy", fillcolor="rgba(36,123,160,0.25)",
                           line_color="#247BA0", name="0 ≤ x ≤ c(y)")
        domain.update_layout(xaxis_title="Vị trí theo sải y [m]", yaxis_title="Dây cung c(y) [m]",
                             height=370, margin=dict(l=10, r=10, t=20, b=20))
        st.plotly_chart(domain, width="stretch")
        st.caption("Phần tô màu là miền ∬dxdy dùng để tính diện tích hình chiếu.")
    st.markdown("#### So sánh tích phân số và tham chiếu")
    st.dataframe(geometry_checks, hide_index=True, width="stretch")
    st.caption("Hàng diện tích bề mặt chỉ kiểm tra cận dưới A>2S; 2S không phải giá trị giải tích chính xác.")

with aircraft_tab:
    st.subheader("Mô hình lắp ghép tương tác")
    st.caption("Dùng chuột kéo để xoay 360°, cuộn để zoom. Bật/tắt cánh, thân và lưới ở thanh bên.")
    if not show_wing and not show_fuselage:
        st.warning("Hãy bật ít nhất cánh hoặc thân ở thanh bên.")
    else:
        full_fig = build_aircraft_figure(p, show_wing=show_wing,
                                         show_fuselage=show_fuselage,
                                         show_grid=show_grid,
                                         resolution=resolution)
        st.plotly_chart(full_fig, width="stretch")
        st.download_button("Tải mô hình 3D HTML với tham số đang chọn",
                           data=full_fig.to_html(include_plotlyjs=True),
                           file_name="aircraft_model_current.html", mime="text/html")
    st.info("Vị trí cánh trên thân chỉ để minh họa lắp ghép. Chương trình chưa mô hình hóa động cơ, đuôi, khung sườn hoặc lực của thân.")

with checks_tab:
    st.subheader("Kiểm chứng và hội tụ")
    a, b = st.columns(2)
    a.metric("Hình học", f"{len(geometry_checks)-len(bad_geo)}/{len(geometry_checks)} đạt")
    b.metric("Khí động cánh phẳng tham chiếu", f"{len(aero_checks)-len(bad_aero)}/{len(aero_checks)} đạt")
    st.markdown("#### Sai số hình học")
    st.dataframe(geometry_checks, hide_index=True, width="stretch")
    st.markdown("#### Sai số khí động (cánh phẳng tham chiếu)")
    aero_display = aero_checks.drop(columns=["Ghi chú"]).copy()
    aero_display["Tham chiếu"] = aero_display["Tham chiếu"].astype(str)
    st.dataframe(aero_display, hide_index=True, width="stretch")
    left, right = st.columns(2)
    with left:
        conv_geo_fig = go.Figure()
        conv_geo_fig.add_scatter(x=geometry_convergence["n_u"],
                                 y=geometry_convergence["Sai số so lưới mịn nhất (%)"],
                                 mode="lines+markers", name="Diện tích cánh")
        conv_geo_fig.update_layout(title="Hội tụ tích phân diện tích",
                                   xaxis_title="Số nút theo dây cung", yaxis_title="Sai số [%]",
                                   height=350)
        st.plotly_chart(conv_geo_fig, width="stretch")
    with right:
        conv_aero_fig = go.Figure()
        conv_aero_fig.add_scatter(x=aero_convergence["n_theta"],
                                  y=aero_convergence["Sai số L (%)"],
                                  mode="lines+markers", name="Lực nâng")
        conv_aero_fig.update_layout(title="Hội tụ tích phân lực",
                                    xaxis_title="Số nút theo dây cung", yaxis_title="Sai số [%]",
                                    height=350)
        st.plotly_chart(conv_aero_fig, width="stretch")
    st.markdown("#### Bài kiểm thử tự động")
    status = test_status()
    if status:
        st.write(f"Lần chạy gần nhất: **{status['tests_run']} bài**, "
                 f"**{status['failures']} lỗi kết quả**, **{status['errors']} lỗi chạy**. "
                 f"Trạng thái: **{'ĐẠT' if status['success'] else 'CHƯA ĐẠT'}**.")
        if status.get("excluded_placeholders", 0):
            st.caption(f"Đã loại {status['excluded_placeholders']} bài test khung `pass` khỏi thống kê.")
        with st.expander("Xem log kiểm thử"):
            st.code(status["output"])
    else:
        st.info("Chưa có kết quả kiểm thử. Bấm nút bên dưới để chạy.")
    if st.button("Chạy lại kiểm thử"):
        with st.spinner("Đang chạy unittest..."):
            subprocess.run([sys.executable, "run_checks.py"], cwd=ROOT, check=False)
        st.rerun()

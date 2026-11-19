"""Chạy toàn bộ bài tập: hình học, khí động, kiểm chứng và xuất báo cáo.

Mặc định ghi bảng vào results/tables và hình vào results/figures (theo README).
# AI-assisted: xem AI_DECLARATION.md
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from src.aero import compute_aero_forces
from src.config import RESULTS_DIR, Params, load_params
from src.fuselage import (calculate_fuselage_mass, calculate_fuselage_surface_area,
                          calculate_fuselage_volume)
from src.validate import (check_aero_convergence, check_mesh_convergence,
                          independent_checks, validate_aerodynamics, validate_geometry)
from src.visualize import (build_aircraft_figure, plot_airfoil_2d,
                           plot_convergence, plot_cp_distribution,
                           plot_fuselage_3d_matplotlib, plot_fuselage_profile_2d,
                           plot_lift_drag_polar, plot_lift_vs_velocity,
                           plot_skin_mass_vs_thickness, plot_span_loading,
                           plot_wing_3d_matplotlib, plot_wing_planform_2d,
                           render_full_aircraft_plotly, sweep_alpha, sweep_velocity)
from src.wing import (WingModel, calculate_projected_area, calculate_surface_area,
                      calculate_wing_volume)

PROJECT_ROOT = Path(__file__).resolve().parent


def run_pipeline(config: Params | None = None, output_root: Path | None = None,
                 generate_figures: bool = True) -> dict:
    """Tính toàn bộ từ tham số; trả summary và lưu file CSV/JSON/PNG/HTML."""
    p = config or load_params()
    out = Path(output_root) if output_root else RESULTS_DIR
    tables, figures = out / "tables", out / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    w, f = p.wing, p.fuselage
    wing = WingModel(w.span, w.chord_root, w.chord_tip, p.airfoil.naca)
    S = calculate_projected_area(w.span, w.chord_root, w.chord_tip)
    areas = calculate_surface_area(w.span, w.chord_root, w.chord_tip,
                                   p.airfoil.naca, w.n_chord, w.n_span)
    volumes = calculate_fuselage_volume(f.length, f.radius_max, f.skin_thickness,
                                        nose_length=f.nose_length,
                                        tail_length=f.tail_length)
    mass = calculate_fuselage_mass(f.length, f.radius_max, f.density,
                                   f.skin_thickness, True,
                                   f.nose_length, f.tail_length)
    volume_wing = calculate_wing_volume(w.span, w.chord_root, w.chord_tip, p.airfoil.naca)
    area_fuselage = calculate_fuselage_surface_area(f.length, f.radius_max,
                                                    f.nose_length, f.tail_length)
    aero = compute_aero_forces(wing, p)

    geometry_checks = validate_geometry(p)
    geometry_convergence = check_mesh_convergence(p)
    # Các công thức tham chiếu trong phần Khải giả thiết cánh phẳng; giữ nguyên
    # bộ kiểm chứng của Khải và chạy trên đối tượng cánh phẳng mặc định của nó.
    aero_checks = validate_aerodynamics(p)
    aero_convergence = check_aero_convergence(p)
    geometry_checks.to_csv(tables / "validation_geometry.csv", index=False, encoding="utf-8-sig")
    geometry_convergence.to_csv(tables / "convergence_geometry.csv", index=False, encoding="utf-8-sig")
    aero_checks.to_csv(tables / "validation_aero_reference.csv", index=False, encoding="utf-8-sig")
    aero_convergence.to_csv(tables / "convergence_aero_reference.csv", index=False, encoding="utf-8-sig")
    independent_checks(p).to_csv(tables / "independent_checks.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(aero.as_rows(), columns=["Đại lượng", "Giá trị", "Đơn vị", "Mô tả"]).to_csv(
        tables / "aero_results.csv", index=False, encoding="utf-8-sig")

    summary_rows = [
        ("S_projected", S, "m²"),
        ("A_upper", areas["area_upper"], "m²"),
        ("A_lower", areas["area_lower"], "m²"),
        ("A_total", areas["total_surface_area"], "m²"),
        ("V_wing", volume_wing, "m³"),
        ("V_solid", volumes["volume_solid"], "m³"),
        ("V_skin", volumes["volume_skin"], "m³"),
        ("mass_skin", mass, "kg"),
        ("A_fuselage", area_fuselage, "m²"),
        ("Lift", aero.L, "N"),
        ("Drag", aero.D_total, "N"),
        ("CL", aero.CL, "-"),
        ("CD", aero.CD, "-"),
    ]
    pd.DataFrame(summary_rows, columns=["quantity", "value", "unit"]).to_csv(
        tables / "summary.csv", index=False, encoding="utf-8-sig")

    # Khảo sát theo góc tới và vận tốc (Khải): dùng lại compute_aero_forces()
    alpha_sweep = sweep_alpha(p, np.arange(-2, 13, 1.0), wing)
    pd.DataFrame(alpha_sweep).to_csv(tables / "alpha_sweep.csv", index=False, encoding="utf-8-sig")
    velocity_sweep = sweep_velocity(p, [30, 40, 50, 60, 70, 80], wing)
    pd.DataFrame(velocity_sweep).to_csv(tables / "velocity_sweep.csv", index=False,
                                        encoding="utf-8-sig")
    skin_rows = []
    for t_mm in (1, 2, 3, 4, 5, 6):
        for rho_name, rho in (("Nhôm", f.density), ("Composite", 1600.0)):
            vol = calculate_fuselage_volume(f.length, f.radius_max, t_mm / 1000,
                                            nose_length=f.nose_length, tail_length=f.tail_length)
            skin_rows.append((rho_name, rho, t_mm, vol["volume_skin"], rho * vol["volume_skin"]))
    pd.DataFrame(skin_rows, columns=["Vật liệu", "rho [kg/m³]", "t_v [mm]", "V_vỏ [m³]",
                                     "m_vỏ [kg]"]).to_csv(tables / "skin_sweep.csv", index=False,
                                                          encoding="utf-8-sig")

    if generate_figures:
        # Hình 2D cho Chương 3 và 4
        plot_airfoil_2d(p.airfoil.naca, figures / "airfoil_profile.png")
        plot_wing_planform_2d(p, figures / "wing_planform_2d.png")
        plot_fuselage_profile_2d(p, figures / "fuselage_profile_2d.png")
        plot_skin_mass_vs_thickness(p, figures / "skin_mass_vs_thickness.png")
        plot_cp_distribution(p, figures / "cp_distribution.png", wing=wing)
        plot_lift_drag_polar(alpha_sweep["alpha"], alpha_sweep["L"], alpha_sweep["D"],
                             figures / "lift_drag_polar.png", q_S=p.q_inf * S)
        plot_span_loading(p, figures / "span_loading.png", wing=wing)
        plot_lift_vs_velocity(p, figures / "lift_vs_velocity.png", wing=wing)
        plot_convergence(geometry_convergence, aero_convergence, figures / "convergence.png")
        # Hình 3D (dành cho Chương 5)
        plot_wing_3d_matplotlib(p, figures / "wing_3d.png")
        plot_fuselage_3d_matplotlib(p, figures / "fuselage_3d.png")
        render_full_aircraft_plotly(p, figures / "aircraft_model.html")
        build_aircraft_figure(p).write_image(figures / "aircraft_3d.png",
                                              width=1200, height=800, scale=2)

    bad_geometry = geometry_checks[geometry_checks["Đánh giá"] != "ĐẠT"]
    bad_aero = aero_checks[aero_checks["Đánh giá"] != "ĐẠT"]
    summary = {
        "parameters": asdict(p),
        "geometry": {"S_projected_m2": S, **areas, **volumes, "mass_skin_kg": mass,
                     "volume_wing_m3": volume_wing, "area_fuselage_m2": area_fuselage},
        "aerodynamics": asdict(aero),
        "validation": {
            "geometry_passed": int(len(geometry_checks) - len(bad_geometry)),
            "geometry_total": int(len(geometry_checks)),
            "aero_reference_passed": int(len(aero_checks) - len(bad_aero)),
            "aero_reference_total": int(len(aero_checks)),
            "aero_reference_note": "Bộ kiểm chứng của Khải dùng cánh phẳng tham chiếu; lực máy bay dùng cánh NACA 2412.",
        },
    }
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    if not bad_geometry.empty or not bad_aero.empty:
        raise RuntimeError("Có kiểm chứng không đạt; xem results/tables/validation_*.csv")
    return summary


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("Đang tính hình học, tích phân, lực khí động và xuất hình...")
    result = run_pipeline()
    g, a, v = result["geometry"], result["aerodynamics"], result["validation"]
    print(f"Diện tích chiếu cánh: {g['S_projected_m2']:.4f} m²")
    print(f"Diện tích hai mặt cánh: {g['total_surface_area']:.4f} m²")
    print(f"Thể tích thân đặc / vỏ: {g['volume_solid']:.4f} / {g['volume_skin']:.4f} m³")
    print(f"Khối lượng vỏ: {g['mass_skin_kg']:.2f} kg")
    print(f"Lực nâng / cản ước lượng: {a['L']:.2f} / {a['D_total']:.2f} N")
    print(f"Kiểm chứng hình học: {v['geometry_passed']}/{v['geometry_total']} đạt")
    print(f"Kiểm chứng khí động cánh phẳng: {v['aero_reference_passed']}/{v['aero_reference_total']} đạt")
    print(f"Thể tích khối cánh: {g['volume_wing_m3']:.4f} m³")
    print(f"Diện tích mặt ngoài thân: {g['area_fuselage_m2']:.4f} m²")
    print(f"Bảng và hình đã lưu tại: {RESULTS_DIR}")


if __name__ == "__main__":
    main()

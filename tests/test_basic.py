"""
Module test_basic.py: Các bài kiểm thử đơn vị (Unit Tests) cho các trường hợp đơn giản.
Người phụ trách:
- Trương Thanh Vĩ: Test biên dạng airfoil, diện tích cánh chữ nhật, thể tích thân hình trụ
- Hà Ngọc Khải: Test hướng lực nâng/cản, thứ nguyên và bậc độ lớn khí động học
"""

import unittest
import numpy as np

from src.config import load_params
from src.airfoil import naca4_thickness, naca4_camber, parse_naca4
from src.wing import calculate_projected_area, calculate_surface_area, WingModel
from src.fuselage import (calculate_fuselage_volume, analytical_fuselage_volume,
                          calculate_fuselage_mass)


class TestAircraftModeling(unittest.TestCase):

    def setUp(self):
        """Khởi tạo tham số mẫu cho test."""
        self.config = load_params()

    # ==========================================================================
    # PHẦN TEST CỦA TRƯƠNG THANH VĨ
    # ==========================================================================

    def test_naca_parsing(self):
        """NACA 2412 và 0012 có các tỷ lệ camber, vị trí, độ dày đúng."""
        self.assertEqual(parse_naca4("2412"), (0.02, 0.4, 0.12))
        self.assertEqual(parse_naca4("0012"), (0.0, 0.0, 0.12))
        with self.assertRaises(ValueError):
            parse_naca4("241")

    def test_airfoil_edges_thickness(self):
        """Biên cánh kín, có độ dày ở giữa và camber đạt cực đại tại x/c=p."""
        self.assertAlmostEqual(naca4_thickness(0.0), 0.0, places=12)
        self.assertAlmostEqual(naca4_thickness(1.0), 0.0, places=12)
        self.assertGreater(naca4_thickness(0.5), 0.0)
        camber, slope = naca4_camber(0.4)
        self.assertAlmostEqual(camber, 0.02, places=12)
        self.assertAlmostEqual(slope, 0.0, places=12)

    def test_rectangular_wing_projected_area(self):
        """Cánh chữ nhật có S=bc, tích phân kép khớp công thức."""
        for method in ("analytical", "numerical"):
            self.assertAlmostEqual(calculate_projected_area(10, 1.5, 1.5, method),
                                   15.0, places=8)

    def test_fuselage_volume_cylinder(self):
        """Khi bỏ mũi và đuôi, tích phân 1D/bội ba phải bằng πR²L."""
        exact = np.pi * 10.0
        for method in ("single_integral", "triple_integral"):
            calc = calculate_fuselage_volume(10, 1, 0, method,
                                             nose_length=0, tail_length=0)
            self.assertAlmostEqual(calc["volume_solid"], exact, places=6)

    def test_default_fuselage_vs_closed_formula(self):
        """Thân ba đoạn khớp công thức đóng và khối lượng bằng mật độ × thể tích vỏ."""
        f = self.config.fuselage
        kw = dict(nose_length=f.nose_length, tail_length=f.tail_length)
        volume = calculate_fuselage_volume(f.length, f.radius_max, f.skin_thickness, **kw)
        exact = analytical_fuselage_volume(f.length, f.radius_max, **kw)
        self.assertAlmostEqual(volume["volume_solid"], exact, places=7)
        self.assertGreater(volume["volume_skin"], 0)
        self.assertLess(volume["volume_skin"], volume["volume_solid"])
        self.assertAlmostEqual(calculate_fuselage_mass(
            f.length, f.radius_max, f.density, f.skin_thickness, True, **kw),
            f.density * volume["volume_skin"], places=6)

    def test_wing_surface_area_converges(self):
        """Diện tích mặt cánh phải > 2S và ổn định khi tăng nút tích phân."""
        w = self.config.wing
        coarse = calculate_surface_area(w.span, w.chord_root, w.chord_tip,
                                        n_u=32, n_v=16)["total_surface_area"]
        fine = calculate_surface_area(w.span, w.chord_root, w.chord_tip,
                                      n_u=128, n_v=64)["total_surface_area"]
        self.assertGreater(fine, 2 * calculate_projected_area(w.span, w.chord_root, w.chord_tip))
        self.assertLess(abs(fine - coarse) / fine, 1e-4)

    def test_wing_api_vectorized(self):
        """Hình học cánh hỗ trợ lưới mảng và khớp dây cung ở gốc/mút."""
        wing = WingModel(10, 1.8, 0.9, "2412")
        u, v = np.meshgrid([0, 1], [0, 5])
        X, Y, Z = wing.surface(u, v, +1)
        self.assertEqual(X.shape, (2, 2))
        np.testing.assert_allclose(X, [[0, 1.8], [0, 0.9]])
        np.testing.assert_allclose(Y, v)
        self.assertTrue(np.isfinite(Z).all())

    # ==========================================================================
    # PHẦN TEST CỦA HÀ NGỌC KHẢI
    # ==========================================================================

    # AI-assisted: xem AI_DECLARATION.md

    def _aero(self, alpha_deg, V=None):
        import copy
        from src.aero import compute_aero_forces
        p = copy.deepcopy(self.config)
        p.flow.alpha_deg = alpha_deg
        if V is not None:
            p.flow.V_inf = V
        w = p.wing
        return compute_aero_forces(WingModel(w.span, w.chord_root, w.chord_tip, p.airfoil.naca), p)

    def test_lift_direction_positive_alpha(self):
        """Khi alpha > alpha_L0 thì L > 0 và D > 0; tại alpha = alpha_L0 thì L ≈ 0."""
        for alpha in (1.0, 4.0, 8.0):
            r = self._aero(alpha)
            self.assertGreater(r.L, 0.0, f"L phải dương tại α = {alpha}°")
            self.assertGreater(r.D_total, 0.0, "Lực cản luôn dương (cản lại chuyển động)")
        r0 = self._aero(self.config.aero.alpha_L0_deg)
        self.assertLess(abs(r0.L), 0.01 * self._aero(4.0).L,
                        "Tại góc nâng không α_L0, lực nâng gần bằng 0")
        # Lực nâng tăng đơn điệu theo góc tới trong vùng tuyến tính
        lifts = [self._aero(a).L for a in (0.0, 2.0, 4.0, 6.0)]
        self.assertTrue(all(b > a for a, b in zip(lifts, lifts[1:])))

    def test_aerodynamic_force_magnitude(self):
        """Bậc độ lớn: 10^3 <= L <= 10^5 N, C_L cỡ 2πα_e, L tỉ lệ V², L/D trong khoảng hợp lý."""
        import math
        r = self._aero(4.0)
        self.assertGreaterEqual(r.L, 1e3)
        self.assertLessEqual(r.L, 1e5)
        alpha_e = math.radians(4.0 - self.config.aero.alpha_L0_deg)
        self.assertLess(r.CL, 2 * math.pi * alpha_e, "Cánh hữu hạn có C_L nhỏ hơn 2πα_e")
        self.assertGreater(r.CL, 0.5 * 2 * math.pi * alpha_e)
        r2 = self._aero(4.0, V=2 * self.config.flow.V_inf)
        self.assertAlmostEqual(r2.L / r.L, 4.0, delta=0.01, msg="Áp suất tỉ lệ V² nên L(2V) = 4L(V)")
        self.assertTrue(5 < r.L_over_D < 60)

    def test_elliptic_loading_total_lift(self):
        """Tải elip: lực pháp tuyến N = L_p·cosα phải bằng q·a·α_e·S (tức C_L,p = a·α_e)."""
        import math
        r = self._aero(4.0)
        N = r.L_pressure * math.cos(math.radians(4.0))
        self.assertAlmostEqual(N / (r.q_inf * r.lift_slope * math.radians(r.alpha_eff_deg) * r.S_ref),
                               1.0, places=4)

    def test_fuselage_surface_area_cylinder(self):
        """Bổ sung: thân trụ (không mũi/đuôi) có diện tích mặt bên 2πRL; hai cách tính khớp nhau."""
        import math
        from src.fuselage import calculate_fuselage_surface_area
        a = calculate_fuselage_surface_area(8.0, 0.7, 0.0, 0.0)
        self.assertAlmostEqual(a, 2 * math.pi * 0.7 * 8.0, places=6)
        f = self.config.fuselage
        a2 = calculate_fuselage_surface_area(f.length, f.radius_max, f.nose_length, f.tail_length)
        a1 = calculate_fuselage_surface_area(f.length, f.radius_max, f.nose_length, f.tail_length,
                                             method="single_integral")
        self.assertAlmostEqual(a2, a1, places=6)


if __name__ == "__main__":
    unittest.main()

"""
Module test_basic.py: Các bài kiểm thử đơn vị (Unit Tests) cho các trường hợp đơn giản.
Người phụ trách:
- Trương Thanh Vĩ: Test biên dạng airfoil, diện tích cánh chữ nhật, thể tích thân hình trụ
- Hà Ngọc Khải: Test hướng lực nâng/cản, thứ nguyên và bậc độ lớn khí động học
"""

import unittest
import numpy as np
from pathlib import Path

from src.config import load_params
from src.airfoil import naca4_thickness, parse_naca4
from src.wing import calculate_projected_area
from src.fuselage import calculate_fuselage_volume


class TestAircraftModeling(unittest.TestCase):

    def setUp(self):
        """Khởi tạo tham số mẫu cho test."""
        self.config = load_params()

    # ==========================================================================
    # PHẦN TEST CỦA TRƯƠNG THANH VĨ
    # ==========================================================================

    def test_naca_parsing(self):
        """TODO (Trương Thanh Vĩ): Kiểm tra phân tích mã NACA 2412."""
        # m, p, t = parse_naca4("2412")
        # self.assertAlmostEqual(m, 0.02)
        # self.assertAlmostEqual(p, 0.4)
        # self.assertAlmostEqual(t, 0.12)
        pass

    def test_airfoil_edges_thickness(self):
        """TODO (Trương Thanh Vĩ): Kiểm tra độ dày tại mép trước (x=0) và mép sau (x=1)."""
        # y_t_0 = naca4_thickness(0.0, t=0.12)
        # self.assertAlmostEqual(y_t_0, 0.0, places=4)
        pass

    def test_rectangular_wing_projected_area(self):
        """TODO (Trương Thanh Vĩ): Kiểm tra diện tích hình chiếu của cánh chữ nhật (c_root == c_tip)."""
        # b = 10.0
        # c = 1.5
        # exact_area = b * c
        # calc_area = calculate_projected_area(b=b, c_root=c, c_tip=c, method="analytical")
        # self.assertAlmostEqual(calc_area, exact_area, places=4)
        pass

    def test_fuselage_volume_cylinder(self):
        """TODO (Trương Thanh Vĩ): Kiểm tra thể tích thân máy bay với trường hợp trụ thẳng."""
        # L = 10.0
        # R = 1.0
        # exact_vol = np.pi * (R**2) * L
        # TODO: đối chiếu với hàm tính thể tích
        pass

    # ==========================================================================
    # PHẦN TEST CỦA HÀ NGỌC KHẢI
    # ==========================================================================

    def test_lift_direction_positive_alpha(self):
        """TODO (Hà Ngọc Khải): Khi góc tới alpha > 0, lực nâng L phải mang giá trị dương (> 0)."""
        pass

    def test_aerodynamic_force_magnitude(self):
        """TODO (Hà Ngọc Khải): Kiểm tra bậc độ lớn của lực nâng (phải nằm trong khoảng hợp lý 10^3 - 10^5 N)."""
        pass


if __name__ == "__main__":
    unittest.main()

"""Kiểm thử ghép module và pipeline; không thay thế phần mã khí động của Khải.
# AI-assisted: xem AI_DECLARATION.md
"""

import json
import math
import tempfile
import unittest
from pathlib import Path

from main import run_pipeline
from src.aero import compute_aero_forces
from src.config import load_params
from src.validate import validate_aerodynamics, validate_geometry
from src.wing import WingModel, calculate_projected_area


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.p = load_params()
        w = self.p.wing
        self.wing = WingModel(w.span, w.chord_root, w.chord_tip, self.p.airfoil.naca)

    def test_actual_wing_connects_to_aero(self):
        """Cánh NACA giao tiếp được với tích phân lực, kết quả hữu hạn và đúng S."""
        result = compute_aero_forces(self.wing, self.p)
        self.assertAlmostEqual(result.S_ref, calculate_projected_area(
            self.p.wing.span, self.p.wing.chord_root, self.p.wing.chord_tip), places=7)
        self.assertTrue(math.isfinite(result.L) and math.isfinite(result.D_total))
        self.assertGreater(result.L, 0)
        self.assertGreater(result.D_total, 0)

    def test_geometry_validation(self):
        """Tất cả đối chiếu hình học và điều kiện cận dưới phải đạt."""
        checks = validate_geometry(self.p)
        self.assertGreaterEqual(len(checks), 5)
        self.assertTrue((checks["Đánh giá"] == "ĐẠT").all())

    def test_aero_reference_validation(self):
        """Giữ nguyên bộ kiểm chứng khí động của Khải trên cánh phẳng tham chiếu."""
        checks = validate_aerodynamics(self.p)
        self.assertTrue((checks["Đánh giá"] == "ĐẠT").all())

    def test_pipeline_writes_real_tables(self):
        """Pipeline chạy từ tham số và xuất CSV/JSON chứa giá trị dương thực tế."""
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            summary = run_pipeline(self.p, out, generate_figures=False)
            self.assertTrue((out / "summary.json").is_file())
            self.assertTrue((out / "tables" / "validation_geometry.csv").is_file())
            self.assertTrue((out / "tables" / "aero_results.csv").is_file())
            saved = json.loads((out / "summary.json").read_text(encoding="utf-8"))
            self.assertGreater(saved["geometry"]["S_projected_m2"], 0)
            self.assertAlmostEqual(saved["geometry"]["S_projected_m2"],
                                   summary["geometry"]["S_projected_m2"])

"""
File main.py: Chạy toàn bộ quy trình tính toán (Pipeline), in và xuất kết quả.
Người phụ trách: Cả hai (Hà Ngọc Khải & Trương Thanh Vĩ)
Review: Nhóm trưởng

Quy trình thực thi:
1. Đọc cấu hình từ params.yaml.
2. Tính toán hình học: Biên dạng cánh, diện tích cánh (tích phân kép), thể tích & khối lượng thân (tích phân bội ba).
3. Tính toán khí động học: Ước lượng lực nâng, lực cản và áp suất bằng tích phân mặt.
4. Kiểm chứng kết quả (validation): So sánh với công thức giải tích và lý thuyết.
5. Xuất bảng dữ liệu ra thư mục results/tables/.
6. Tạo và lưu trực quan hóa hình ảnh 3D và đồ thị ra thư mục results/figures/.
"""

import sys
from pathlib import Path
import pandas as pd

# Import các module trong src/
from src.config import load_params, get_project_root
from src.wing import calculate_projected_area, calculate_surface_area
from src.fuselage import calculate_fuselage_volume, calculate_fuselage_mass
from src.aero import calculate_aerodynamic_forces
from src.validate import validate_geometry, validate_aerodynamics
from src.visualize import (
    plot_airfoil_2d,
    plot_wing_3d_matplotlib,
    plot_fuselage_3d_matplotlib,
    render_full_aircraft_plotly,
    plot_cp_distribution
)


def ensure_output_directories():
    """Tạo sẵn các thư mục đầu ra nếu chưa tồn tại."""
    root = get_project_root()
    tables_dir = root / "results" / "tables"
    figures_dir = root / "results" / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    return tables_dir, figures_dir


def main():
    print("=" * 70)
    print(" BÀI TẬP LỚN GIẢI TÍCH 3: ỨNG DỤNG TÍCH PHÂN TRONG MÔ HÌNH HÓA MÁY BAY")
    print(" Thực hiện: Trương Thanh Vĩ & Hà Ngọc Khải")
    print("=" * 70)

    tables_dir, figures_dir = ensure_output_directories()

    # Bước 1: Nạp cấu hình tham số
    # --------------------------------------------------------------------------
    print("\n[Bước 1] Nạp tham số từ params.yaml...")
    config = load_params()
    print("  -> Đã nạp thành công các thông số đầu vào.")

    # Bước 2: Tính toán hình học cánh và thân (Phần việc của Trương Thanh Vĩ)
    # --------------------------------------------------------------------------
    print("\n[Bước 2 - VĨ] Tính toán hình học, diện tích và thể tích...")
    # TODO (Trương Thanh Vĩ & Cả hai):
    # - Gọi calculate_projected_area, calculate_surface_area từ wing.py
    # - Gọi calculate_fuselage_volume, calculate_fuselage_mass từ fuselage.py
    # - In các thông số tóm tắt ra màn hình console

    # Bước 3: Tính toán khí động học và tích phân mặt (Phần việc của Hà Ngọc Khải)
    # --------------------------------------------------------------------------
    print("\n[Bước 3 - KHẢI] Tính toán lực nâng, lực cản bằng tích phân mặt...")
    # TODO (Hà Ngọc Khải & Cả hai):
    # - Gọi calculate_aerodynamic_forces từ aero.py
    # - In giá trị lực nâng Lift (N), lực cản Drag (N), hệ số CL, CD ra màn hình console

    # Bước 4: Kiểm chứng kết quả với giải tích & lý thuyết (Cả hai)
    # --------------------------------------------------------------------------
    print("\n[Bước 4 - CẢ HAI] Tiến hành kiểm chứng kết quả số trị...")
    # TODO (Vĩ & Khải):
    # - Vĩ: validate_geometry
    # - Khải: validate_aerodynamics
    # - Xuất các bảng đối chiếu ra file CSV / Markdown trong results/tables/

    # Bước 5: Trực quan hóa và xuất đồ thị, mô hình 3D
    # --------------------------------------------------------------------------
    print("\n[Bước 5 - CẢ HAI] Xuất trực quan hóa đồ thị và mô hình 3D...")
    # TODO (Trương Thanh Vĩ):
    # - Xuất hình airfoil 2D, cánh 3D, thân 3D vào results/figures/
    # - Xuất mô hình tương tác HTML bằng Plotly: aircraft_model.html
    # TODO (Hà Ngọc Khải):
    # - Xuất đồ thị phân bố hệ số áp suất Cp: cp_distribution.png
    # - Xuất đồ thị đặc tuyến lực nâng - lực cản: lift_drag_polar.png

    print("\n" + "=" * 70)
    print(" HOÀN THÀNH PIPELINE TÍNH TOÁN!")
    print(f" Kết quả bảng lưu tại: {tables_dir}")
    print(f" Kết quả đồ thị lưu tại: {figures_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()

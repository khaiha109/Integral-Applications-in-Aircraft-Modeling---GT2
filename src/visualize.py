"""
Module visualize.py: Trực quan hóa hình học 3D, vẽ đồ thị phân bố áp suất và xuất kết quả.
Người phụ trách:
- Trương Thanh Vĩ: Trực quan hóa 3D (Matplotlib 3D, Plotly Interactive 3D HTML, xuất ảnh mô hình 3D)
- Hà Ngọc Khải: Biểu đồ khí động học 2D (phân bố Cp, đường đặc tuyến nâng/cản theo alpha, xuất đồ thị kết quả)
"""

from pathlib import Path
from typing import Dict, Any
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from src.airfoil import get_airfoil_coordinates
from src.wing import wing_surface
from src.fuselage import fuselage_surface_3d


# ==============================================================================
# PHẦN VIỆC CỦA TRƯƠNG THANH VĨ (Trực quan hóa 3D)
# ==============================================================================

def plot_airfoil_2d(naca_code: str = "2412", save_path: Path | str | None = None) -> None:
    """
    Vẽ biên dạng mặt cắt cánh Airfoil 2D (biên trên, biên dưới, đường camber).
    
    Parameters
    ----------
    naca_code : str
        Mã NACA 4 chữ số
    save_path : Path | str | None
        Đường dẫn lưu ảnh (mặc định lưu vào results/figures/airfoil_profile.png, dpi>=300)
        
    TODO (Trương Thanh Vĩ):
    - Lấy tọa độ từ get_airfoil_coordinates.
    - Vẽ bằng Matplotlib với tỉ lệ trục bằng nhau (equal aspect ratio).
    - Lưu hình với dpi=300 theo yêu cầu.
    """
    # TODO (Trương Thanh Vĩ): Viết code vẽ biên dạng 2D ở đây
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm plot_airfoil_2d")


def plot_wing_3d_matplotlib(
    config: Dict[str, Any], 
    save_path: Path | str | None = None
) -> None:
    """
    Vẽ phối cảnh 3D cánh máy bay bằng Matplotlib (mặt trên và mặt dưới).
    
    Parameters
    ----------
    config : dict
        Tham số cấu hình từ params.yaml
    save_path : Path | str | None
        Đường dẫn lưu ảnh (vd: results/figures/wing_3d.png)
        
    TODO (Trương Thanh Vĩ):
    - Lấy lưới tọa độ từ wing_surface (cho cả upper và lower).
    - Dùng ax.plot_surface với colormap phù hợp (vd: 'viridis' hoặc 'plasma').
    - Cân chỉnh tỉ lệ trục (set_box_aspect) để hình không bị méo.
    """
    # TODO (Trương Thanh Vĩ): Viết code vẽ cánh 3D bằng Matplotlib ở đây
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm plot_wing_3d_matplotlib")


def plot_fuselage_3d_matplotlib(
    config: Dict[str, Any], 
    save_path: Path | str | None = None
) -> None:
    """
    Vẽ phối cảnh 3D thân máy bay bằng Matplotlib.
    
    TODO (Trương Thanh Vĩ):
    - Lấy tọa độ từ fuselage_surface_3d.
    - Dùng ax.plot_surface vẽ thân xoay tròn 3D.
    - Lưu hình vào results/figures/fuselage_3d.png.
    """
    # TODO (Trương Thanh Vĩ): Viết code vẽ thân 3D ở đây
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm plot_fuselage_3d_matplotlib")


def render_full_aircraft_plotly(
    config: Dict[str, Any], 
    output_html_path: Path | str | None = None
) -> None:
    """
    Ghép cánh và thân thành mô hình 3D tương tác hoàn chỉnh bằng thư viện Plotly.
    Người dùng có thể xoay, zoom và xem trực quan trên trình duyệt (file .html).
    
    Parameters
    ----------
    config : dict
        Tham số từ params.yaml
    output_html_path : Path | str | None
        Đường dẫn xuất file HTML (mặc định results/figures/aircraft_model.html)
        
    TODO (Trương Thanh Vĩ):
    - Tạo go.Figure() với các go.Surface cho thân máy bay, cánh trái, cánh phải.
    - Thiết lập camera, layout, màu sắc đồng nhất.
    - Ghi ra file HTML và xuất ảnh tĩnh nếu cài kaleido.
    """
    # TODO (Trương Thanh Vĩ): Viết code render mô hình tương tác 3D Plotly ở đây
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm render_full_aircraft_plotly")


# ==============================================================================
# PHẦN VIỆC CỦA HÀ NGỌC KHẢI (Biểu đồ khí động học 2D & Kết quả lực)
# ==============================================================================

def plot_cp_distribution(
    config: Dict[str, Any], 
    save_path: Path | str | None = None
) -> None:
    """
    Vẽ đồ thị phân bố hệ số áp suất -C_p dọc theo chiều dài dây cung x/c.
    Quy ước chuẩn khí động học: Trục tung -C_p thường đảo ngược (giá trị âm ở trên).
    
    Parameters
    ----------
    config : dict
        Tham số cấu hình
    save_path : Path | str | None
        Đường dẫn lưu ảnh (vd: results/figures/cp_distribution.png, dpi>=300)
        
    TODO (Hà Ngọc Khải):
    - Lấy phân bố Cp mặt trên và mặt dưới từ module aero.py.
    - Vẽ 2 đường cong: Mặt trên (Upper - nét liền), Mặt dưới (Lower - nét đứt).
    - Tô màu diện tích khép kín giữa 2 đường (thể hiện trực quan lực nâng tích phân).
    """
    # TODO (Hà Ngọc Khải): Viết code vẽ phân bố Cp ở đây
    raise NotImplementedError("Hà Ngọc Khải cần hoàn thiện hàm plot_cp_distribution")


def plot_lift_drag_polar(
    alpha_range_deg: np.ndarray, 
    lifts: np.ndarray, 
    drags: np.ndarray, 
    save_path: Path | str | None = None
) -> None:
    """
    Vẽ các đường đặc tính khí động học quan trọng:
    1. Đường cong hệ số lực nâng theo góc tới C_L vs alpha.
    2. Đường cong cực khí động C_L vs C_D (drag polar).
    3. Tỉ số L/D theo góc tới alpha để tìm góc tới tối ưu (max aerodynamic efficiency).
    
    Parameters
    ----------
    alpha_range_deg : np.ndarray
        Mảng các góc tới khảo sát (vd: từ 0 đến 12 độ)
    lifts, drags : np.ndarray
        Mảng lực nâng và lực cản tương ứng
    save_path : Path | str | None
        Đường dẫn lưu file ảnh
        
    TODO (Hà Ngọc Khải):
    - Vẽ đồ thị nhiều subplot (1 hàng 2 cột hoặc 1 hàng 3 cột).
    - Định dạng nhãn trục, chú thích (legend), lưới tọa độ (grid), font chuẩn cho báo cáo.
    - Lưu hình độ phân giải cao dpi>=300 vào results/figures/.
    """
    # TODO (Hà Ngọc Khải): Viết code vẽ đường đặc tính khí động học ở đây
    raise NotImplementedError("Hà Ngọc Khải cần hoàn thiện hàm plot_lift_drag_polar")

"""
Module airfoil.py: Mô hình hóa biên dạng cánh máy bay (Airfoil NACA 4 chữ số).
Người phụ trách chính: Trương Thanh Vĩ
Người review chéo: Hà Ngọc Khải
"""

import numpy as np
from typing import Tuple, Callable


# ==============================================================================
# PHẦN VIỆC CỦA TRƯƠNG THANH VĨ
# ==============================================================================

def parse_naca4(naca_code: str = "2412") -> Tuple[float, float, float]:
    """
    Phân tích mã NACA 4 chữ số thành các tham số hình học m, p, t.
    
    Parameters
    ----------
    naca_code : str
        Chuỗi mã NACA 4 chữ số (vd: "2412", "0012")
        
    Returns
    -------
    tuple (m, p, t)
        m: Độ cong tối đa (max camber) dưới dạng tỉ lệ (vd: 2 -> 0.02)
        p: Vị trí độ cong tối đa (max camber position) dạng tỉ lệ (vd: 4 -> 0.4)
        t: Độ dày tối đa (max thickness) dạng tỉ lệ dây cung (vd: 12 -> 0.12)
        
    TODO (Trương Thanh Vĩ):
    - Trích xuất chữ số đầu tiên: m = int(naca_code[0]) / 100.0
    - Trích xuất chữ số thứ hai: p = int(naca_code[1]) / 10.0
    - Trích xuất hai chữ số cuối: t = int(naca_code[2:4]) / 100.0
    """
    # TODO (Trương Thanh Vĩ): Viết code xử lý ở đây
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm parse_naca4")


def naca4_thickness(x: np.ndarray | float, t: float = 0.12) -> np.ndarray | float:
    """
    Tính phân bố nửa độ dày y_t(x) theo công thức giải tích chuẩn NACA 4 chữ số:
    y_t(x) = 5 * t * (0.2969*sqrt(x) - 0.1260*x - 0.3516*x^2 + 0.2843*x^3 - 0.1036*x^4)
    với x thuộc [0, 1].
    
    Parameters
    ----------
    x : np.ndarray hoặc float
        Tọa độ dọc dây cung chuẩn hóa, x trong đoạn [0, 1]
    t : float
        Độ dày tối đa (mặc định 0.12 tương ứng 12% chord)
        
    Returns
    -------
    np.ndarray hoặc float
        Nửa bề dày y_t tại các tọa độ x.
        
    TODO (Trương Thanh Vĩ):
    - Cài đặt công thức giải tích chuẩn NACA trên.
    - Đảm bảo x nằm trong khoảng [0, 1], xử lý giá trị âm nếu có bằng np.clip(x, 0, 1).
    - Lưu ý: Đánh dấu comment '# AI-assisted: xem AI_DECLARATION.md' nếu có tham khảo AI.
    """
    # TODO (Trương Thanh Vĩ): Viết code tính toán ở đây
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm naca4_thickness")


def naca4_camber(x: np.ndarray | float, m: float = 0.02, p: float = 0.4) -> Tuple[np.ndarray, np.ndarray]:
    """
    Tính đường cong camber y_c(x) và đạo hàm dy_c/dx theo công thức từng đoạn:
    - Khi 0 <= x < p:
        y_c(x) = (m / p^2) * (2*p*x - x^2)
        dy_c/dx = (2*m / p^2) * (p - x)
    - Khi p <= x <= 1:
        y_c(x) = (m / (1-p)^2) * ((1 - 2*p) + 2*p*x - x^2)
        dy_c/dx = (2*m / (1-p)^2) * (p - x)
        
    Parameters
    ----------
    x : np.ndarray hoặc float
        Tọa độ dọc dây cung chuẩn hóa [0, 1]
    m : float
        Max camber
    p : float
        Vị trí max camber
        
    Returns
    -------
    tuple (y_c, dyc_dx)
        y_c: Giá trị camber tại x
        dyc_dx: Đạo hàm camber theo x
        
    TODO (Trương Thanh Vĩ):
    - Xử lý trường hợp đối xứng (m == 0): y_c = 0, dyc_dx = 0.
    - Áp dụng np.where hoặc logic mảng để tính toán trên mảng numpy x.
    """
    # TODO (Trương Thanh Vĩ): Viết code tính camber và đạo hàm ở đây
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm naca4_camber")


def get_airfoil_coordinates(
    x: np.ndarray, 
    naca_code: str = "2412"
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Tính toán tọa độ mặt trên (upper) và mặt dưới (lower) của airfoil.
    
    Quy ước tọa độ chuẩn hóa:
    theta = arctan(dy_c / dx)
    x_U = x - y_t * sin(theta)
    y_U = y_c + y_t * cos(theta)
    x_L = x + y_t * sin(theta)
    y_L = y_c - y_t * cos(theta)
    
    (Hoặc xấp xỉ thiết diện mỏng: y_U = y_c + y_t, y_L = y_c - y_t)
    
    Parameters
    ----------
    x : np.ndarray
        Mảng tọa độ x chuẩn hóa từ 0 đến 1 (thường tập trung dày ở mép trước và mép sau, vd: chia theo cos).
    naca_code : str
        Mã naca (vd: "2412")
        
    Returns
    -------
    tuple (x_upper, y_upper, x_lower, y_lower)
        Tọa độ mặt trên và mặt dưới của profile cánh.
        
    TODO (Trương Thanh Vĩ):
    - Gọi parse_naca4, naca4_thickness, naca4_camber.
    - Tính toán góc theta và tọa độ x_U, y_U, x_L, y_L.
    """
    # TODO (Trương Thanh Vĩ): Viết code tính tọa độ mặt trên/dưới ở đây
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm get_airfoil_coordinates")


# ==============================================================================
# ĐIỂM GIAO TIẾP VỚI HÀ NGỌC KHẢI:
# Khải sẽ import các hàm độ dày, camber và biên mặt trên/dưới để dựng hình học cánh và tính áp suất.
# ==============================================================================

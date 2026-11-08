"""
Module wing.py: Mô hình hóa hình học cánh 3D và tính toán diện tích bằng tích phân kép.
Người phụ trách chính: Trương Thanh Vĩ
Người review chéo: Hà Ngọc Khải
"""

import numpy as np
from scipy import integrate
from typing import Tuple, Dict, Any, Callable

# Import từ module airfoil
from src.airfoil import naca4_thickness, naca4_camber, parse_naca4


# ==============================================================================
# PHẦN VIỆC CỦA TRƯƠNG THANH VĨ
# ==============================================================================

def chord_distribution(y: np.ndarray | float, b: float, c_root: float, c_tip: float) -> np.ndarray | float:
    """
    Quy luật biến thiên của dây cung cánh theo sải cánh y:
    c(y) = c_root - (c_root - c_tip) * (|y| / (b / 2))
    với y thuộc [-b/2, b/2].
    
    Parameters
    ----------
    y : np.ndarray | float
        Tọa độ vị trí theo sải cánh [m]
    b : float
        Tổng sải cánh (span) [m]
    c_root : float
        Độ dài dây cung ở gốc cánh (root chord) [m]
    c_tip : float
        Độ dài dây cung ở đầu mút cánh (tip chord) [m]
        
    Returns
    -------
    np.ndarray | float
        Độ dài dây cung c(y) tại vị trí y [m]
        
    TODO (Trương Thanh Vĩ):
    - Cài đặt công thức dây cung cánh hình thang.
    """
    # TODO (Trương Thanh Vĩ): Viết code ở đây
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm chord_distribution")


def wing_surface(
    u: np.ndarray, 
    v: np.ndarray, 
    b: float, 
    c_root: float, 
    c_tip: float, 
    naca_code: str = "2412",
    surface_type: str = "upper"
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Tham số hóa bề mặt cánh máy bay 3D r(u, v) = (x(u, v), y(u, v), z(u, v)).
    - u in [0, 1]: tham số chuẩn hóa dọc dây cung (mép trước -> mép sau)
    - v in [-b/2, b/2]: tham số dọc sải cánh
    
    x(u, v) = u * c(v)  (hoặc dịch gốc theo góc quét/sweep)
    y(u, v) = v
    z(u, v) = z_airfoil(u) * c(v)  (z_airfoil lấy từ camber +/- thickness)
    
    Parameters
    ----------
    u, v : np.ndarray
        Lưới tham số 2D (tạo bởi np.meshgrid)
    surface_type : str
        'upper' (mặt trên) hoặc 'lower' (mặt dưới)
        
    Returns
    -------
    tuple (X, Y, Z)
        Tọa độ các điểm trên mặt cánh trong không gian 3D [m].
        
    TODO (Trương Thanh Vĩ):
    - Rất quan trọng: Thống nhất định dạng đầu ra với Hà Ngọc Khải vì Khải sẽ dùng X, Y, Z
      để tính vector pháp tuyến và tích phân mặt trong aero.py!
    """
    # TODO (Trương Thanh Vĩ): Hoàn thiện hàm wing_surface
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm wing_surface")


def calculate_projected_area(
    b: float, 
    c_root: float, 
    c_tip: float, 
    method: str = "analytical"
) -> float:
    """
    Tính diện tích hình chiếu của cánh S = int c(y) dy.
    
    Hai phương pháp đối chiếu:
    1. 'analytical': S = (c_root + c_tip) / 2 * b (công thức hình thang)
    2. 'numerical': Tích phân kép bằng scipy.integrate.dblquad hoặc scipy.integrate.trapezoid
    
    Parameters
    ----------
    b : float
        Sải cánh [m]
    c_root, c_tip : float
        Dây cung gốc và đầu cánh [m]
    method : str
        'analytical' hoặc 'numerical'
        
    Returns
    -------
    float
        Diện tích hình chiếu S [m^2]
        
    TODO (Trương Thanh Vĩ):
    - Cài đặt cả 2 phương pháp giải tích và số trị để kiểm chứng chéo.
    """
    # TODO (Trương Thanh Vĩ): Viết code tính diện tích hình chiếu ở đây
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm calculate_projected_area")


def calculate_surface_area(
    b: float, 
    c_root: float, 
    c_tip: float, 
    naca_code: str = "2412",
    n_u: int = 200,
    n_v: int = 100
) -> Dict[str, float]:
    """
    Tính diện tích bề mặt thực tế của cánh (mặt trên + mặt dưới) bằng tích phân kép:
    A = iint ||r_u x r_v|| du dv
    
    Parameters
    ----------
    b, c_root, c_tip : float
        Kích thước cánh [m]
    naca_code : str
        Mã NACA
    n_u, n_v : int
        Số điểm chia lưới tham số u và v
        
    Returns
    -------
    dict
        {'area_upper': float, 'area_lower': float, 'total_surface_area': float} [m^2]
        
    TODO (Trương Thanh Vĩ):
    - Tính đạo hàm riêng r_u, r_v của mặt cong (hoặc xấp xỉ đạo hàm bằng sai phân hữu hạn np.gradient).
    - Tính tích có hướng (cross product) r_u x r_v và độ dài chuẩn ||r_u x r_v||.
    - Áp dụng tích phân kép số (scipy.integrate.trapezoid hoặc dblquad).
    """
    # TODO (Trương Thanh Vĩ): Hoàn thiện hàm calculate_surface_area
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm calculate_surface_area")

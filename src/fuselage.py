"""
Module fuselage.py: Mô hình hóa hình học thân máy bay, tính thể tích và khối lượng bằng tích phân bội ba.
Người phụ trách chính: Trương Thanh Vĩ
Người review chéo: Hà Ngọc Khải
"""

import numpy as np
from scipy import integrate
from typing import Tuple, Dict, Callable


# ==============================================================================
# PHẦN VIỆC CỦA TRƯƠNG THANH VĨ
# ==============================================================================

def fuselage_radius(x: np.ndarray | float, length: float, radius_max: float) -> np.ndarray | float:
    """
    Hàm bán kính thân r(x) theo trục dọc x in [0, length]:
    Chia làm 3 đoạn hình học:
    1. Phần mũi (Nose): elipsoid hoặc ogive (0 <= x < 0.2 * length)
    2. Phần thân giữa (Mid-body): hình trụ thẳng bán kính R_max (0.2 * length <= x < 0.7 * length)
    3. Phần đuôi (Tail): hình nón cụt thu nhỏ về mép sau (0.7 * length <= x <= length)
    
    Parameters
    ----------
    x : np.ndarray | float
        Tọa độ dọc thân x [m]
    length : float
        Chiều dài tổng thể thân máy bay L [m]
    radius_max : float
        Bán kính tối đa của thân R_max [m]
        
    Returns
    -------
    np.ndarray | float
        Bán kính r(x) tại vị trí x [m]
        
    TODO (Trương Thanh Vĩ):
    - Định nghĩa hàm từng đoạn trơn tru (smooth piecewise function).
    - Đảm bảo r(0) = 0 (đầu mũi) và bán kính ở đuôi hợp lý.
    """
    # TODO (Trương Thanh Vĩ): Cài đặt hàm bán kính thân ở đây
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm fuselage_radius")


def fuselage_surface_3d(
    length: float, 
    radius_max: float, 
    n_x: int = 100, 
    n_theta: int = 60
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Tham số hóa bề mặt ngoài của thân máy bay trong không gian 3D:
    x in [0, length]
    theta in [0, 2*pi]
    y(x, theta) = r(x) * cos(theta)
    z(x, theta) = r(x) * sin(theta)
    
    Parameters
    ----------
    length : float
        Chiều dài thân [m]
    radius_max : float
        Bán kính lớn nhất [m]
    n_x, n_theta : int
        Số điểm lưới
        
    Returns
    -------
    tuple (X, Y, Z)
        Lưới 3D tọa độ mặt thân máy bay phục vụ render 3D
        
    TODO (Trương Thanh Vĩ):
    - Tạo lưới (X, Theta) qua np.meshgrid.
    - Tính Y, Z từ bán kính r(X) và góc Theta.
    """
    # TODO (Trương Thanh Vĩ): Cài đặt hàm tọa độ 3D mặt thân ở đây
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm fuselage_surface_3d")


def calculate_fuselage_volume(
    length: float, 
    radius_max: float, 
    skin_thickness: float = 0.0,
    method: str = "single_integral"
) -> Dict[str, float]:
    """
    Tính thể tích thân máy bay bằng tích phân:
    Trong tọa độ trụ (r, theta, x):
    V = iiint r dr dtheta dx = int_0^L pi * r(x)^2 dx
    
    Nếu tính vỏ rỗng mỏng (skin_thickness > 0):
    V_skin = int_0^L pi * [r(x)^2 - (r(x) - t_skin)^2] dx
    
    Parameters
    ----------
    length : float
        Chiều dài thân [m]
    radius_max : float
        Bán kính tối đa [m]
    skin_thickness : float
        Độ dày vỏ thân máy bay [m]
    method : str
        'single_integral' (tích phân 1 lớp int pi*r^2 dx) hoặc 'triple_integral' (scipy.integrate.tplquad)
        
    Returns
    -------
    dict
        {'volume_solid': float, 'volume_skin': float} [m^3]
        
    TODO (Trương Thanh Vĩ):
    - Cài đặt phương pháp tích phân đơn (1D) với scipy.integrate.quad hoặc trapezoid.
    - Cài đặt phương pháp tích phân bội ba (scipy.integrate.tplquad) để đối chiếu kiểm chứng chéo.
    """
    # TODO (Trương Thanh Vĩ): Cài đặt tính thể tích ở đây
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm calculate_fuselage_volume")


def calculate_fuselage_mass(
    length: float, 
    radius_max: float, 
    density: float, 
    skin_thickness: float = 0.003,
    is_hollow: bool = True
) -> float:
    """
    Tính khối lượng thân máy bay:
    m = iiint_V rho dV
    
    Parameters
    ----------
    length : float
        Chiều dài thân [m]
    radius_max : float
        Bán kính thân [m]
    density : float
        Khối lượng riêng vật liệu (vd: nhôm rho = 2700 kg/m^3)
    skin_thickness : float
        Độ dày vỏ [m]
    is_hollow : bool
        True: tính theo vỏ rỗng (thực tế); False: thân đặc
        
    Returns
    -------
    float
        Khối lượng m [kg]
        
    TODO (Trương Thanh Vĩ):
    - Tính thể tích từ hàm calculate_fuselage_volume.
    - Nhân với khối lượng riêng density.
    - Hỗ trợ mở rộng nếu mật độ rho(x) biến thiên dọc thân máy bay.
    """
    # TODO (Trương Thanh Vĩ): Cài đặt tính khối lượng ở đây
    raise NotImplementedError("Trương Thanh Vĩ cần hoàn thiện hàm calculate_fuselage_mass")

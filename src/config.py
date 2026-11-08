"""
config.py - Đọc, kiểm tra và cung cấp tham số từ params.yaml.

Cách dùng:
    from src.config import load_params
    p = load_params()                 # đọc params.yaml ở thư mục gốc repo
    p.flow.rho, p.wing.span           # truy cập từng tham số
    p.q_inf, p.alpha_rad              # đại lượng suy ra

Quy ước: SI (m, kg, s, N, Pa); góc trong file là ĐỘ, thuộc tính *_rad là radian.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

import yaml

# --------------------------------------------------------------------------
# Đường dẫn dự án
# --------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PARAMS_PATH = PROJECT_ROOT / "params.yaml"
RESULTS_DIR = PROJECT_ROOT / "results"
TABLES_DIR = RESULTS_DIR / "tables"
FIGURES_DIR = RESULTS_DIR / "figures"


def ensure_output_dirs() -> None:
    """Tạo thư mục results/tables và results/figures nếu chưa có."""
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------
# Các nhóm tham số
# --------------------------------------------------------------------------
@dataclass
class AirfoilParams:
    naca: str = "2412"

    @property
    def naca_digits(self) -> tuple[float, float, float]:
        """(m, p, t) của NACA 4 chữ số, đã chuẩn hóa theo dây cung."""
        m = int(self.naca[0]) / 100.0
        p = int(self.naca[1]) / 10.0
        t = int(self.naca[2:]) / 100.0
        return m, p, t


@dataclass
class WingParams:
    span: float = 10.0
    chord_root: float = 1.8
    chord_tip: float = 0.9
    n_chord: int = 200
    n_span: int = 100

    @property
    def semi_span(self) -> float:
        return self.span / 2.0


@dataclass
class FuselageParams:
    length: float = 8.0
    radius_max: float = 0.7
    nose_length: float = 1.5
    tail_length: float = 2.5
    skin_thickness: float = 0.003
    density: float = 2700.0


@dataclass
class FlowParams:
    rho: float = 1.225
    V_inf: float = 60.0
    alpha_deg: float = 4.0
    mu: float = 1.81e-5


@dataclass
class AeroParams:
    alpha_L0_deg: float = -2.0
    span_loading: str = "elliptic"
    finite_wing_correction: bool = True
    oswald_e: float = 0.9
    leading_edge_suction: bool = True
    include_induced_drag: bool = True
    boundary_layer: str = "auto"
    transition_re: float = 5.0e5
    n_theta: int = 96
    n_span: int = 64


@dataclass
class Params:
    airfoil: AirfoilParams = field(default_factory=AirfoilParams)
    wing: WingParams = field(default_factory=WingParams)
    fuselage: FuselageParams = field(default_factory=FuselageParams)
    flow: FlowParams = field(default_factory=FlowParams)
    aero: AeroParams = field(default_factory=AeroParams)

    # ---- đại lượng suy ra -------------------------------------------------
    @property
    def alpha_rad(self) -> float:
        return math.radians(self.flow.alpha_deg)

    @property
    def alpha_L0_rad(self) -> float:
        return math.radians(self.aero.alpha_L0_deg)

    @property
    def q_inf(self) -> float:
        """Áp suất động q = 1/2 * rho * V^2 [Pa]."""
        return 0.5 * self.flow.rho * self.flow.V_inf ** 2

    @property
    def mean_chord(self) -> float:
        return 0.5 * (self.wing.chord_root + self.wing.chord_tip)

    def reynolds(self, chord: float) -> float:
        """Số Reynolds theo dây cung: Re = rho * V * c / mu."""
        return self.flow.rho * self.flow.V_inf * chord / self.flow.mu


# --------------------------------------------------------------------------
# Đọc + kiểm tra
# --------------------------------------------------------------------------
def _build(cls, data: dict[str, Any] | None, section: str):
    """Tạo dataclass từ dict, ép kiểu theo giá trị mặc định, báo lỗi khi sai tên khóa."""
    data = data or {}
    if not isinstance(data, dict):
        raise ValueError(f"[params.yaml] mục '{section}' phải là một nhóm khóa: giá trị.")
    defaults = cls()
    valid = {f.name for f in fields(cls)}
    unknown = set(data) - valid
    if unknown:
        raise ValueError(
            f"[params.yaml] mục '{section}' có khóa không hợp lệ: {sorted(unknown)}. "
            f"Các khóa hợp lệ: {sorted(valid)}"
        )
    kwargs = {}
    for key, value in data.items():
        expected = type(getattr(defaults, key))
        try:
            if expected is bool:
                if not isinstance(value, bool):
                    raise TypeError("cần true/false")
                kwargs[key] = value
            elif expected in (int, float):
                kwargs[key] = expected(value)   # '1.81e-5' dạng chuỗi cũng được
            else:
                kwargs[key] = str(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"[params.yaml] {section}.{key} = {value!r} không hợp lệ ({exc})."
            ) from exc
    return cls(**kwargs)


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(f"[params.yaml] {msg}")


def validate(p: Params) -> None:
    """Kiểm tra giá trị hợp lý; ném ValueError kèm thông báo rõ ràng."""
    a = p.airfoil
    _require(len(a.naca) == 4 and a.naca.isdigit(), "airfoil.naca phải gồm đúng 4 chữ số, ví dụ \"2412\".")
    _, _, t = a.naca_digits
    _require(t > 0, "airfoil.naca: độ dày t phải > 0.")

    w = p.wing
    _require(w.span > 0, "wing.span phải > 0.")
    _require(w.chord_root > 0 and w.chord_tip > 0, "wing.chord_root và wing.chord_tip phải > 0.")
    _require(w.chord_tip <= w.chord_root, "wing.chord_tip không được lớn hơn chord_root.")
    _require(w.n_chord >= 10 and w.n_span >= 10, "wing.n_chord và wing.n_span nên >= 10.")

    f = p.fuselage
    _require(f.length > 0 and f.radius_max > 0, "fuselage.length và radius_max phải > 0.")
    _require(f.nose_length >= 0 and f.tail_length >= 0, "fuselage.nose_length/tail_length phải >= 0.")
    _require(f.nose_length + f.tail_length <= f.length,
             "fuselage: nose_length + tail_length không được vượt quá length.")
    _require(0 < f.skin_thickness < f.radius_max, "fuselage.skin_thickness phải trong (0, radius_max).")
    _require(f.density > 0, "fuselage.density phải > 0.")

    fl = p.flow
    _require(fl.rho > 0 and fl.V_inf > 0 and fl.mu > 0, "flow.rho, V_inf, mu phải > 0.")
    _require(-20 <= fl.alpha_deg <= 20, "flow.alpha_deg nên trong [-20, 20] độ (mô hình tuyến tính).")

    ae = p.aero
    _require(ae.span_loading in ("elliptic", "uniform"), "aero.span_loading phải là elliptic hoặc uniform.")
    _require(ae.boundary_layer in ("laminar", "turbulent", "auto"),
             "aero.boundary_layer phải là laminar, turbulent hoặc auto.")
    _require(0 < ae.oswald_e <= 1.0, "aero.oswald_e phải trong (0, 1].")
    _require(ae.n_theta >= 8 and ae.n_span >= 8, "aero.n_theta và aero.n_span nên >= 8.")


def load_params(path: str | Path | None = None) -> Params:
    """Đọc params.yaml (mặc định ở thư mục gốc repo) và trả về Params đã kiểm tra."""
    path = Path(path) if path else DEFAULT_PARAMS_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy {path}. Hãy chạy từ thư mục gốc repo hoặc truyền đường dẫn đúng."
        )
    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    unknown = set(raw) - {"airfoil", "wing", "fuselage", "flow", "aero"}
    if unknown:
        raise ValueError(f"[params.yaml] có mục không hợp lệ: {sorted(unknown)}")

    params = Params(
        airfoil=_build(AirfoilParams, raw.get("airfoil"), "airfoil"),
        wing=_build(WingParams, raw.get("wing"), "wing"),
        fuselage=_build(FuselageParams, raw.get("fuselage"), "fuselage"),
        flow=_build(FlowParams, raw.get("flow"), "flow"),
        aero=_build(AeroParams, raw.get("aero"), "aero"),
    )
    validate(params)
    return params


if __name__ == "__main__":
    p = load_params()
    print("Đọc params.yaml thành công.")
    print(f"  q_inf     = {p.q_inf:.2f} Pa")
    print(f"  alpha     = {p.flow.alpha_deg:.2f} deg = {p.alpha_rad:.4f} rad")
    print(f"  Re(root)  = {p.reynolds(p.wing.chord_root):.3e}")
    print(f"  NACA {p.airfoil.naca}: m, p, t = {p.airfoil.naca_digits}")
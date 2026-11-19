"""Lớp tương thích cho đồ thị khí động (giữ tên hàm cũ cho dashboard/notebook).

Trước đây file này vẽ Cp và cực khí động thay cho hai hàm khung của Khải trong
visualize.py. Nay hai hàm đó đã được Khải hoàn thiện, nên các hàm dưới đây chỉ
gọi lại visualize.py để chỉ còn một cài đặt duy nhất.
# AI-assisted: xem AI_DECLARATION.md
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .config import Params
from .visualize import plot_cp_distribution, plot_lift_drag_polar, sweep_alpha
from .wing import WingModel


def plot_cp_report(p: Params, wing: WingModel, path: Path) -> None:
    """Lưu Cp hai mặt tại y = b/4 (gọi visualize.plot_cp_distribution)."""
    plot_cp_distribution(p, path, wing=wing)


def plot_polar_report(p: Params, wing: WingModel, path: Path) -> None:
    """Lưu đặc tuyến L(α), cực khí động và L/D (gọi visualize.plot_lift_drag_polar)."""
    r = sweep_alpha(p, np.linspace(-2, 12, 15), wing)
    S = (p.wing.chord_root + p.wing.chord_tip) * p.wing.span / 2
    plot_lift_drag_polar(r["alpha"], r["L"], r["D"], path, q_S=p.q_inf * S)

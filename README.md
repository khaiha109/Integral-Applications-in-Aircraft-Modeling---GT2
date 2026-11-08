# Ứng dụng tích phân trong máy bay

> Bài tập lớn môn **Giải tích 3** — Phần 1: CODE & Mô hình hóa 3D
> Mô hình hóa cánh và thân máy bay; dùng tích phân kép, tích phân bội ba để tính diện tích, thể tích, khối lượng; dùng tích phân mặt để ước lượng lực nâng và lực cản; trực quan hóa bằng mô hình 3D.

| Mục | Thông tin |
|---|---|
| Người thực hiện | Trương Thanh Vĩ, Hà Ngọc Khải |
| Review | Nhóm trưởng |
| Deadline | 14/11/2026 |
| Ngôn ngữ / công cụ | Python 3.10+, NumPy, SciPy, Matplotlib, Plotly |

> **Lưu ý:** đây là mô hình hóa theo giả thiết của bài tập, **không phải** mô phỏng khí động học đầy đủ (CFD). Lực nâng/lực cản chỉ có ý nghĩa khi nêu rõ phân bố áp suất, vận tốc dòng khí, mật độ không khí và các giả thiết đi kèm.

---

## 1. Yêu cầu hệ thống

- Python **3.10 trở lên** (kiểm tra: `python --version`)
- Git (kiểm tra: `git --version`)
- Khuyến nghị: VS Code + extension Python / Jupyter

---

## 2. Cài đặt môi trường ảo

### 2.1. Clone repo

Chọn <Code> -> open with Github Desktop (khuyến khích nên tải Github Desktop)/Download Zip (này nào làm xong gửi Khải để Khải push lên)


```bash
git clone https://github.com/<username>/<ten-repo>.git
cd <ten-repo>
```

### 2.2. Tạo và kích hoạt môi trường ảo (venv)

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> Nếu PowerShell báo lỗi chặn script, chạy một lần:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
> Hoặc dùng CMD: `.venv\Scripts\activate.bat`

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Kích hoạt thành công khi dòng lệnh có tiền tố `(.venv)`.

### 2.3. Cài thư viện

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` (tối thiểu):

```
numpy
scipy
matplotlib
plotly
pyyaml
pandas
jupyter
kaleido        # xuất ảnh tĩnh từ plotly
```

### 2.4. Kiểm tra cài đặt

```bash
python -c "import numpy, scipy, matplotlib, plotly, yaml; print('OK')"
```

### 2.5. (Tùy chọn) Dùng Conda thay cho venv

```bash
conda create -n aircraft python=3.11 -y
conda activate aircraft
pip install -r requirements.txt
```

### 2.6. Thoát môi trường ảo

```bash
deactivate        # venv
conda deactivate  # conda
```

> Mỗi khi thêm thư viện mới: `pip install <tên>` rồi cập nhật `requirements.txt` (`pip freeze > requirements.txt`) và báo cho nhóm.

---

## 3. Cấu trúc thư mục dự kiến

```
.
├── README.md
├── requirements.txt
├── .gitignore
├── params.yaml                 # tham số đầu vào + đơn vị (SI)
├── AI_DECLARATION.md           # khai báo phần code do AI tạo/sửa
├── prompt_log/                 # nhật ký prompt (mỗi file một ngày/phiên)
│   └── 2026-11-09_ten-chu-de.md
├── src/
│   ├── __init__.py
│   ├── config.py               # đọc params.yaml, hằng số, đổi đơn vị
│   ├── airfoil.py              # NACA 4 chữ số: độ dày, camber, biên trên/dưới
│   ├── wing.py                 # hình học cánh 3D, diện tích (tích phân kép)
│   ├── fuselage.py             # thân máy bay, thể tích/khối lượng (tích phân bội ba)
│   ├── aero.py                 # áp suất, pháp tuyến, lực nâng/cản (tích phân mặt)
│   ├── validate.py             # kiểm chứng: số vs giải tích, trường hợp đơn giản
│   └── visualize.py            # render 3D, đồ thị, xuất hình
├── notebooks/
│   └── demo.ipynb              # chạy lại toàn bộ từ đầu
├── tests/
│   └── test_basic.py           # test nhanh các trường hợp có đáp án biết trước
├── results/
│   ├── tables/                 # bảng kết quả (csv/md)
│   └── figures/                # hình xuất cho báo cáo/slide (png, dpi >= 300)
├── docs/
│   └── assumptions.md          # giả thiết, công thức, quy ước tọa độ
└── main.py                     # chạy toàn bộ pipeline, lưu kết quả vào results/
```

### Phân công module

| Module | Phụ trách chính | Review chéo |
|---|---|---|
| `config.py`, `params.yaml` | cả hai (thống nhất trước) | Nhóm trưởng |
| `airfoil.py`, `wing.py`, `fuselage.py` | Trương Thanh Vĩ | Hà Ngọc Khải |
| `aero.py` | Hà Ngọc Khải | Trương Thanh Vĩ |
| `validate.py` | Hà Ngọc Khải (phần lực), Trương Thanh Vĩ (phần diện tích/thể tích) | Nhóm trưởng |
| `visualize.py` (hình 3D) | Trương Thanh Vĩ | Hà Ngọc Khải |
| `visualize.py` (biểu đồ, bảng kết quả lực nâng/lực cản) | Hà Ngọc Khải | Trương Thanh Vĩ |
| `main.py` | cả hai | Nhóm trưởng |
| `AI_DECLARATION.md`, `prompt_log/` | Hà Ngọc Khải ghi chép | Nhóm trưởng |

> Để hai người cùng sửa `visualize.py` không xung đột, nên tách thành `visualize_3d.py` (Vĩ) và `plots_results.py` (Khải), hoặc làm trên hai nhánh riêng và merge qua Pull Request.

---|---|---|
| `config.py`, `params.yaml` | cả hai (thống nhất trước) | Nhóm trưởng |
| `airfoil.py`, `wing.py`, `fuselage.py` | Trương Thanh Vĩ | Hà Ngọc Khải |
| `aero.py`, `validate.py` | Hà Ngọc Khải | Trương Thanh Vĩ |
| `visualize.py`, `main.py` | cả hai | Nhóm trưởng |

---

## 3b. Phân công công việc

| Mục công việc | Người phụ trách |
|---|---|
| Mô hình hóa hình dạng cánh máy bay (airfoil profile) bằng hàm toán học | Trương Thanh Vĩ |
| Mô hình hóa hình dạng thân máy bay | Trương Thanh Vĩ |
| Dùng tích phân kép tính diện tích bề mặt cánh | Trương Thanh Vĩ |
| Dùng tích phân bội ba tính thể tích và khối lượng thân máy bay | Trương Thanh Vĩ |
| Dùng tích phân mặt tính lực nâng và lực cản khí động | Hà Ngọc Khải |
| Trực quan hóa 3D và render mô hình | Trương Thanh Vĩ |
| Xuất hình ảnh/đồ thị cho báo cáo và slide | Trương Thanh Vĩ: xuất hình 3D; Hà Ngọc Khải: biểu đồ, bảng kết quả lực nâng/lực cản |
| Review / khai báo code do AI tạo và lưu prompt log | Hà Ngọc Khải ghi chép; cả hai đánh dấu phần AI hỗ trợ trong code của mình |

**Điểm giao nhau giữa hai người** (cần thống nhất sớm):
- Khải dùng hình học cánh (hàm `wing_surface(u, v)`, pháp tuyến) do Vĩ viết để tính tích phân mặt, nên Vĩ cần chốt giao diện hàm này trước (đầu vào, đầu ra, đơn vị).
- Vĩ cần diện tích hình chiếu $S$ của cánh để Khải kiểm chứng $L \approx \tfrac12\rho V^2 S C_L$.
- Hình 3D (Vĩ) và biểu đồ lực (Khải) dùng chung bảng màu, cỡ chữ, kích thước hình để đồng nhất trong báo cáo và slide.

---

## 4. Quy ước chung (chốt trước khi code)

- **Hệ tọa độ:** x dọc thân (mũi → đuôi), y theo sải cánh, z hướng lên.
- **Đơn vị:** SI (m, kg, s, N, Pa). Góc tới α nhập bằng độ trong `params.yaml`, đổi sang radian trong code.
- **Tham số dùng chung** đặt trong `params.yaml`, **không** hard-code trong các module.
- Mỗi hàm có docstring ghi rõ đầu vào, đầu ra, đơn vị.
- Mỗi đại lượng tích phân được tính **hai cách** để đối chiếu (ví dụ `scipy.integrate.dblquad` và `scipy.integrate.trapezoid` / công thức giải tích).

Ví dụ `params.yaml`:

```yaml
airfoil:
  naca: "2412"          # m=2%, p=0.4, t=12%
wing:
  span: 10.0            # b [m]
  chord_root: 1.8       # [m]
  chord_tip: 0.9        # [m]
  n_chord: 200
  n_span: 100
fuselage:
  length: 8.0           # [m]
  radius_max: 0.7       # [m]
  skin_thickness: 0.003 # [m]
  density: 2700         # [kg/m^3], nhôm
flow:
  rho: 1.225            # [kg/m^3]
  V_inf: 60.0           # [m/s]
  alpha_deg: 4.0        # [độ]
  mu: 1.81e-5           # [Pa.s]
```

---

## 5. Hướng code (thứ tự thực hiện)

### Bước 1 — Airfoil (`airfoil.py`)

- Độ dày NACA 4 chữ số:
  $y_t(x) = 5t\,(0.2969\sqrt{x} - 0.1260x - 0.3516x^2 + 0.2843x^3 - 0.1036x^4)$, với $x\in[0,1]$.
- Đường camber $y_c(x)$ theo m, p; biên trên/dưới = $y_c \pm y_t$.
- Đầu ra: hàm `upper(x)`, `lower(x)`, `thickness(x)`.

### Bước 2 — Cánh 3D và diện tích (`wing.py`)

- Dây cung thay đổi theo sải: $c(y) = c_{root} - (c_{root}-c_{tip})\,\dfrac{|y|}{b/2}$.
- Tham số hóa mặt: $\mathbf r(u,v) = (u\,c(v),\; v,\; \pm z(u)\,c(v))$, $u\in[0,1]$, $v\in[0,b/2]$.
- **Tích phân kép:**
  - Diện tích hình chiếu: $S = \iint dx\,dy = \int c(y)\,dy$.
  - Diện tích bề mặt: $A = \iint \lVert \mathbf r_u \times \mathbf r_v \rVert \, du\,dv$ (cả mặt trên và dưới).
- Đối chiếu: cánh chữ nhật $S = c\cdot b$; cánh thon có công thức giải tích.

### Bước 3 — Thân máy bay (`fuselage.py`)

- Bán kính theo trục $r(x)$: mũi (ogive/elip) + đoạn trụ + đuôi thu nhỏ (hàm từng đoạn).
- **Tích phân bội ba** (tọa độ trụ): $V = \iiint r\,dr\,d\theta\,dx = \int \pi r(x)^2\,dx$.
- Khối lượng: $m = \iiint_V \rho\,dV$.
  - Phương án 1: đặc, $\rho$ hằng.
  - Phương án 2 (thực tế hơn): vỏ rỗng dày $t_{skin}$, tính bằng hiệu hai thể tích.
  - Phương án 3 (nâng cao): $\rho(x)$ thay đổi dọc thân.
- Đối chiếu: trụ → $\pi r^2 L$; elipsoid → $\tfrac43\pi abc$; so `scipy.integrate.tplquad`.

### Bước 4 — Lực khí động (`aero.py`)

- Lực tổng: $\mathbf F = -\iint p\,\mathbf n\,dS + \iint \boldsymbol\tau\,dS$, trong đó $\mathbf n$ là pháp tuyến ngoài từ $\mathbf r_u\times\mathbf r_v$.
- Áp suất: $p = p_\infty + \tfrac12\rho V_\infty^2\,C_p(x,\alpha)$, dùng mô hình $C_p$ đơn giản (nêu rõ giả thiết).
- Hướng dòng tự do: $\hat{\mathbf e}_\infty = (\cos\alpha,\,0,\,\sin\alpha)$.
  - **Lực cản** $D = \mathbf F\cdot\hat{\mathbf e}_\infty$ (song song dòng).
  - **Lực nâng** $L$ = thành phần của $\mathbf F$ vuông góc dòng (trong mặt phẳng x–z).
- Lực cản do áp suất thuần túy (không nhớt) ≈ 0 (nghịch lý d'Alembert), nên cộng thêm **ma sát bề mặt**: $\tau = \tfrac12\rho V^2 C_f$, $C_f = 1.328/\sqrt{Re}$ (Blasius, lớp biên tầng).
- Đối chiếu: $L \approx \tfrac12\rho V^2 S\,C_L$ với $C_L\approx 2\pi\alpha$ (lý thuyết thiết diện mỏng).

### Bước 5 — Kiểm chứng (`validate.py`)

- So sánh tích phân số và công thức giải tích, in sai số tương đối.
- Kiểm tra hội tụ theo độ mịn lưới (`n_chord`, `n_span`).
- Kiểm tra đơn vị và bậc độ lớn (ví dụ lực nâng của máy bay nhỏ cỡ $10^3$–$10^4$ N).

### Bước 6 — Trực quan hóa (`visualize.py`)

- Matplotlib: biên dạng airfoil, cánh 3D, thân 3D, phân bố $C_p$ trên cánh.
- Plotly: mô hình 3D tương tác (cánh + thân ghép lại), xuất HTML.
- Lưu hình vào `results/figures/` với `dpi=300`, tên file có nghĩa (`wing_3d.png`, `cp_distribution.png`, ...).

### Bước 7 — Ghép và chạy (`main.py`)

```bash
python main.py
```

Chương trình đọc `params.yaml`, tính toàn bộ, in bảng kết quả và lưu vào `results/tables/`, `results/figures/`.

---

## 6. Kết quả đầu ra (bàn giao)

1. Mã nguồn / notebook chạy lại được từ đầu.
2. `params.yaml` chứa tham số đầu vào và đơn vị.
3. Bảng kết quả: diện tích, thể tích, khối lượng, lực nâng, lực cản (`results/tables/`).
4. Hình 3D và đồ thị cho báo cáo/slide (`results/figures/`).
5. `AI_DECLARATION.md` + `prompt_log/`.

---

## 7. Quy trình làm việc với Git

- **Không** đẩy trực tiếp vào `main`. Mỗi đầu việc làm trên một nhánh riêng:

```bash
git checkout main
git pull
git checkout -b feature/<ten-viec>      # ví dụ: feature/wing-area
# ... code ...
git add .
git commit -m "Add wing surface area double integral"
git push -u origin feature/<ten-viec>
```

- Mở **Pull Request** vào `main`, gán **Nhóm trưởng** làm reviewer; chỉ merge khi đã được duyệt.
- Commit message ngắn gọn, bắt đầu bằng động từ (Add / Fix / Update / Refactor).
- **Không commit:** `.venv/`, `__pycache__/`, file tạm, dữ liệu lớn. Đảm bảo `.gitignore` có các dòng:

```
.venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
.DS_Store
```

---

## 8. Khai báo AI (bắt buộc)

Theo yêu cầu đề bài, mọi phần code do AI tạo/sửa phải được ghi rõ. **Hà Ngọc Khải** phụ trách ghi chép và tổng hợp `AI_DECLARATION.md` + `prompt_log/`; **cả hai** tự đánh dấu (comment `# AI-assisted`) phần AI hỗ trợ trong code của mình và gửi prompt cho Khải.

**`AI_DECLARATION.md`** dùng bảng sau:

| File | Hàm / đoạn | AI tạo hay sửa | Công cụ AI | Prompt log | Người rà soát |
|---|---|---|---|---|---|
| `src/airfoil.py` | `naca4_thickness` | Tạo | (tên công cụ) | `prompt_log/2026-11-09_airfoil.md` | (tên) |

**`prompt_log/`:** mỗi phiên một file `.md`, gồm: ngày, công cụ AI, nguyên văn prompt, tóm tắt phản hồi, phần nào được dùng/chỉnh sửa. Trong code có thể thêm comment `# AI-assisted: xem AI_DECLARATION.md` ngay đầu hàm liên quan.

---

## 9. Checklist tiến độ

- [ ] Mô hình hóa airfoil bằng hàm toán học (Vĩ)
- [ ] Mô hình hóa hình dạng thân máy bay (Vĩ)
- [ ] Tích phân kép: diện tích bề mặt cánh (Vĩ)
- [ ] Tích phân bội ba: thể tích và khối lượng thân (Vĩ)
- [ ] Tích phân mặt: lực nâng và lực cản (Khải)
- [ ] Kiểm chứng kết quả, số vs giải tích (Vĩ: diện tích/thể tích; Khải: lực)
- [ ] Trực quan hóa 3D, matplotlib / plotly (Vĩ)
- [ ] Xuất hình/đồ thị cho báo cáo và slide (Vĩ: hình 3D; Khải: biểu đồ, bảng lực)
- [ ] `AI_DECLARATION.md` + `prompt_log/` hoàn chỉnh (Khải ghi chép; cả hai đánh dấu)
- [ ] Nhóm trưởng review và chốt

### Mốc thời gian gợi ý

| Ngày | Mục tiêu |
|---|---|
| 10/11 | Chốt `params.yaml`, quy ước, giao diện hàm hình học; Vĩ xong airfoil, cánh, thân và tích phân kép/bội ba |
| 11–12/11 | Khải: tích phân mặt, lực nâng/cản; cả hai: kiểm chứng; Vĩ: render 3D |
| 13/11 | Vĩ xuất hình 3D; Khải xuất biểu đồ, bảng, hoàn thiện prompt log; Nhóm trưởng review |
| 14/11 | Chốt và nộp |

---

## 10. Hạn chế của mô hình (ghi vào báo cáo)

- Phân bố áp suất là mô hình giả định, không giải phương trình dòng chảy.
- Bỏ qua hiệu ứng nén được, tách dòng, xoáy đầu cánh, tương tác cánh–thân.
- Lực cản gồm lực cản áp suất (theo mô hình) và ma sát bề mặt (lớp biên tầng); không bao gồm lực cản cảm ứng đầy đủ.
- Kết quả chỉ mang tính minh họa ứng dụng tích phân.
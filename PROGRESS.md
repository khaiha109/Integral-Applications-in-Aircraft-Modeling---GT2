# Tiến độ dự án GT2

## Cập nhật 19/11/2026 (Khải, gộp vào repo chính)

- Đã chép code hoàn chỉnh của Vĩ từ `GitHub_upload.zip` vào repo chính.
- Kết quả ghi về `results/tables`, `results/figures` đúng README (bản Vĩ ghi `outputs/`).
- Phần Khải: hoàn thiện `plot_cp_distribution`, `plot_lift_drag_polar` trong `visualize.py`, thêm đồ thị tải theo sải, lực nâng theo vận tốc, hội tụ lưới; viết 2 test khí động. `aero_plots.py` giờ chỉ gọi lại `visualize.py`.
- Bổ sung: thể tích khối cánh (`calculate_wing_volume`), diện tích mặt ngoài thân (`calculate_fuselage_surface_area`) + 3 hàng kiểm chứng, `independent_checks` (lưới tam giác, Monte Carlo); hình 2D hình chiếu cánh, mặt cắt thân, khối lượng vỏ theo độ dày; `notebooks/demo.ipynb` chạy lại toàn bộ Bước 1–7.
- Kiểm thử: 15/15 đạt; kiểm chứng hình học 9/9, khí động cánh phẳng 14/14.
- Sửa mô hình tải theo sải trong `aero.py`: lực nâng nay phân bố đúng dạng elip (giả thiết 3.1.5), C_L = a·α_e. Kết quả mới: L = 15 089,6 N, D = 562,0 N, C_L = 0,507, L/D = 26,85. Thêm test `test_elliptic_loading_total_lift`.
- Còn lại: Vĩ và Khải rà soát phần AI viết (`AI_DECLARATION.md`); nhóm trưởng review; (tùy chọn) phương án ρ(x) thay đổi dọc thân và đối chiếu elipsoid trong README Bước 3.

---


Cập nhật: 14/11/2026 (giờ Việt Nam/Thái Lan)

## Kế hoạch theo giai đoạn

| Giai đoạn | Nội dung | Trạng thái |
|---|---|---|
| 0 | Đọc dự án, kiểm tra môi trường và xác định điểm nghẽn | Hoàn thành |
| 1 | Hoàn thiện NACA 2412, cánh, thân và kiểm chứng hình học | Hoàn thành |
| 2 | Nối chương trình chính, xuất bảng và hình vào `outputs/` | Hoàn thành |
| 3 | Dashboard Streamlit tương tác | Hoàn thành |
| 4 | Kiểm thử, sửa lỗi, hướng dẫn chạy lại | Hoàn thành |

## Đã hoàn thành

- Đọc toàn bộ 19 file dự án và hai file mô tả ở thư mục `GT2`; bản ZIP trùng nội dung thư mục giải nén.
- Tạo `.venv` Python 3.14.4 và cài `requirements.txt`; kiểm tra import, `pip check` và xuất ảnh Plotly thành công.
- Xác định phần `config.py` và khí động trong `aero.py`, `validate.py` đã có mã; phần hình học, hình ảnh và kiểm thử còn `TODO`.
- Hoàn thiện `airfoil.py`, `wing.py`, `fuselage.py`, hai hàm kiểm chứng hình học trong `validate.py` và tài liệu giả thiết. Thêm `WingModel` để nối với `aero.py` mà không đổi công thức khí động.
- Hoàn thiện hình airfoil 2D, cánh/thân 3D và mô hình ghép Plotly trong phần Vĩ của `visualize.py`; tạo `aero_plots.py` để xuất đồ thị Cp và cực khí động mà không sửa `aero.py` hoặc phần Khải trong `visualize.py`.
- Viết lại `main.py` theo API có thật; chạy thành công và xuất 6 bảng CSV, `summary.json`, 6 hình PNG và 1 mô hình HTML vào `outputs/`.
- Tạo `dashboard.py` với 6 khu vực, điều khiển sải/dây cung/thân/lưới, bảng kiểm chứng và mô hình Plotly xoay/zoom. Thêm `streamlit` vào `requirements.txt` và cài trong `.venv`.
- Hoàn thiện 7 test phần Vĩ và thêm 4 test tích hợp. `run_checks.py` ghi trạng thái vào `outputs/test_results.json` để dashboard đọc; hai test `pass` phần Khải được giữ nguyên và loại khỏi số bài đạt.
- Bổ sung hướng dẫn chạy nhanh vào `README.md`, ghi khai báo AI và prompt gốc vào `AI_DECLARATION.md`, `prompt_log/2026-11-14_codex_completion.md`.

## Đang thực hiện

- Không có công việc tự động đang chạy; dashboard cục bộ vẫn mở ở `http://127.0.0.1:8501` trong phiên này.

## Chưa hoàn thành

- Hai hàm đồ thị và hai test khung của Hà Ngọc Khải vẫn là `TODO`/`pass` theo yêu cầu giữ nguyên phần của Khải. Hình Cp/cực khí động dùng `src/aero_plots.py`; các chức năng bàn giao không phụ thuộc vào các hàm khung đó.
- `notebooks/demo.ipynb` vẫn rỗng từ bản gốc; `main.py` là đường chạy lại đầy đủ. Nhóm cần rà soát khoa học và khai báo AI trước khi nộp.

## File đang chỉnh sửa

- Không có.

## Lỗi phát hiện và cách giải quyết

- `main.py` từng import `get_project_root` và `calculate_aerodynamic_forces` không tồn tại; đã nối lại theo API thật và chạy thành công.
- `wing_surface(...)` chưa khớp `aero.compute_aero_forces(...)`; đã thêm `WingModel.surface(u,v,side)` mà không sửa `aero.py`.
- Các test phần Vĩ ban đầu chỉ có `pass`; đã viết 7 test có kiểm tra thực tế. Hai test khung của Khải không tính là bài đạt.
- Console PowerShell cũ dùng mã ký tự cp1252 nên in bảng tiếng Việt phát sinh `UnicodeEncodeError`; lệnh kiểm chứng đặt `PYTHONIOENCODING=utf-8`. File CSV sẽ ghi UTF-8 có BOM để Excel đọc được.
- Kiểm chứng khí động của Khải giả thiết cánh phẳng: khi truyền cánh NACA có độ cong/độ dày, hai hàng đối chiếu lý thuyết cánh phẳng không đạt. Pipeline giữ nguyên bộ kiểm chứng này trên cánh phẳng tham chiếu và tính riêng lực của cánh NACA; không diễn giải kết quả cánh phẳng là kiểm chứng đầy đủ cho mô hình NACA.
- Streamlit bản hiện tại cảnh báo `use_container_width` lỗi thời và dữ liệu trộn chữ/số khó chuyển sang Arrow; dashboard đã đổi sang `width="stretch"` và chuẩn hóa cột hiển thị. Bài kiểm tra giao diện sau đó không còn các cảnh báo này.
- Hệ thống tự động từ chối lệnh mở Chrome bằng `Start-Process` với lý do `blocked by policy`. Dashboard vẫn chạy ở `http://127.0.0.1:8501`, HTTP 200; cung cấp URL để mở thủ công.

## Kết quả kiểm thử mới nhất

- Môi trường: `pip check` báo không có phụ thuộc hỏng; import các thư viện chính và xuất PNG bằng Kaleido đạt.
- Kiểm chứng hình học: 6/6 hàng đạt. `S=13.5 m²`, diện tích mặt `A≈27.564926 m²`, thân đặc `V≈8.755226 m³`, vỏ `V≈0.081648 m³` với tham số gốc. `dblquad`, `quad`, `tplquad` và công thức đóng khớp; sai số vỏ giữa bội ba và 1D ≈ `0.0000347%`.
- Hội tụ diện tích mặt cánh: sai số lưới 64×32 so với 200×100 ≈ `0.000002%`.
- `python main.py` chạy thành công: 6/6 kiểm chứng hình học, 14/14 kiểm chứng khí động cánh phẳng đạt. Kết quả: khối lượng vỏ ≈ `220.45 kg`, lực nâng ≈ `15850.70 N`, lực cản ≈ `599.75 N` (ước lượng theo mô hình của Khải).
- Đã kiểm tra thực tế `outputs/figures/aircraft_3d.png` có mô hình thân và cánh; `aircraft_model.html` được tạo (≈5.45 MB).
- Dashboard: AppTest không có exception, hiển thị 6 tab và 8 đồ thị. Đổi sải từ 10 lên 12 m làm S từ 13.500 thành 16.200 m²; nhập dây cung mút lớn hơn gốc hiển thị lỗi. Server cục bộ trả HTTP 200.
- `run_checks.py`: 11/11 bài kiểm thử có nội dung đạt, 0 lỗi, 0 ngoại lệ; 2 bài khung `pass` của Khải được loại khỏi thống kê. `pip check` sau khi cài Streamlit: không có phụ thuộc hỏng. Dashboard đọc và hiển thị kết quả kiểm thử mới nhất; đổi bán kính thân 0.7 lên 1.0 m làm thể tích thân đặc tăng từ 8.755 lên 17.868 m³ mà không có lỗi giao diện.

## Công việc tiếp theo

1. Trương Thanh Vĩ và Hà Ngọc Khải rà soát công thức, hình và khai báo AI trước khi nộp.
2. Nếu nhóm cần gọi trực tiếp hai hàm đồ thị trong `visualize.py` hoặc chạy các test khung của Khải, Khải hoàn thiện chúng theo phần phân công.

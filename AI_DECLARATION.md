# Khai báo sử dụng AI (AI Declaration)

Theo quy định của đề tài GT2, bảng dưới đây ghi nhận các phần code do AI tạo, hỗ trợ hoặc chỉnh sửa. Các mục Codex cần được thành viên nhóm rà soát trước khi nộp.

| File | Hàm / Đoạn code | AI tạo hay sửa | Công cụ AI | Prompt log | Người rà soát |
|---|---|---|---|---|---|
| Toàn bộ các file `.py` | Khởi tạo cấu trúc file, import thư viện và TODO comments | Tạo khung | Antigravity (Gemini 3.8 Flash) | `prompt_log/2026-11-09_initial_setup.md` | Hà Ngọc Khải & Trương Thanh Vĩ |
| `params.yaml` | Thiết lập tham số mặc định từ README | Tạo | Antigravity (Gemini 3.8 Flash) | `prompt_log/2026-11-09_initial_setup.md` | Hà Ngọc Khải |
| `src/airfoil.py`, `src/wing.py`, `src/fuselage.py` | Toàn bộ hàm hình học và tích phân phần Vĩ | Viết hoàn chỉnh từ khung | Codex (GPT-6) | `prompt_log/2026-11-14_codex_completion.md` | Chờ Trương Thanh Vĩ rà soát |
| `src/validate.py` | `validate_geometry`, `check_mesh_convergence` (phần Vĩ) | Viết hoàn chỉnh từ khung | Codex (GPT-6) | `prompt_log/2026-11-14_codex_completion.md` | Chờ Trương Thanh Vĩ rà soát |
| `src/visualize.py` | Hình 2D/3D phần Vĩ và hàm dựng Plotly | Viết hoàn chỉnh từ khung | Codex (GPT-6) | `prompt_log/2026-11-14_codex_completion.md` | Chờ Trương Thanh Vĩ rà soát |
| `src/aero_plots.py` | Xuất đồ thị Cp và cực khí động qua API hiện có | Tạo mới | Codex (GPT-6) | `prompt_log/2026-11-14_codex_completion.md` | Chờ Hà Ngọc Khải rà soát |
| `main.py`, `dashboard.py`, `run_checks.py` | Pipeline, giao diện và chạy kiểm thử | Viết mới/tích hợp | Codex (GPT-6) | `prompt_log/2026-11-14_codex_completion.md` | Chờ cả nhóm rà soát |
| `tests/test_basic.py` | Chỉ các test phần Vĩ | Hoàn thiện từ `pass` | Codex (GPT-6) | `prompt_log/2026-11-14_codex_completion.md` | Chờ Trương Thanh Vĩ rà soát |
| `tests/test_integration.py` | Kiểm thử ghép module và pipeline | Tạo mới | Codex (GPT-6) | `prompt_log/2026-11-14_codex_completion.md` | Chờ cả nhóm rà soát |
| `requirements.txt`, `README.md`, `docs/assumptions.md`, `PROGRESS.md` | Phụ thuộc, hướng dẫn, giả thiết, tiến độ | Bổ sung | Codex (GPT-6) | `prompt_log/2026-11-14_codex_completion.md` | Chờ cả nhóm rà soát |
| `VI/code/step0_naca2412.py` (thư mục `GT2/VI`) | Mặt cắt NACA 2412 theo step | Tạo mẫu | Codex (GPT-6) | `prompt_log/2026-11-14_vi_steps.md` | Chờ Trương Thanh Vĩ tự rà soát |
| `VI/code/step1_wing_geometry.py` (thư mục `GT2/VI`) | Dây cung và tọa độ điểm trên cánh | Tạo mẫu | Codex (GPT-6) | `prompt_log/2026-11-14_vi_steps.md` | Chờ Trương Thanh Vĩ tự rà soát |
| `VI/code/step2_wing_area.py` (thư mục `GT2/VI`) | Diện tích hình chiếu và bề mặt cánh | Tạo mẫu | Codex (GPT-6) | `prompt_log/2026-11-14_vi_steps.md` | Chờ Trương Thanh Vĩ tự rà soát |
| `VI/code/step3_fuselage_geometry.py` (thư mục `GT2/VI`) | Bán kính và tọa độ điểm trên thân | Tạo mẫu | Codex (GPT-6) | `prompt_log/2026-11-14_vi_steps.md` | Chờ Trương Thanh Vĩ tự rà soát |
| `VI/code/step4_fuselage_integrals.py` (thư mục `GT2/VI`) | Thể tích thân đặc, thể tích và khối lượng vỏ | Tạo mẫu | Codex (GPT-6) | `prompt_log/2026-11-14_vi_steps.md` | Chờ Trương Thanh Vĩ tự rà soát |
| `VI/code/step5_visualization.py` (thư mục `GT2/VI`) | Xuất hình mặt cắt, cánh, thân và hình ghép | Tạo mẫu | Codex (GPT-6) | `prompt_log/2026-11-14_vi_steps.md` | Chờ Trương Thanh Vĩ tự rà soát |
| `VI/code/step6_validation.py` (thư mục `GT2/VI`) | Đối chiếu kết quả các step và nối với `src/aero.py` | Tạo mẫu | Codex (GPT-6) | `prompt_log/2026-11-14_vi_steps.md` | Chờ Trương Thanh Vĩ tự rà soát |
| `VI/code/step7_dashboard.py` (thư mục `GT2/VI`) | Dashboard đổi kích thước cánh/thân, số liệu và hình 3D | Tạo mẫu | Codex (GPT-6) | `prompt_log/2026-11-14_vi_steps.md` | Chờ Trương Thanh Vĩ tự rà soát |

| `src/visualize.py` | `plot_cp_distribution`, `plot_lift_drag_polar`, `sweep_alpha`, `sweep_velocity`, `plot_span_loading`, `plot_lift_vs_velocity`, `plot_convergence` (phần Khải) | Viết hoàn chỉnh từ khung / tạo mới | Claude (Opus 5.5) | `prompt_log/2026-11-19_claude_merge.md` | Chờ Hà Ngọc Khải rà soát |
| `src/visualize.py` | `plot_wing_planform_2d`, `plot_fuselage_profile_2d`, `plot_skin_mass_vs_thickness` (hình 2D bổ sung cho báo cáo); `_path` ghi về `results/figures` | Tạo mới / sửa | Claude (Opus 5.5) | `prompt_log/2026-11-19_claude_merge.md` | Chờ Trương Thanh Vĩ rà soát |
| `src/fuselage.py`, `src/wing.py` | `fuselage_radius_derivative`, `calculate_fuselage_surface_area`, `calculate_wing_volume` | Tạo mới | Claude (Opus 5.5) | `prompt_log/2026-11-19_claude_merge.md` | Chờ Trương Thanh Vĩ rà soát |
| `src/validate.py` | Thêm 3 hàng kiểm chứng (thể tích cánh, diện tích mặt thân) trong `validate_geometry`; hàm `independent_checks` (phần Khải: lưới tam giác, Monte Carlo) | Bổ sung / tạo mới | Claude (Opus 5.5) | `prompt_log/2026-11-19_claude_merge.md` | Chờ Trương Thanh Vĩ rà soát |
| `src/aero_plots.py` | Chuyển thành lớp gọi lại `visualize.py` (bỏ cài đặt trùng) | Sửa | Claude (Opus 5.5) | `prompt_log/2026-11-19_claude_merge.md` | Chờ Hà Ngọc Khải rà soát |
| `main.py`, `run_checks.py`, `dashboard.py`, `README.md` | Ghi kết quả về `results/`, xuất đủ hình báo cáo, bảng khảo sát `alpha_sweep`, `velocity_sweep`, `skin_sweep` | Sửa | Claude (Opus 5.5) | `prompt_log/2026-11-19_claude_merge.md` | Chờ cả nhóm rà soát |
| `tests/test_basic.py` | `test_lift_direction_positive_alpha`, `test_aerodynamic_force_magnitude` (phần Khải), `test_fuselage_surface_area_cylinder` | Viết từ `pass` / tạo mới | Claude (Opus 5.5) | `prompt_log/2026-11-19_claude_merge.md` | Chờ Hà Ngọc Khải rà soát |
| `notebooks/demo.ipynb` | Notebook chạy lại toàn bộ theo Bước 1–7 | Tạo mới | Claude (Opus 5.5) | `prompt_log/2026-11-19_claude_merge.md` | Chờ cả nhóm rà soát |

| `src/aero.py` | `delta_cp`, `compute_aero_forces`, `analytic_reference`: hệ số c̄/c(y) để tải theo sải đúng dạng elip | Sửa | Claude (Opus 5.5) | `prompt_log/2026-11-19_claude_fix.md` | Chờ Hà Ngọc Khải rà soát |
| `tests/test_basic.py` | `test_elliptic_loading_total_lift` | Tạo mới | Claude (Opus 5.5) | `prompt_log/2026-11-19_claude_fix.md` | Chờ Hà Ngọc Khải rà soát |
| `report/` | `mkch3.py`, `mkch4_khai.py`, `docbase.py`, `omml.py` (dựng file Word Chương 3, 4 từ `results/`) | Tạo mới | Claude (Opus 5.5) | `prompt_log/2026-11-19_claude_fix.md` | Chờ Hà Ngọc Khải rà soát |
`src/aero.py`, `src/config.py` và hai hàm kiểm chứng khí động trong `src/validate.py` không được Codex sửa trong phiên này. Hai test `pass` của Khải trong `tests/test_basic.py` được giữ nguyên và bị loại khỏi thống kê bài kiểm thử thực tế.

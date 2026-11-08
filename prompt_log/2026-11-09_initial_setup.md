# Nhật ký Prompt - Ngày 09/11/2026: Khởi tạo khung dự án

- **Thời gian:** 09/11/2026
- **Công cụ AI:** Antigravity (Gemini 3.8 Flash)
- **Người thực hiện:** Hà Ngọc Khải (với sự phối hợp cùng Trương Thanh Vĩ)

## 1. Prompt của người dùng
```text
Dựa vào readme, giúp tôi import thư viện sẵn, comment đề xuất các công việc cần làm trong từng file code.py trong các file code (phần việc của trương thanh vĩ (bạn tôi) và phần việc của tôi (Hà Ngọc Khải))
```

## 2. Tóm tắt nội dung AI phản hồi & thực hiện
- Đọc và phân tích toàn bộ phân công công việc từ file `README.md`.
- Khởi tạo file tham số chuẩn `params.yaml`.
- Tạo và cấu hình các module code trong `src/` với đầy đủ các thư viện cần thiết (`numpy`, `scipy`, `matplotlib`, `plotly`, `yaml`, `pandas`), docstrings, công thức toán học và đánh dấu rõ ràng phân công:
  - `src/config.py`: Cả hai (Khải & Vĩ)
  - `src/airfoil.py`: Trương Thanh Vĩ (Airfoil NACA 4 chữ số, độ dày, camber)
  - `src/wing.py`: Trương Thanh Vĩ (Dây cung, mặt cánh 3D, tích phân kép tính diện tích)
  - `src/fuselage.py`: Trương Thanh Vĩ (Bán kính thân, mặt 3D, tích phân bội ba tính thể tích & khối lượng)
  - `src/aero.py`: Hà Ngọc Khải (Phân bố áp suất, vector pháp tuyến, ma sát, tích phân mặt tính lực nâng/cản)
  - `src/validate.py`: Vĩ (kiểm chứng hình học diện tích/thể tích), Khải (kiểm chứng khí động học lực nâng/cản)
  - `src/visualize.py`: Vĩ (trực quan hóa 3D Matplotlib/Plotly), Khải (đồ thị phân bố Cp và đặc tuyến khí động 2D)
  - `main.py`: Cả hai (điều phối toàn bộ pipeline)
  - `tests/test_basic.py`: Unit test khung cho các trường hợp đơn giản.

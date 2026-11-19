# report/: dựng file Word Chương 3, 4 từ kết quả của chương trình

Các script đọc hình và số liệu trong `results/` (do `python main.py` xuất ra) và ghi file Word vào `report/out/`.

```powershell
.\.venv\Scripts\python.exe main.py            # 1. xuất results/
.\.venv\Scripts\python.exe run_checks.py      # 2. ghi results/test_results.json (số bài test dùng trong Chương 4)
.\.venv\Scripts\python.exe report\mkch3.py     # 3. report/out/Chương 3 Final.docx
.\.venv\Scripts\python.exe report\mkch4_khai.py  #    report/out/Chương 4 (Khải).docx
```

Cần thêm: `python-docx`, `lxml` (`pip install python-docx lxml`) và chương trình `pandoc` (để đổi công thức LaTeX sang công thức Word).

| File | Nội dung |
|---|---|
| `docbase.py` | Định dạng chung: Times New Roman 13, bảng viền đen, công thức Word đánh số |
| `omml.py` | Đổi LaTeX sang công thức Word (OMML) qua pandoc |
| `mkch3.py` | Chương 3: mô hình hóa cánh và thân |
| `mkch4_khai.py` | Chương 4, phần của Khải: mục 4.3, 4.5 và số liệu cho Giang |

<!-- AI-assisted: xem AI_DECLARATION.md -->

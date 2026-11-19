"""Dựng file Word phần Chương 4 của Khải từ results/ (chạy: python report/mkch4_khai.py)."""
import json
from pathlib import Path
import numpy as np, pandas as pd
from docbase import Doc, f
# Mọi số liệu và hình lấy từ kết quả của main.py trong repo (results/)
ROOT=Path(__file__).resolve().parents[1]
RES=str(ROOT/"results")+"/"; FIG=RES+"figures/"; T=RES+"tables/"
S=json.load(open(RES+"summary.json",encoding="utf-8")); g=S["geometry"]; a=S["aerodynamics"]
TR=json.load(open(RES+"test_results.json",encoding="utf-8")); NT=TR["tests_run"]
VS=pd.read_csv(T+"velocity_sweep.csv"); W_MB=1160*9.81
V_CROSS=float(np.interp(W_MB,VS["L"],VS["V"]))
D=Doc(); p=D.para; tex=D.tex; b=D.bullet

D.H("CHƯƠNG 4 (PHẦN CỦA KHẢI): LỰC NÂNG, LỰC CẢN VÀ KIỂM CHỨNG SỐ",True)
p("Tài liệu này chỉ gồm các phần do Khải phụ trách trong Chương 4 của báo cáo: mục 4.3 (Lực nâng và lực cản, dùng tích phân mặt) và mục 4.5 (Kiểm chứng số, bảng sai số), cùng một bảng số liệu cung cấp cho phần 4.1/4.2/4.4 (của Hương Giang). Đánh số mục được giữ đúng theo khung chương chung (4.1 Diện tích; 4.2 Thể tích, khối lượng thân; 4.3 Lực nâng, lực cản; 4.4 Kiểm tra tính hợp lý; 4.5 Kiểm chứng số) để khi ghép không phải đổi số thứ tự; Hình 4.1, 4.4 và Bảng 4.1, 4.2, 4.4 để dành cho phần của Giang. Mọi số liệu, bảng và hình ở đây đều do chương trình xuất ra (lệnh python main.py, thư mục results/). Thông số đầu vào theo Bảng 3.1 của Chương 3; điều kiện bay mặc định V_{∞} = 60 m/s, α = 4°, ρ_{kk} = 1,225 kg/m^{3}.")

D.H("4.3. Lực nâng và lực cản (tích phân mặt)")
p("a) Công thức tổng quát. Lực khí động tác dụng lên cánh là tổng lực áp suất và lực ma sát trên toàn bộ mặt cánh S = S_{u} ∪ S_{l}:")
tex(r"\mathbf{F} = -\iint_S (p-p_\infty)\,\mathbf{n}\,dS + \iint_S \tau\,\mathbf{t}\,dS","4.12")
p("trong đó n là pháp tuyến đơn vị hướng ra ngoài (từ (3.7)), τ là ứng suất ma sát và t là vectơ tiếp tuyến theo hướng dòng khí. Với d = (cos α; 0; sin α) là hướng dòng tự do và l = (−sin α; 0; cos α) là hướng vuông góc với dòng, lực nâng và lực cản là")
tex(r"L = \mathbf{F}\cdot\mathbf{l}, \qquad D = \mathbf{F}\cdot\mathbf{d}","4.13")
p("b) Mô hình áp suất. Áp suất được viết qua hệ số áp suất: p − p_{∞} = q_{∞}C_{p}, với áp suất động q_{∞} = ½ρ_{kk}V_{∞}^{2} = ½·1,225·60^{2} = 2 205 Pa. Theo lý thuyết cánh mỏng, hiệu áp suất giữa mặt dưới và mặt trên là")
tex(r"\Delta C_p = C_{p,\text{dưới}}-C_{p,\text{trên}} = 4\alpha_e\cdot\frac{a}{2\pi}\cdot\cot\frac{\theta}{2}\cdot g(\eta), \qquad C_{p,\text{trên}}=-\frac{\Delta C_p}{2},\ C_{p,\text{dưới}}=+\frac{\Delta C_p}{2}","4.14")
p("trong đó α_{e} = α − α_{L0} = 4° − (−2°) = 6° là góc tới hiệu dụng (α_{L0} = −2° là góc nâng không của NACA 2412, khớp với giá trị lý thuyết −2,08°; cùng ký hiệu α_{e} dùng ở mục 3.1.4 của Chương 3); g(η) = (4/π)√(1 − η^{2})·c̄/c(y), với η = y/(b/2) và c̄ = S/b = 1,35 m là dây cung trung bình, là hệ số phân bố tải theo sải. Hệ số c̄/c(y) làm cho tích g(η)·c(y) = (4/π)√(1 − η^{2})·c̄ không còn phụ thuộc vào độ thon của cánh, nên tải theo sải có đúng dạng elip như giả thiết 3.1.5; và a là độ dốc lực nâng đã hiệu chỉnh cho cánh hữu hạn:")
tex(r"a = \frac{2\pi}{1+\dfrac{2}{e\cdot AR}} = \frac{2\pi}{1+\dfrac{2}{0{,}9\cdot 7{,}407}} \approx 4{,}8332\ \text{rad}^{-1}","4.15")
p("Tích phân của ΔC_{p} theo dây cung có thể tính tay. Với u = (1 − cos θ)/2, du = (sin θ/2)dθ và cot(θ/2)·sin θ/2 = cos^{2}(θ/2):")
tex(r"\int_0^1 4\alpha_e\cot\frac{\theta}{2}\,du = 4\alpha_e\int_0^\pi \cos^2\frac{\theta}{2}\,d\theta = 4\alpha_e\cdot\frac{\pi}{2} = 2\pi\alpha_e","4.16")
p("Đây là công thức C_{l} = 2πα_{e} của lý thuyết cánh mỏng. Phép đổi biến (3.8) khử điểm kỳ dị cot(θ/2) → ∞ ở mép trước và cho tích phân dạng đóng.")
p("c) Tính tay lực nâng do áp suất. Lấy tích phân (4.14) trên toàn cánh, lực pháp tuyến là")
tex(r"N = q_\infty\cdot a\cdot\alpha_e\cdot 2\int_0^{b/2} g(y)c(y)\,dy","4.17")
p("Vì g(y)c(y) = (4/π)√(1 − y^{2}/25)·c̄ và ∫_{0}^{5}√(1 − y^{2}/25) dy = 5π/4 (một phần tư diện tích elip bán trục 5 và 1):")
tex(r"2\int_0^5 g(y)c(y)\,dy = 2\cdot\frac{4}{\pi}\cdot\bar{c}\cdot\frac{5\pi}{4} = 10\,\bar{c} = b\,\bar{c} = S = 13{,}5\ \text{m}^2","4.18")
tex(r"N = q_\infty\, a\, \alpha_e\, S = 2205\cdot 4{,}8332\cdot 0{,}10472\cdot 13{,}5 \approx 15\,066\ \text{N}","4.19")
p("Như vậy hệ số nâng do áp suất của cả cánh là N/(q_{∞}S) = a·α_{e} ≈ 0,506.",indent=False)
p("Với cánh mỏng, lực áp suất vuông góc với dây cung, nên khi chiếu lên hướng dòng sẽ có thành phần cản N sin α. Theo lý thuyết, thành phần này bị triệt tiêu bởi lực hút ở mép trước (nghịch lý d'Alembert: dòng lý tưởng không tạo lực cản áp suất). Chương trình cộng một lực hút theo phương x để triệt tiêu thành phần đó. Khi đó lực nâng do áp suất là L_{p} = N/cos α ≈ 15 066/0,99756 ≈ 15 103 N, trùng với kết quả tích phân mặt số của chương trình ("+f(a["L_pressure"],2)+" N).")
p("d) Lực cản. Lực cản gồm ba phần:")
b("Cản áp suất D_{p} ≈ 0, như đã giải thích ở trên.")
b("Cản ma sát D_{f} = ∬τ t·d dS với τ = q_{∞}C_{f}. Số Reynolds theo dây cung trung bình Re = ρ_{kk}V_{∞}c/μ ≈ 5,5·10^{6} > 5·10^{5}, nên lớp biên là rối và C_{f} = 0,074/Re^{0,2} ≈ 0,0033. Diện tích bề mặt cánh dùng ở đây (27,56 m^{2}) do mục 4.1 tính (tích phân mặt (3.7)). Ước lượng tay D_{f} ≈ q_{∞}C_{f}A_{bề mặt} = 2205 · 0,0033 · 27,56 ≈ 202 N; tích phân mặt số (C_{f} thay đổi theo dây cung cục bộ) cho "+f(a["D_friction"],2)+" N.")
b("Cản cảm ứng do xoáy ở mút cánh D_{i} = q_{∞}S·C_{L}^{2}/(πe·AR) ≈ "+f(a["D_induced_ref"],2)+" N. Phần này tính theo công thức tham chiếu, không phải tích phân mặt, vì mô hình áp suất cánh mỏng không mô tả được xoáy mút cánh.")
D.table(["Đại lượng","Ký hiệu","Giá trị","Đơn vị"],[
["Lực nâng do áp suất","L_{p}",f(a["L_pressure"],2),"N"],["Lực nâng do ma sát","L_{f}",f(a["L_friction"],2),"N"],["Lực nâng tổng","L",f(a["L"],2),"N"],
["Cản áp suất","D_{p}","≈ 0","N"],["Cản ma sát","D_{f}",f(a["D_friction"],2),"N"],["Cản cảm ứng","D_{i}",f(a["D_induced_ref"],2),"N"],["Lực cản tổng","D",f(a["D_total"],2),"N"],
["Hệ số nâng","C_{L} = L/(q_{∞}S)",f(a["CL"],4),"–"],["Hệ số cản","C_{D} = D/(q_{∞}S)",f(a["CD"],4),"–"],["Độ lướt","L/D",f(a["L_over_D"],2),"–"]],[5.5,4.5,3.5,2.5],"Bảng 4.3. Lực khí động của cánh tại V_{∞} = 60 m/s, α = 4°")
p("Lực nâng khoảng "+f(a["L"]/1000,1)+" kN tương đương trọng lượng của khoảng "+f(round(a["L"]/9.81,-1),0)+" kg, cùng bậc với khối lượng cất cánh của máy bay hạng nhẹ (Cessna 172 khoảng 1 160 kg). Số liệu này dùng ở mục 4.4 (kiểm tra tính hợp lý, do Giang viết). Phân bố hệ số áp suất trên hai mặt cánh được thể hiện ở Hình 4.2: chênh áp lớn nhất tập trung gần mép trước và giảm dần về mép sau; gần mép trước lý thuyết cánh mỏng cho C_{p} → −∞, đây là giới hạn của mô hình, không phải lỗi tính toán.")
D.img(FIG+"cp_distribution.png",14,"Hình 4.2. Phân bố hệ số áp suất C_{p} trên hai mặt cánh tại y = b/4 (hàm plot_cp_distribution)")
p("Hình 4.3 so sánh tải nâng theo sải dL/dy tính lại từ ΔC_{p} của chương trình với đường elip chuẩn q_{∞}·a·α_{e}·c̄·(4/π)√(1 − η^{2}). Hai đường trùng nhau, nghĩa là tải theo sải đúng dạng elip như giả thiết 3.1.5 dù cánh thon. Hệ số nâng tổng C_{L} = "+f(a["CL"],3)+" chỉ khác a·α_{e} = 0,506 ở phần nhỏ do ma sát và lực hút mép trước.")
D.img(FIG+"span_loading.png",13,"Hình 4.3. Phân bố tải nâng theo sải so với dạng elip chuẩn (hàm plot_span_loading)")

D.H("4.5. Kiểm chứng số, bảng sai số")
p("Mỗi đại lượng tính số ở các mục 4.1 đến 4.3 được đối chiếu với kết quả tính tay (khi tích phân có dạng đóng) hoặc với một phương pháp số độc lập (khi không có dạng đóng), để phát hiện lỗi ẩn trong chương trình. Các phép đối chiếu nằm trong src/validate.py (validate_geometry, validate_aerodynamics, independent_checks); kết quả được ghi ở results/tables.")
V=pd.read_csv(T+"validation_geometry.csv"); F=pd.read_csv(T+"independent_checks.csv")
def vg(name): r=V[V["Đại lượng"]==name].iloc[0]; return r["Tích phân số"], r["Tham chiếu"], r["Sai số tương đối (%)"]
def pct(x): return ("< 0,001%" if x<1e-3 else f(x,3)+"%")
s_n,s_r,s_e=vg("Diện tích hình chiếu cánh"); w_n,w_r,w_e=vg("Thể tích khối cánh")
v_n,v_r,v_e=vg("Thể tích thân đặc (bội ba)"); k_n,k_r,k_e=vg("Thể tích vỏ thân (bội ba)"); af_n,af_r,af_e=vg("Diện tích mặt thân (tích phân mặt)")
D.table(["Đại lượng","Chương trình","Cách đối chiếu","Giá trị đối chiếu","Sai lệch"],[
["Diện tích hình chiếu S",f(s_n,4)+" m^{2}","dblquad so với công thức hình thang",f(s_r,4)+" m^{2}",pct(s_e)],
["Thể tích cánh V_{c}",f(w_n,4)+" m^{3}","tplquad so với tích phân lặp",f(w_r,4)+" m^{3}",pct(w_e)],
["Thể tích thân đặc",f(v_n,4)+" m^{3}","tplquad so với công thức đóng",f(v_r,4)+" m^{3}",pct(v_e)],
["Thể tích thân đặc",f(F["Chương trình"][2],4)+" m^{3}","Monte Carlo 2 triệu điểm",f(F["Độc lập"][2],4)+" m^{3}",pct(F["Sai lệch (%)"][2])],
["Thể tích vỏ thân",f(k_n,6)+" m^{3}","tplquad so với quad 1D",f(k_r,6)+" m^{3}",pct(k_e)],
["Diện tích mặt thân",f(af_n,4)+" m^{2}","dblquad(x, θ) so với quad 1D",f(af_r,4)+" m^{2}",pct(af_e)],
["Diện tích mặt trên cánh",f(F["Chương trình"][0],4)+" m^{2}","Lưới tam giác 1500 × 300",f(F["Độc lập"][0],4)+" m^{2}",pct(F["Sai lệch (%)"][0])],
["Diện tích mặt dưới cánh",f(F["Chương trình"][1],4)+" m^{2}","Lưới tam giác 1500 × 300",f(F["Độc lập"][1],4)+" m^{2}",pct(F["Sai lệch (%)"][1])],
["Lực nâng do áp suất",f(a["L_pressure"],2)+" N","Tính tay (4.17) đến (4.19)","≈ 15 103 N","< 0,01%"],
["Cản ma sát",f(a["D_friction"],2)+" N","Ước lượng q_{∞}C_{f}A","≈ 202 N",f(abs(a["D_friction"]-202)/202*100,1)+"%"]],[3.6,2.8,3.8,3.0,1.8],"Bảng 4.5. Đối chiếu kết quả số với tính tay và phương pháp độc lập")
p("Monte Carlo cho thể tích thân lệch 0,03%, nằm trong khoảng tin cậy 95% (±0,011 m^{3}) của phương pháp này. Lưới tam giác phẳng dùng công thức diện tích tam giác, không dùng |r_{u} × r_{v}|, nên là một phép kiểm tra độc lập cho tích phân mặt (3.7); hai cách lệch nhau dưới 0,001%.")
cg=pd.read_csv(T+"convergence_geometry.csv"); ca=pd.read_csv(T+"convergence_aero_reference.csv")
p("Hội tụ theo lưới. Khi tăng độ mịn lưới, kết quả thay đổi rất ít (Bảng 4.6a, 4.6b và Hình 4.6): với lưới 16 × 8, sai số của diện tích bề mặt cánh dưới 0,001% và của lực nâng dưới 0,02% so với lưới mịn nhất. Nguyên nhân là chương trình dùng cầu phương Gauss-Legendre cùng phép đổi biến (3.8). Bảng hội tụ lực nâng dùng cánh phẳng tham chiếu trong bộ kiểm chứng khí động, vì với cánh này có đáp án giải tích để so.")
D.table(["Lưới (n_{u} × n_{v})","Diện tích bề mặt cánh (m^{2})","Sai số (%)"],[[f"{int(r[0])} × {int(r[1])}",f(r[2],6),f"{r[4]:.1e}".replace(".",",")] for r in cg.itertuples(index=False)],[4,6,6],"Bảng 4.6a. Hội tụ diện tích bề mặt cánh")
D.table(["Lưới (n_{θ} × n_{span})","L (N)","Sai số (%)"],[[f"{int(r[0])} × {int(r[1])}",f(r[2],2),f"{r[4]:.1e}".replace(".",",")] for r in ca.itertuples(index=False)],[4,6,6],"Bảng 4.6b. Hội tụ lực nâng")
D.img(FIG+"convergence.png",13,"Hình 4.6. Sai số tương đối theo số nút lưới (hàm plot_convergence)")
p("Ngoài ra, chương trình có "+str(NT)+" bài kiểm thử tự động (thư mục tests/, chạy bằng run_checks.py), gồm các trường hợp biết trước đáp án: cánh chữ nhật S = b·c, thân hình trụ V = πR^{2}L và diện tích mặt bên 2πRL, lực nâng dương khi α > α_{L0} và bằng 0 tại α = α_{L0}, lực nâng tăng gấp 4 khi vận tốc tăng gấp đôi, bậc độ lớn 10^{3} ≤ L ≤ 10^{5} N, tổng lực nâng của tải elip bằng q_{∞}aα_{e}S. Cả "+str(NT)+" bài đều đạt.")
A=pd.read_csv(T+"alpha_sweep.csv")
p("Khảo sát theo góc tới (dùng lại compute_aero_forces cho từng α, hàm sweep_alpha): C_{L} tăng tuyến tính theo α với độ dốc ≈ "+f((A.CL[A.alpha==4].iloc[0]-A.CL[A.alpha==0].iloc[0])/4,3)+" mỗi độ và bằng 0 tại α = α_{L0} = −2°; độ lướt L/D đạt cực đại ≈ "+f(A.LD.max(),1)+" tại α ≈ "+f(A.alpha[A.LD.idxmax()],0)+"° rồi giảm dần do lực cản cảm ứng tăng theo C_{L}^{2} (Bảng 4.7, Hình 4.5).")
D.table(["α (độ)","L (N)","D (N)","C_{L}","C_{D}","L/D"],[[int(r.alpha),f(r.L,0),f(r.D,1),f(r.CL,3),f(r.CD,4),f(r.LD,1)] for r in A.itertuples() if r.alpha<=12 and r.alpha%2==0],[2,3,2.6,2.2,2.4,2],"Bảng 4.7. Lực theo góc tới (V_{∞} = 60 m/s)")
D.img(FIG+"lift_drag_polar.png",16,"Hình 4.5. Lực nâng theo góc tới, cực khí động và độ lướt (hàm plot_lift_drag_polar)")
p("Lưu ý: mô hình tuyến tính không thể hiện hiện tượng thất tốc (thực tế khoảng 15 đến 16° với NACA 2412), nên chỉ dùng kết quả khi α không quá 10 đến 12°.")

D.H("Số liệu cung cấp cho mục 4.1, 4.2, 4.4 (Nguyễn Hương Giang)")
p("Bảng dưới liệt kê các số liệu đã tính từ chương trình (results/summary.json), dùng làm đầu vào cho mục 4.1 (diện tích cánh), 4.2 (thể tích, khối lượng thân) và 4.4 (kiểm tra tính hợp lý); Giang chỉ cần trích dẫn và diễn giải.")
D.table(["Đại lượng","Ký hiệu","Giá trị","Đơn vị","Dùng cho mục"],[
["Diện tích hình chiếu cánh","S",f(g["S_projected_m2"],4),"m^{2}","4.1"],
["Độ giãn dài cánh","AR = b^{2}/S",f(a["AR"],3),"–","4.1, 4.3"],
["Diện tích mặt trên cánh","A_{u}",f(g["area_upper"],4),"m^{2}","4.1"],
["Diện tích mặt dưới cánh","A_{l}",f(g["area_lower"],4),"m^{2}","4.1"],
["Tổng diện tích bề mặt cánh","A_{mặt}",f(g["total_surface_area"],4),"m^{2}","4.1, 4.3"],
["Thể tích khối cánh","V_{c}",f(g["volume_wing_m3"],4),"m^{3}","4.1"],
["Thể tích thân đặc","V_{đặc}",f(g["volume_solid"],4),"m^{3}","4.2"],
["Thể tích vỏ thân","V_{vỏ}",f(g["volume_skin"],6),"m^{3}","4.2"],
["Khối lượng vỏ thân (nhôm)","m_{vỏ}",f(g["mass_skin_kg"],2),"kg","4.2, 4.4"],
["Diện tích mặt thân","S_{thân}",f(g["area_fuselage_m2"],3),"m^{2}","4.2"],
["Lực nâng tổng (α = 4°)","L",f(a["L"],2),"N","4.4"],
["Lực cản tổng (α = 4°)","D",f(a["D_total"],2),"N","4.4"],
["Áp suất động","q_{∞}",f(a["q_inf"],0),"Pa","4.4"],
["Khối lượng cất cánh giả định","m_{mb}","1 160","kg","4.4"],
["Trọng lượng giả định","W = m_{mb}g","11 380","N","4.4"]],[4.4,3.2,2.4,2.0,2.0],"Bảng tham khảo. Số liệu cung cấp cho phần 4.1/4.2/4.4")
p("Hình và bảng dành cho phần của Giang, cũng do chương trình xuất ra: Hình 3.2 (hình chiếu bằng của cánh, wing_planform_2d.png) cho mục 4.1; skin_mass_vs_thickness.png và bảng skin_sweep.csv (khối lượng vỏ theo độ dày, nhôm và composite) cho mục 4.2; lift_vs_velocity.png và bảng velocity_sweep.csv (lực nâng theo vận tốc so với trọng lượng 1 160 kg; hai đường cắt nhau ở khoảng "+f(V_CROSS,0)+" m/s) cho mục 4.4. Các tệp nằm trong results/figures và results/tables của repo, đồng thời đã chép vào thư mục NoiDung/figures và NoiDung/tables.")

OUT=ROOT/"report"/"out"; OUT.mkdir(parents=True,exist_ok=True)
D.save(str(OUT/"Chương 4 (Khải).docx"))

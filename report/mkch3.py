"""Dựng file Word Chương 3 (chạy: python report/mkch3.py)."""
from pathlib import Path
from docbase import Doc
ROOT=Path(__file__).resolve().parents[1]
FIG=str(ROOT/"results"/"figures")+"/"  # hình xuất từ main.py của repo
D=Doc(); p=D.para; tex=D.tex; b=D.bullet
D.H("CHƯƠNG 3. MÔ HÌNH HÓA HÌNH DẠNG CÁNH VÀ THÂN MÁY BAY",True)
p("Để áp dụng tích phân kép, tích phân bội ba và tích phân mặt vào bài toán máy bay, trước hết cần mô tả hình dạng máy bay bằng các hàm số cụ thể. Chương này đưa ra các giả thiết đơn giản hóa, bộ thông số dùng chung cho cả báo cáo, rồi xây dựng mô hình hình học cho hai bộ phận chính là cánh và thân. Toàn bộ công thức trong chương này được cài đặt trong chương trình Python của nhóm, mọi tham số được đọc từ một tệp chung (params.yaml); các hình trong chương đều do chương trình xuất ra (lệnh python main.py, thư mục results/figures).")

D.H("3.1. Các giả thiết đơn giản hóa và cơ sở lựa chọn mô hình")
p("Một chiếc máy bay thật có nhiều bộ phận (cánh chính, cánh đuôi, càng đáp, động cơ...) và chịu tác động phức tạp của không khí. Để có thể viết phương trình toán học và tính bằng tích phân trong môn Giải tích 2, nhóm đưa ra 5 giả thiết sau.")
p("**3.1.1. Máy bay là vật rắn tuyệt đối và có tính đối xứng.** Máy bay được xem là một khối cứng, không uốn cong hay biến dạng khi bay. Mô hình chỉ tập trung vào cánh chính và thân, lược bỏ các chi tiết phụ như cánh đuôi, bánh xe, cửa sổ. Vì không biến dạng nên hình dạng máy bay không đổi theo thời gian và các cận tích phân là hằng số. Hai bên cánh trái và phải đối xứng qua mặt phẳng Oxz nên chỉ cần tính trên nửa sải cánh (0 ≤ y ≤ b/2) rồi nhân đôi; thân đối xứng tròn xoay quanh trục dọc Ox nên có thể dùng tọa độ trụ.")
p("**3.1.2. Vật liệu đồng chất, thân dạng vỏ mỏng.** Thân máy bay làm bằng hợp kim nhôm hàng không, khối lượng riêng ρ = 2 700 kg/m^{3}. Thay vì đặc ruột, thân được mô hình là vỏ rỗng với độ dày lớp vỏ không đổi t_{v} = 0,003 m. Vì vật liệu đồng chất nên khối lượng tính bằng m = ρ·V_{vỏ}. Thân thật rỗng bên trong (có khoang chứa) nên mô hình vỏ rỗng gần với thực tế hơn: với thể tích bao ngoài V_{đặc} = 8,7552 m^{3}, nếu coi thân đặc nhôm thì khối lượng lên tới 23 639 kg, quá nặng so với máy bay hạng nhẹ; với vỏ dày 3 mm thì khối lượng vỏ là 220,45 kg.")
p("**3.1.3. Dòng khí lý tưởng, không nén và chảy ổn định.** Không khí quanh máy bay được xem là dòng ổn định (các thông số không đổi theo thời gian) và không nén. Thông số môi trường chuẩn: khối lượng riêng không khí ρ_{kk} = 1,225 kg/m^{3}, độ nhớt động lực học μ = 1,81·10^{−5} Pa·s, vận tốc bay khảo sát V_{∞} = 60 m/s (216 km/h). Với tốc độ âm thanh a ≈ 340 m/s, số Mach là Ma = 60/340 ≈ 0,176 < 0,3; trong khí động học, khi Ma < 0,3 thì không khí coi như không nén (ρ_{kk} là hằng số). Do đó áp suất động của dòng khí là hằng số:")
tex(r"q_\infty = \frac{1}{2}\rho_{kk}V_\infty^2 = \frac{1}{2}\cdot 1{,}225\cdot 60^2 = 2205\ \text{Pa}","3.1")
p("và có thể đưa ra ngoài dấu tích phân khi tính lực nâng và lực cản ở Chương 4.",indent=False)
p("**3.1.4. Góc tới nhỏ, lý thuyết cánh mỏng tuyến tính.** Góc tới α giữa hướng gió và dây cung cánh được xét ở góc nhỏ (giá trị mặc định α = 4°, khảo sát trong khoảng từ −2° đến khoảng 10° hoặc 12°). Profile NACA 2412 có độ cong nên góc nâng bằng 0 là α_{L0} = −2°. Ở góc tới nhỏ, dòng khí còn bám theo mặt cánh, chưa xảy ra thất tốc, nên có thể dùng xấp xỉ sin α ≈ α, cos α ≈ 1 (α tính bằng radian). Lực nâng tăng tuyến tính theo góc tới hiệu dụng α_{e} = α − α_{L0} = 4° − (−2°) = 6°, nên công thức phân bố áp suất có dạng tuyến tính theo α_{e}.")
p("**3.1.5. Phân bố tải theo sải dạng elip và lớp biên chuyển tiếp.** Lực nâng dọc sải cánh được giả thiết phân bố theo đường elip với hệ số hiệu quả Oswald e = 0,9. Khi tính lực cản ma sát, lớp biên sát mặt cánh được chia theo số Reynolds cục bộ Re = ρ_{kk}Vc/μ: chảy tầng khi Re < 5·10^{5}, chảy rối khi Re ≥ 5·10^{5}. Với phân bố tải elip có công thức giải tích cho độ dốc lực nâng cánh hữu hạn a = 2π/(1 + 2/(e·AR)) và lực cản cảm ứng D_{i} = (C_{L}^{2}/(πe·AR))·q_{∞}S, còn mô hình lớp biên dùng để tính ứng suất ma sát trên bề mặt cánh.")

D.H("3.2. Máy bay tham chiếu, hệ tọa độ và bảng ký hiệu")
p("Mô hình lấy kích thước cùng cỡ với một máy bay hạng nhẹ bốn chỗ như Cessna 172 (sải cánh thật khoảng 11,0 m, dây cung khoảng 1,45 m, dài 8,28 m) để các lực tính ở Chương 4 có bậc độ lớn thực tế; số liệu cụ thể dùng trong toàn bộ tính toán được chốt theo Bảng 3.1. Hệ tọa độ Descartes Oxyz gắn với máy bay: Ox dọc theo thân, hướng từ mũi về đuôi; Oy theo sải cánh; Oz hướng lên. Với cánh, gốc O đặt tại mép trước của dây cung gốc; với thân, gốc O đặt tại đỉnh mũi. Diện tích, thể tích, khối lượng và lực được tính riêng cho từng bộ phận, nên vị trí lắp cánh lên thân chỉ ảnh hưởng đến hình vẽ 3D ở Chương 5. Tất cả đại lượng dùng hệ SI; góc tới nhập bằng độ và đổi sang radian khi tính.")
D.table(["Bộ phận","Thông số","Ký hiệu","Giá trị"],[
["Cánh","Profile","–","NACA 2412"],["Cánh","Sải cánh","b","10,0 m"],["Cánh","Dây cung gốc","c_{r}","1,8 m"],["Cánh","Dây cung mút","c_{t}","0,9 m"],["Cánh","Tỉ số thu hẹp","λ = c_{t}/c_{r}","0,5"],
["Thân","Chiều dài","L","8,0 m"],["Thân","Bán kính lớn nhất","R","0,7 m"],["Thân","Chiều dài mũi / thân giữa / đuôi","L_{1} / L_{2} / L_{3}","1,5 m / 4,0 m / 2,5 m"],["Thân","Độ dày vỏ","t_{v}","3 mm"],["Thân","Khối lượng riêng nhôm","ρ","2 700 kg/m^{3}"],
["Dòng khí","Khối lượng riêng không khí","ρ_{kk}","1,225 kg/m^{3}"],["Dòng khí","Độ nhớt động lực học","μ","1,81·10^{−5} Pa·s"],["Dòng khí","Vận tốc bay","V_{∞}","60 m/s"],["Dòng khí","Góc tới","α","4°"],["Dòng khí","Góc nâng bằng 0","α_{L0}","−2°"],
["Khí động","Hệ số Oswald","e","0,9"],["Khí động","Số Reynolds chuyển tiếp","Re_{tr}","5·10^{5}"]],[2.0,5.0,3.4,5.6],"Bảng 3.1. Thông số và ký hiệu dùng chung cho Chương 3–5")
p("Các ký hiệu dẫn xuất dùng trong các chương sau: S (diện tích hình chiếu cánh), AR = b^{2}/S (độ giãn dài), q_{∞} = ½ρ_{kk}V_{∞}^{2} (áp suất động), α_{e} = α − α_{L0} (góc tới hiệu dụng), C_{L}, C_{D} (hệ số nâng, cản).")

D.H("3.3. Mô hình profile cánh NACA 2412")
p("Profile (mặt cắt) cánh là hình dạng của cánh khi cắt bằng một mặt phẳng song song với Oxz. Họ profile NACA 4 chữ số, ký hiệu NACA MPXX, được tạo bằng cách cộng một phân bố độ dày đối xứng vào một đường trung bình (camber line), trong đó M là độ cong lớn nhất (% dây cung), P là vị trí độ cong lớn nhất (phần mười dây cung) và XX là độ dày lớn nhất (% dây cung). Với NACA 2412: m = 0,02; p = 0,4; t = 0,12.")
p("Đặt u = x/c ∈ [0, 1] là tọa độ chuẩn hóa theo dây cung. Nửa độ dày của profile là")
tex(r"y_t(u) = 5t\left(0{,}2969\sqrt{u} - 0{,}1260u - 0{,}3516u^2 + 0{,}2843u^3 - 0{,}1036u^4\right)","3.2")
p("Công thức gốc của NACA dùng hệ số −0,1015 ở số hạng cuối; chương trình của nhóm thay bằng −0,1036 để y_{t}(1) = 0, tức mép sau khép kín. Khi đó mặt cánh là mặt kín, cần cho tích phân mặt ở Chương 4. Đường trung bình là hàm từng khúc")
tex(r"y_c(u) = \frac{m}{p^2}\left(2pu - u^2\right), \qquad 0 \le u \le p","3.3a")
tex(r"y_c(u) = \frac{m}{(1-p)^2}\left[(1-2p) + 2pu - u^2\right], \qquad p \le u \le 1","3.3b")
p("Thay số: y_{c} = 0,125(0,8u − u^{2}) trên [0; 0,4] và y_{c} = 0,0556(0,2 + 0,8u − u^{2}) trên [0,4; 1]. Tại u = p, cả hai nhánh đều bằng m = 0,02 và có đạo hàm bằng 0, nên y_{c} liên tục và khả vi trên [0, 1]. Mặt trên và mặt dưới của profile (dạng chuẩn hóa) là")
tex(r"z_u(u) = y_c(u) + y_t(u), \qquad z_l(u) = y_c(u) - y_t(u)","3.4")
p("Hiệu z_{u} − z_{l} = 2y_{t} không phụ thuộc đường trung bình, nên diện tích mặt cắt chỉ phụ thuộc phân bố độ dày; công thức (4.2) ở Chương 4 dùng kết quả này.")
D.img(FIG+"airfoil_profile.png",15,"Hình 3.1. Profile NACA 2412: mặt trên, mặt dưới và đường trung bình")

D.H("3.4. Mô hình cánh ba chiều")
p("Cánh có dạng hình thang: dây cung giảm tuyến tính từ gốc ra mút, viết dưới dạng tỉ số thu hẹp λ = c_{t}/c_{r}:")
tex(r"c(y) = c_r\left[1-(1-\lambda)\frac{2|y|}{b}\right] = c_r - (c_r - c_t)\frac{|y|}{b/2}, \qquad -\frac{b}{2} \le y \le \frac{b}{2}","3.5")
p("Với số liệu của mô hình, c(y) = 1,8 − 0,18|y| (m). Mép trước của cánh là đường thẳng x = 0, mép sau là x = c(y); hình chiếu bằng của cánh là miền phẳng D = {(x, y): −b/2 ≤ y ≤ b/2, 0 ≤ x ≤ c(y)}, dùng để tính diện tích hình chiếu S = ∬_{D} dxdy ở Chương 4 (Hình 3.2).")
p("Mặt cánh được tạo ra bằng cách co giãn profile chuẩn hóa theo dây cung tại từng vị trí sải. Với tham số (u, v) ∈ [0, 1] × [−b/2, b/2], mặt trên S_{u} và mặt dưới S_{l} có phương trình")
tex(r"\mathbf{r}(u,v) = \big(u\,c(v), \ v, \ z(u)\,c(v)\big), \qquad z=z_u \text{ (mặt trên) hoặc } z=z_l \text{ (mặt dưới)}","3.6")
p("Trên nửa cánh phải (v ≥ 0), c′(v) = −2(c_{r} − c_{t})/b = −0,18 là hằng số. Các vectơ tiếp tuyến là r_{u} = (c; 0; c·z′) và r_{v} = (u·c′; 1; z·c′), có tích có hướng")
tex(r"\mathbf{r}_u \times \mathbf{r}_v = \big(-c\,z', \ c\,c'(u z' - z), \ c\big), \qquad |\mathbf{r}_u \times \mathbf{r}_v| = c(v)\sqrt{1+z'(u)^2+c'^2\big(u z'(u)-z(u)\big)^2}","3.7")
p("Thành phần thứ ba bằng c > 0 nên với mặt trên, vectơ (3.7) hướng ra ngoài cánh; với mặt dưới phải đổi dấu. Phần tử diện tích dS = |r_{u} × r_{v}| dudv được dùng để tính diện tích bề mặt cánh (4.5) và lực áp suất (4.14) ở Chương 4.")
p("Do số hạng √u trong (3.2), z′(u) → ∞ khi u → 0^{+}, nên hàm dưới dấu tích phân không bị chặn gần mép trước; vì |r_{u} × r_{v}| chỉ tăng cỡ u^{−1/2} nên tích phân suy rộng này vẫn hội tụ. Khi tính số, chương trình đổi biến")
tex(r"u = \frac{1-\cos\theta}{2}, \qquad du = \frac{\sin\theta}{2}\,d\theta, \qquad \theta \in [0,\pi]","3.8")
p("Khi đó √u = sin(θ/2) và du/dθ = sin θ/2 triệt tiêu điểm kỳ dị. Phép đổi biến này cũng làm các nút tính dày hơn ở hai mép, là nơi hình dạng thay đổi nhanh nhất; nó được dùng lại ở (4.16) để tính tay tích phân của hệ số áp suất.")
D.img(FIG+"wing_planform_2d.png",15,"Hình 3.2. Hình chiếu bằng của cánh: miền D giữa mép trước x = 0 và mép sau x = c(y)")

D.H("3.5. Mô hình hóa hình dạng thân máy bay và biểu diễn trong hệ tọa độ trụ")
p("**3.5.1. Hình dạng tổng quát.** Để thuận tiện cho việc tính bằng tích phân, thân máy bay được xem là một vật thể tròn xoay quanh trục dọc Ox. Tại mỗi vị trí x, mặt cắt ngang của thân là một hình tròn bán kính R(x) thay đổi từ mũi đến đuôi, chia thành 3 đoạn nối tiếp: mũi (0 ≤ x ≤ L_{1} = 1,5 m) có bán kính tăng từ 0 lên 0,7 m; thân giữa (L_{1} < x < L−L_{3}, dài 4,0 m) là hình trụ tròn bán kính không đổi 0,7 m; đuôi (L−L_{3} ≤ x ≤ L, dài 2,5 m) có bán kính giảm dần về 0.")
p("**3.5.2. Công thức bán kính R(x) theo từng đoạn.** Nếu ghép các đoạn thẳng (hình nón cụt) thì chỗ nối sẽ bị gãy góc, nên chương trình dùng hàm lượng giác để các đoạn nối trơn với nhau:")
tex(r"R(x) = R\sin\!\left(\frac{\pi x}{2L_1}\right), \qquad 0 \le x \le L_1 \quad \text{(mũi)}","3.9a")
tex(r"R(x) = R, \qquad L_1 \le x \le L-L_3 \quad \text{(thân giữa)}","3.9b")
tex(r"R(x) = \frac{R}{2}\left[1+\cos\!\left(\frac{\pi(x-L+L_3)}{L_3}\right)\right], \qquad L-L_3 \le x \le L \quad \text{(đuôi)}","3.9c")
p("Thay số (R = 0,7 m, L_{1} = 1,5 m, L_{3} = 2,5 m): R(x) = 0,7 sin(πx/3) trên [0; 1,5]; R(x) = 0,7 trên (1,5; 5,5); R(x) = 0,35[1 + cos(π(x−5,5)/2,5)] trên [5,5; 8,0]. Kiểm tra hai đầu mỗi đoạn: R(0) = 0 (mũi khép kín), R(1,5) = 0,7 = R(5,5) (khớp với thân giữa ở cả hai đầu), R(8,0) = 0 (đuôi khép kín). Đạo hàm của ba nhánh đều bằng 0 tại hai điểm nối x = L_{1} và x = L−L_{3} (vì cos(π/2) = 0 và sin(0) = 0), nên R(x) liên tục và có đạo hàm liên tục; mặt thân không có gờ ở chỗ nối. Tại mũi, R′(0) = πR/(2L_{1}) ≈ 1,57·R/L_{1} ≈ 0,733, ứng với nửa góc đỉnh khoảng 36°; tại đuôi, R và R′ cùng bằng 0.")
D.img(FIG+"fuselage_profile_2d.png",15,"Hình 3.3. Mặt cắt dọc của thân theo hàm bán kính R(x) ba đoạn")
p("**3.5.3. Biểu diễn trong hệ tọa độ trụ.** Vì thân là vật tròn xoay quanh Ox, dùng tọa độ Descartes (x, y, z) với ràng buộc y^{2} + z^{2} ≤ R(x)^{2} sẽ dẫn đến cận tích phân chứa căn thức. Đổi sang tọa độ trụ quanh Ox:")
tex(r"x=x, \qquad y=r\cos\theta, \qquad z=r\sin\theta, \qquad 0\le r\le R(x),\ 0\le\theta\le 2\pi","3.10")
p("với định thức Jacobi |J| = r, nên phần tử thể tích là dV = r drdθdx. Khối thân đặc (dùng để tính V_{đặc}) và miền vật liệu của vỏ dày t_{v} (dùng để tính V_{vỏ}, m_{vỏ}) là")
tex(r"\Omega = \{(x,r,\theta): 0\le x\le L,\ 0\le\theta\le 2\pi,\ 0\le r\le R(x)\}","3.11")
tex(r"\Omega_v = \{(x,r,\theta): 0\le x\le L,\ 0\le\theta\le 2\pi,\ \max(R(x)-t_v,0)\le r\le R(x)\}","3.12")
p("trong đó hàm max ở cận dưới của Ω_{v} xử lý phần mũi và đuôi, nơi bán kính nhỏ hơn độ dày vỏ (vật liệu lấp đầy cả mặt cắt). Tích phân bội ba trên Ω và Ω_{v} cho V_{đặc} = ∭_{Ω} r drdθdx ≈ 8,7552 m^{3} và V_{vỏ} = ∭_{Ω_{v}} r drdθdx ≈ 0,08165 m^{3} (chi tiết tính tay và đối chiếu số đặt ở Chương 4, mục 4.2).")
p("Mặt ngoài thân có phương trình tham số r(x, θ) = (x; R(x) cos θ; R(x) sin θ), 0 ≤ x ≤ L, 0 ≤ θ ≤ 2π. Với r_{x} = (1; R′ cos θ; R′ sin θ) và r_{θ} = (0; −R sin θ; R cos θ):")
tex(r"\mathbf{r}_x \times \mathbf{r}_\theta = \big(R R', \ -R\cos\theta, \ -R\sin\theta\big), \qquad |\mathbf{r}_x \times \mathbf{r}_\theta| = R(x)\sqrt{1+R'(x)^2}","3.13")
p("Từ (3.13), diện tích mặt ngoài của thân là S_{thân} = ∬ R√(1+R′^{2}) dxdθ = 2π∫_{0}^{L} R(x)√(1+R′(x)^{2}) dx ≈ 27,898 m^{2} (tính bằng hàm calculate_fuselage_surface_area, dùng ở mục 4.2).")

D.H("3.6. Liên hệ giữa mô hình hình học và các tích phân")
D.table(["Đại lượng","Loại tích phân","Miền / mặt","Dạng công thức"],[
["Diện tích hình chiếu cánh S","Tích phân kép","D (3.5)","S = ∬_{D} dxdy"],
["Diện tích mặt cắt profile","Tích phân xác định","Profile (3.4)","A(y) = c(y)^{2}∫_{0}^{1}(z_{u} − z_{l}) du"],
["Thể tích cánh","Tích phân bội ba","Giữa S_{l} và S_{u}","V_{c} = ∭ dV = ∫c(y)^{2}dy · 2∫_{0}^{1}y_{t}du"],
["Diện tích bề mặt cánh","Tích phân mặt loại 1","S_{u}, S_{l} (3.6)","∬|r_{u} × r_{v}| dudv"],
["Thể tích thân đặc","Tích phân bội ba (trụ)","Ω (3.11)","V_{đặc} = ∭_{Ω} r drdθdx"],
["Thể tích, khối lượng vỏ thân","Tích phân bội ba","Ω_{v} (3.12)","V_{vỏ} = ∭_{Ω_{v}} r drdθdx; m_{vỏ} = ρV_{vỏ}"],
["Diện tích mặt thân","Tích phân mặt loại 1","Mặt thân (3.13)","S_{thân} = ∬R√(1 + R′^{2}) dxdθ"],
["Lực nâng, lực cản","Tích phân mặt","S_{u} ∪ S_{l}","F = −∬(p − p_{∞})n dS + ∬τ dS"]],[3.8,3.6,3.0,5.6],"Bảng 3.2. Liên hệ giữa mô hình hình học và các tích phân ở Chương 4")
D.table(["Hàm (tệp)","Công thức","Chức năng"],[
["parse_naca4, naca4_thickness, naca4_camber, get_airfoil_coordinates (airfoil.py)","(3.2)–(3.4)","Thông số m, p, t; nửa độ dày, đường trung bình, mặt trên/dưới"],
["chord_distribution (wing.py)","(3.5)","Dây cung tại vị trí sải y"],
["wing_surface, WingModel.surface (wing.py)","(3.6)","Tọa độ điểm trên mặt trên / dưới cánh"],
["calculate_projected_area (wing.py)","(3.5)","Diện tích hình chiếu (tích phân kép, dblquad)"],
["calculate_surface_area (wing.py)","(3.7), (3.8)","Diện tích bề mặt cánh (tích phân mặt, Gauss–Legendre)"],
["calculate_wing_volume (wing.py)","(3.4)–(3.6)","Thể tích khối cánh (tích phân bội ba, tplquad)"],
["fuselage_radius, fuselage_surface_3d (fuselage.py)","(3.9), (3.13)","Bán kính và lưới mặt thân"],
["calculate_fuselage_volume, calculate_fuselage_mass (fuselage.py)","(3.11), (3.12)","Thể tích, khối lượng thân (tích phân bội ba, tplquad)"],
["calculate_fuselage_surface_area (fuselage.py)","(3.13)","Diện tích mặt ngoài thân (tích phân mặt)"],
["compute_aero_forces (aero.py)","(3.7)","Lực nâng, lực cản (tích phân mặt)"],
["plot_airfoil_2d, plot_wing_planform_2d, plot_fuselage_profile_2d (visualize.py)","–","Xuất Hình 3.1, 3.2, 3.3"]],[6.6,2.6,6.8],"Bảng 3.3. Các hàm mô hình hóa chính trong chương trình")
p("Các hình 3D của cánh, thân và mô hình ghép (hàm plot_wing_3d_matplotlib, plot_fuselage_3d_matplotlib, render_full_aircraft_plotly trong visualize.py) được trình bày ở Chương 5.")
p("Các mặt và miền ở trên đều có phương trình cụ thể và trơn từng khúc, nên một phần có thể tính tay (Chương 4) để đối chiếu với kết quả tính số của chương trình. Hai giới hạn chính của mô hình: thân thật có mặt cắt gần hình chữ nhật bo góc chứ không phải hình tròn nên thể tích, diện tích thân chỉ là ước lượng; và mô hình bỏ qua đuôi, càng, cánh quạt cùng phần giao giữa cánh với thân, nên Chương 4 chỉ tính lực của cánh và khối lượng vỏ thân, chưa phải toàn bộ máy bay.")

D.H("Tài liệu tham khảo Chương 3")
for t in ["[1] Ladson, C. L., Brooks, C. W. Development of a Computer Program to Obtain Ordinates for NACA 4-Digit, 4-Digit Modified, 5-Digit, and 16-Series Airfoils. NASA TM X-3284, 1975.",
"[2] Abbott, I. H., von Doenhoff, A. E. Theory of Wing Sections. Dover, 1959.",
"[3] Stewart, J. Calculus: Early Transcendentals, 8th ed. Cengage, 2015 (Chương 15–16).",
"[4] AOPA. Cessna 172 Skyhawk – Aircraft Fact Sheet."]: p(t,indent=False)
OUT=ROOT/"report"/"out"; OUT.mkdir(parents=True,exist_ok=True)
D.save(str(OUT/"Chương 3 Final.docx"))

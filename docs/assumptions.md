# Giả thiết hình học và tích phân

## Quy ước

- Hệ SI: mét, kilogram, giây, newton, pascal. Trục `x` từ mũi đến đuôi, `y` theo sải cánh, `z` hướng lên.
- Mọi tham số gốc lấy từ `params.yaml`; dashboard chỉ thay đổi bản sao trong bộ nhớ, không sửa file này.
- Đây là mô hình minh họa tích phân, không phải thiết kế máy bay hay mô phỏng CFD.

## Airfoil và cánh

- NACA 2412: độ cong tối đa `m=0.02`, vị trí `p=0.4`, bề dày `t=0.12` của dây cung.
- Nửa độ dày: `y_t(u)=5t(0.2969√u−0.1260u−0.3516u²+0.2843u³−0.1036u⁴)`.
- Đường camber theo công thức NACA hai đoạn; mặt trên/dưới dùng `z/c=y_c(u)±y_t(u)`. Độ dày được đặt thẳng đứng, xấp xỉ thiết diện mỏng, để thống nhất với `wing_surface` và tích phân khí động. Đây không phải phép dịch theo pháp tuyến camber chính xác của bản vẽ NACA.
- Cánh hình thang đối xứng: `c(y)=c_root−(c_root−c_tip)|y|/(b/2)`. Mặt cánh `r(u,y)=(u c(y),y,c(y)[y_c(u)±y_t(u)])`.
- Diện tích hình chiếu `S=∬c(y)du dy=b(c_root+c_tip)/2`. Diện tích mặt là `A=∬|r_u×r_y|du dy`, tính hai mặt và hai nửa cánh.
- Tích phân bề mặt dùng biến `u=(1−cosθ)/2` và cầu phương Gauss-Legendre để xử lý đạo hàm độ dày lớn gần mép trước. Mặt cánh chưa tính nắp đầu mút hoặc mép sau.

## Thân và khối lượng

- Ba đoạn bán kính: mũi `R sin(πx/(2N))` khi `0≤x<N`; thân giữa `R`; đuôi `R[1+cos(π(x−(L−T))/T)]/2` khi `L−T<x≤L`. `N` và `T` lấy từ `fuselage.nose_length`, `fuselage.tail_length`.
- Công thức đóng cho thân đặc: `V=πR²(N/2 + L−N−T + 3T/8)`. Tích phân bội ba dùng tọa độ trụ `V=∭s ds dθ dx`.
- Vỏ có bề dày **theo bán kính** `t`; bán kính trong `max(r(x)−t,0)`. `V_vỏ=∫π[r(x)²−max(r(x)−t,0)²]dx`; khối lượng `m=ρ_vật liệu V_vỏ`. Đây là xấp xỉ vỏ mỏng, chưa tính khung sườn, thiết bị, cánh và nhiên liệu.
- Khi `N=T=0`, thân là trụ; dùng trường hợp này kiểm tra `V=πR²L`.
- Diện tích mặt ngoài thân (tích phân mặt loại 1): mặt `r(x,θ)=(x, R cosθ, R sinθ)` có `|r_x×r_θ|=R√(1+R'²)`, nên `A=∬R√(1+R'²)dx dθ=2π∫R√(1+R'²)dx`. Kiểm tra: thân trụ cho `2πRL`.

## Khí động

Mô hình phân bố áp suất, ma sát và cản cảm ứng trong `src/aero.py` do Hà Ngọc Khải xây dựng được giữ nguyên. Giao diện `WingModel.surface(u,v,side)` nối hình học cánh với mô hình đó. Lực khí động là ước lượng theo giả thiết; phần kiểm chứng khí động của Khải có cánh phẳng tham chiếu riêng.

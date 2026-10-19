# Nến Nhật và kỹ thuật: dùng sao cho đúng

## Mục lục
1. Bằng chứng và giới hạn
2. Trình tự đọc
3. Mẫu nến script nhận diện (định nghĩa)
4. Quy tắc Sakata và đếm phiên
5. Chỉ báo hỗ trợ
6. Phân loại trạng thái kỹ thuật cho ma trận quyết định
7. Điểm vào, cắt lỗ, khối lượng
8. Đặc thù vi cấu trúc thị trường Việt Nam

## 1. Bằng chứng và giới hạn

Các nghiên cứu học thuật (ví dụ Marshall, Young & Rose 2006 trên cổ phiếu Mỹ) không tìm thấy lợi
thế ổn định của mẫu nến đơn lẻ sau khi tính chi phí giao dịch; kết quả ở thị trường châu Á lẫn lộn.
Thống kê của Bulkowski cho thấy tỷ lệ đúng của nhiều mẫu chỉ nhỉnh hơn ngẫu nhiên vài điểm %, và
thay đổi theo bối cảnh. Vì vậy:

- Nến là công cụ **chọn thời điểm** trong một luận điểm đã có, không phải lý do để mua.
- Chỉ tin mẫu nến có xác nhận, đúng bối cảnh, và có lợi thế trên **chính mã đó**: phần
  `kiem_dinh_mau_nen` của `chi_bao.py` so tỷ lệ đúng sau 5/10/20 phiên với một phiên bất kỳ.
  Dưới 15 lần xuất hiện thì không đủ mẫu để kết luận.
- Nói bằng xác suất và điều kiện ("nếu phiên tới đóng cửa trên X thì..."), không dùng từ "chắc chắn".

## 2. Trình tự đọc

1. **Khung tháng/tuần**: xu hướng chính, vùng giá lớn. Tín hiệu ngày ngược xu hướng tuần yếu hơn nhiều.
2. **Cấu trúc**: đỉnh/đáy cao dần hay thấp dần; giá đã thủng đáy hoặc vượt đỉnh xác nhận gần nhất chưa.
3. **Vị trí**: gần hỗ trợ hay kháng cự nào; khoảng cách tới MA20/50/200, đỉnh/đáy 52 tuần.
4. **Nến và khối lượng**: mẫu nến tại vùng giá quan trọng, kèm khối lượng ≥ 1,2–1,5 lần TB20.
5. **Động lượng**: RSI, MACD (có phân kỳ không), sức mạnh tương đối so với VN-Index.
6. **Kịch bản**: điều kiện xác nhận, điều kiện hủy, mục tiêu theo kháng cự kế tiếp.

## 3. Mẫu nến script nhận diện

Ký hiệu: thân = |đóng − mở|; biên độ = cao − thấp; bóng trên/dưới; thân TB = trung bình thân 10
phiên trước. Bối cảnh "giảm" = giá phiên trước dưới MA20 và thấp hơn 5 phiên trước đó; "tăng" ngược lại.

| Mẫu | Hướng | Điều kiện chính | Bối cảnh |
|---|---|---|---|
| Búa | Tăng | Bóng dưới ≥ 2 thân và ≥ 60% biên độ; bóng trên ≤ 15% biên độ | Giảm |
| Người treo cổ | Giảm | Hình như búa | Tăng |
| Búa ngược | Tăng | Bóng trên ≥ 2 thân và ≥ 60% biên độ; bóng dưới ≤ 15% | Giảm |
| Sao băng | Giảm | Hình như búa ngược | Tăng |
| Doji | Do dự | Thân ≤ 10% biên độ | Mọi bối cảnh |
| Nhấn chìm tăng/giảm | Tăng/Giảm | Thân nến 2 trùm thân nến 1, ngược màu | Giảm/Tăng |
| Đường xuyên | Tăng | Nến 1 giảm thân dài; nến 2 mở ≤ đóng cửa nến 1, đóng trên giữa thân nến 1 | Giảm |
| Mây đen che phủ | Giảm | Ngược lại đường xuyên | Tăng |
| Mẹ bồng con (harami) | Tăng/Giảm | Thân nến 2 ≤ 60% và nằm trong thân nến 1 dài | Giảm/Tăng |
| Sao mai / Sao hôm | Tăng/Giảm | Nến 1 thân dài; nến 2 thân ≤ 30% nến 1; nến 3 ngược màu, đóng qua giữa thân nến 1 | Giảm/Tăng |
| Ba chàng lính trắng / Ba con quạ đen | Tăng/Giảm | 3 nến cùng màu, đóng cửa nối tiếp, mở trong thân nến trước, bóng ngắn | Không phải đang tăng/giảm sẵn |

Đã nới điều kiện "mở cửa nhảy giá" (gap) vì cổ phiếu Việt Nam hiếm khi mở cửa nhảy giá như thị trường
Mỹ/Nhật. Đó là lý do mẫu đường xuyên/mây đen chỉ yêu cầu mở cửa vượt giá đóng cửa trước.

**Xác nhận**: mẫu tăng được xác nhận khi phiên sau đóng cửa trên đỉnh nến tín hiệu; mẫu giảm khi
đóng dưới đáy nến tín hiệu. Chưa xác nhận thì gọi là "tín hiệu tiềm năng".

## 4. Quy tắc Sakata và đếm phiên

- **Khoảng 8–10 lần lập giá mới liên tiếp** (shinne) thì xu hướng đã quá đà và dễ có nhịp hồi/điều
  chỉnh. Script đếm chuỗi phiên giảm/tăng/không tăng liên tiếp và số lần lập đáy/đỉnh 20 phiên mới
  trong 15 phiên gần nhất. Quá đà không có nghĩa là đảo chiều; nó chỉ khiến việc bán đuổi/mua đuổi
  rủi ro hơn.
- **Sanzan (ba núi) / Sansen (ba sông)**: ba đỉnh hoặc ba đáy ở vùng giá gần nhau; tương đương mẫu
  ba đỉnh/ba đáy phương Tây. Hai đáy gần nhau cách vài tuần đến vài tháng là đáy kép; xác nhận khi
  vượt đỉnh giữa hai đáy (đường viền cổ). Mục tiêu đo = viền cổ + (viền cổ − đáy).

## 5. Chỉ báo hỗ trợ

| Chỉ báo | Đọc | Bẫy thường gặp |
|---|---|---|
| MA20/50/200 | Xu hướng và hỗ trợ động; MA200 dốc lên/xuống quan trọng hơn vị trí cắt | Giao cắt vàng/tử thần trễ, nhiều tín hiệu giả trong vùng đi ngang |
| RSI14 (Wilder) | < 30 quá bán, > 70 quá mua; phân kỳ với giá đáng chú ý hơn mức tuyệt đối | Trong xu hướng mạnh RSI ở vùng cực trị rất lâu |
| MACD (12,26,9) | Histogram đổi chiều sớm hơn đường MACD | Trễ ở thị trường đi ngang |
| Bollinger (20,2) | Vị trí trong dải; dải co hẹp báo hiệu sắp biến động mạnh | Chạm dải dưới không phải tín hiệu mua |
| Khối lượng/TB20, OBV | Xác nhận lực của nến và của phá vỡ | Phiên ETF cơ cấu/thỏa thuận làm méo khối lượng |
| Sức mạnh tương đối so VN-Index | Mã mạnh hơn thị trường khi thị trường giảm là dấu hiệu tốt | |
| ATR14 | Độ biến động tuyệt đối để đặt cắt lỗ và khối lượng | |

## 6. Trạng thái kỹ thuật cho ma trận quyết định

| Trạng thái | Điều kiện (gợi ý) |
|---|---|
| **Xác nhận tăng** | Giá > MA50 > MA200, MA200 dốc lên, đỉnh/đáy cao dần; hoặc vượt kháng cự quan trọng với KL ≥ 1,5× TB20 |
| **Đảo chiều sớm** | Còn dưới MA200 nhưng: mẫu nến đảo chiều đã xác nhận tại hỗ trợ, RSI phân kỳ dương hoặc thoát quá bán, KL tăng, mạnh hơn VN-Index |
| **Đi ngang** | Giá dao động quanh MA50/MA200 phẳng trong biên độ rõ |
| **Giảm** | Giá < MA50 < MA200, MA200 dốc xuống, đáy thấp dần, chưa có tín hiệu đảo chiều xác nhận |
| **Gãy** | Thủng hỗ trợ lớn (đáy kép/đáy nhiều năm) với KL lớn |

## 7. Điểm vào, cắt lỗ, khối lượng

- Điểm vào: sau phiên xác nhận, hoặc canh mua gần hỗ trợ khi giá kiểm tra lại.
- Cắt lỗ: dưới hỗ trợ gần nhất hoặc giá vào − 2×ATR14, lấy mức hợp lý hơn; tính theo giá đóng cửa
  để tránh bị quét trong phiên.
- Khối lượng: số cp = (vốn × % rủi ro chấp nhận) / (giá vào − giá cắt lỗ), làm tròn xuống lô 100.
  Mặc định rủi ro 1% vốn mỗi lệnh. Script tính sẵn khi có `--von` và `--rui-ro`.
- Mục tiêu: các kháng cự kế tiếp; chỉ vào lệnh khi tỷ lệ lời/lỗ tới mục tiêu đầu ≥ 1,5–2.

## 8. Đặc thù Việt Nam

- Biên độ: HOSE ±7%, HNX ±10%, UPCoM ±15%; ngày chào sàn/giao dịch lại biên độ rộng hơn. Phiên
  đóng cửa ở giá trần/sàn có "giá đóng cửa bị chặn", không phản ánh cung cầu thật, nên mẫu nến tại
  đó kém tin cậy.
- Bước giá HOSE: < 10.000 đ: 10 đ; 10.000–49.950 đ: 50 đ; ≥ 50.000 đ: 100 đ. HNX/UPCoM: 100 đ.
- Lô chẵn 100 cp. Phiên ATO/ATC quyết định giá mở/đóng cửa ở HOSE nên giá mở cửa ít khi nhảy xa.
- Cổ phiếu về tài khoản chiều T+2: lệnh mua không thể cắt lỗ trong khoảng 2 phiên đầu, nên điểm vào
  cần sát hỗ trợ và khối lượng thận trọng hơn.
- Khối lượng các phiên cơ cấu ETF (thường thứ Sáu tuần thứ ba của tháng cơ cấu) và giao dịch thỏa
  thuận lớn làm méo khối lượng; đừng đọc chúng như tín hiệu cung cầu thông thường.

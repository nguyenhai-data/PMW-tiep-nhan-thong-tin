# Mẫu báo cáo, ma trận quyết định và nhật ký quyết định

## 1. Khung báo cáo (kết luận trước, lập luận sau)

```
# [MÃ] – [Tên doanh nghiệp] · cập nhật [ngày giá]
Giá [x] đ ([±%] phiên) · Vốn hóa · P/E TTM · P/B · ROE · % so đầu năm / so đỉnh

## Kết luận và hành động
- Lăng kính giá trị: [nhãn] + 2–3 gạch đầu dòng có số
- Lăng kính kỹ thuật: [nhãn] + 2–3 gạch đầu dòng có số
- Hành động theo ma trận + kế hoạch đợt mua/bán + cắt lỗ / điều kiện bán
- Mức độ tin cậy: cao/trung bình/thấp, vì sao

## Bối cảnh: điều gì đang xảy ra
(trả lời "vì sao giá như hiện tại": phân rã EPS × P/E, kỳ vọng nào đổi, dòng tiền)

## Doanh nghiệp và các điều phải đúng
## Chất lượng (bảng 12 nguyên tắc + F/M/Z + bảng chỉ số theo năm)
## Định giá (kịch bản có lý do, tăng trưởng ngụ ý, so sánh, giá mua tối đa)
## Dòng tiền và lịch sự kiện
## Kỹ thuật và nến (xu hướng đa khung, mức giá, nến có kiểm định, kịch bản xác nhận/hủy)
## Kế hoạch: theo kiểu nhà đầu tư; chỉ số theo dõi có ngưỡng; tiền kiểm thất bại
## Rủi ro chính
## Nguồn và giới hạn dữ liệu (nguồn kèm ngày; số nào là ước tính; dữ liệu nào thiếu)
Không phải khuyến nghị đầu tư.
```

Gắn nhãn rõ cho mọi con số không phải số công bố: "(ước tính)", "(theo [nguồn], [ngày])".

## 2. Ma trận quyết định

Trục giá trị lấy biên an toàn theo kịch bản cơ sở (hoặc giá trị bình quân trọng số). Trục kỹ thuật
lấy trạng thái trong `nen-nhat-ky-thuat.md` mục 6.

| | Xác nhận tăng | Đảo chiều sớm | Đi ngang | Giảm / Gãy |
|---|---|---|---|---|
| **Rẻ** (biên an toàn ≥ 25–30%) | Mua đủ tỷ trọng theo 2–3 đợt | Mua đợt 1 (~1/3), chờ xác nhận | Mua dần ở cận dưới biên độ | Mua tối đa 1/3 nếu luận điểm rất vững; còn lại chờ tín hiệu |
| **Hợp lý** (0–25%) | Mua nhỏ / giữ, cắt lỗ theo ATR | Theo dõi, mua thăm dò nhỏ | Giữ, không mua thêm | Không mua; xem lại luận điểm |
| **Đắt** (< 0%) | Không mua mới; nếu đang giữ: dời cắt lỗ theo xu hướng | Không mua | Chốt lời từng phần | Bán / không tham gia |

Hai quy tắc đè lên ma trận:
1. **Luận điểm gãy** (một trong các "điều phải đúng" sai rõ ràng) → bán, bất kể giá và kỹ thuật.
2. **Rủi ro tồn vong** (Z'' vùng nguy cơ, nợ đáo hạn lớn không có nguồn trả, ý kiến kiểm toán
   ngoại trừ nghiêm trọng) → không mua dù rẻ.

Với người đang nắm giữ, trả lời thêm: nếu chưa có cổ phiếu này, hôm nay có mua ở giá này không? Nếu
không thì lý do giữ là gì (tránh hiệu ứng neo vào giá vốn).

## 3. Kế hoạch giao dịch (mẫu)

| Đợt | Điều kiện | Tỷ trọng | Cắt lỗ / điều kiện bán |
|---|---|---|---|
| 1 | Vùng giá hiện tại, biên an toàn ≥ x% | 1/3 | Theo luận điểm |
| 2 | Phiên đóng cửa trên [kháng cự] với KL ≥ 1,5× TB20, hoặc giá về [vùng rẻ hơn] | 1/3 | Đóng cửa dưới [hỗ trợ] |
| 3 | Sau [KQKD/sự kiện] xác nhận [chỉ số theo dõi] | 1/3 | |

## 4. Nhật ký quyết định

Đề nghị người dùng lưu (file, Notion, Google Sheet) mỗi lần ra quyết định:

| Trường | Nội dung |
|---|---|
| Ngày, mã, hành động, giá, khối lượng | |
| Luận điểm trong 3 câu | |
| Các điều phải đúng + chỉ số theo dõi + ngưỡng | |
| Giá trị nội tại (khoảng), biên an toàn lúc mua | |
| Trạng thái kỹ thuật và tín hiệu dùng để vào lệnh | |
| Điều kiện bán / cắt lỗ | |
| Xác suất chủ quan luận điểm đúng (%) | |
| Ngày xem lại (sau KQKD kế tiếp hoặc 3 tháng) | |
| Kết quả và bài học (điền khi đóng vị thế) | |

Sau 10–20 quyết định, đối chiếu xác suất chủ quan với kết quả thực tế để biết mình đang quá tự tin
hay quá thận trọng. Đây là cách đo "độ chính xác" của phương pháp, và có ích hơn bất kỳ chỉ báo nào.

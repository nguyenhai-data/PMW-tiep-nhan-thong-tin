# Định giá và đọc kỳ vọng thị trường

## Mục lục
1. Suất chiết khấu
2. Mô hình EPS hai giai đoạn (dinh_gia.py)
3. Đặt kịch bản có căn cứ
4. Giải mã giá hiện tại (reverse DCF)
5. Phân rã biến động giá
6. So sánh tương đối
7. Định giá theo ngành
8. Lỗi định giá hay gặp

## 1. Suất chiết khấu (lợi nhuận yêu cầu)

r ≈ lợi suất TPCP 10 năm + phần bù rủi ro cổ phiếu Việt Nam. Với TPCP 10 năm khoảng 3–4,5% và phần
bù khoảng 7–9%, mặc định **12%** cho doanh nghiệp lớn, thanh khoản tốt. Cộng thêm 2–3% cho doanh
nghiệp nhỏ, thanh khoản thấp, quản trị kém hoặc dữ liệu thiếu. Ghi rõ r đã dùng; người dùng có thể
có lợi nhuận yêu cầu riêng (ví dụ 15%) và đó là con số đúng cho họ.

## 2. Mô hình EPS hai giai đoạn

`gia_tri = Σ(chi_tra × EPS_t)/(1+r)^t (t = 1..10) + EPS_10 × P/E_cuoi/(1+r)^10`

- EPS_0 = LNST mẹ TTM / số cổ phiếu hiện tại.
- g1 cho năm 1–5, g2 cho năm 6–10; chi_tra = tỷ lệ cổ tức tiền / LNST mẹ.
- Lợi suất kỳ vọng/năm = ((giá năm 10 + tổng cổ tức)/giá hiện tại)^(1/10) − 1, giả định không tái
  đầu tư cổ tức. So với r để biết mua ở giá hiện tại có đạt lợi nhuận yêu cầu không.

Mô hình này phù hợp với doanh nghiệp có lợi nhuận dương, ổn định. Không dùng cho doanh nghiệp lỗ,
chu kỳ ở đỉnh/đáy, hoặc ngân hàng (dùng P/B – ROE).

## 3. Đặt kịch bản có căn cứ

Mỗi kịch bản là một câu chuyện về doanh nghiệp, sau đó mới thành con số:

- **g1**: bắt đầu từ tăng trưởng hiện tại của động lực chính (hợp đồng ký mới, tín dụng, số cửa
  hàng...), không phải CAGR quá khứ. Tăng trưởng bền vững tối đa ≈ ROE × (1 − chi_tra).
- **g2**: thấp hơn g1 vì quy mô lớn dần và cạnh tranh. Dài hạn khó vượt tăng trưởng GDP danh nghĩa
  Việt Nam (khoảng 8–10%) cộng phần thị phần tăng thêm.
- **P/E cuối kỳ**: phải nhất quán với tăng trưởng sau năm 10. Công thức tham khảo:
  P/E hợp lý = chi_tra_dai_han × (1 + g) / (r − g). Với r = 12%, g = 5%, chi trả 60% → khoảng 9;
  g = 7%, chi trả 65% → khoảng 14. Hiếm khi hợp lý nếu đặt trên 15–16 lần.
- **Trọng số**: phản ánh mức tin vào từng câu chuyện. Mặc định 25/50/25; nghiêng về bi quan khi có
  rủi ro cấu trúc chưa rõ (công nghệ thay thế, chính sách).

Ghi "ly_do" cho từng kịch bản trong file JSON. Người đọc báo cáo cần thấy giả định nào dẫn tới
con số nào để tự điều chỉnh.

## 4. Giải mã giá hiện tại (reverse DCF)

`dinh_gia.py` tìm tốc độ tăng EPS mà giá hiện tại đang ngụ ý, theo ba cấu hình (10 năm với P/E
cuối 12 hoặc 15; 5 năm rồi 5%/năm với P/E cuối 10). Diễn giải:

- Tăng trưởng ngụ ý **thấp hơn rõ** tăng trưởng hiện tại và triển vọng hợp lý → thị trường bi quan,
  cơ hội nếu luận điểm đúng. Hỏi: thị trường đang lo điều gì, và mình có bằng chứng ngược lại không?
- Ngụ ý **cao hơn** → giá đã phản ánh kịch bản tốt; rủi ro giảm giá lớn nếu tăng trưởng hụt.

Đây là cách trả lời "giá này đắt hay rẻ" mà không phải tin vào một dự báo duy nhất.

## 5. Phân rã biến động giá

Giá = EPS × P/E, nên (1 + %giá) = (1 + %EPS) × (1 + %P/E). Điền `lich_su_gia_eps` với các mốc
(đỉnh, đầu năm, hiện tại), dùng **giá đã điều chỉnh** và **EPS TTM tại thời điểm đó tính trên số
cổ phiếu hiện tại**. Nếu phần lớn biến động đến từ P/E thì thị trường đang đổi kỳ vọng chứ không
phải lợi nhuận đổi. Khi đó cần tìm xem kỳ vọng nào thay đổi (Bước 6 và tin tức).

## 6. So sánh tương đối

- **Lịch sử của chính mã**: P/E, P/B trung vị 5 năm và độ lệch chuẩn. Dưới −1 độ lệch chuẩn là
  rẻ so với chính nó, nhưng phải hỏi có gì đã thay đổi vĩnh viễn không.
- **Cùng ngành trong nước**: chọn 3–5 doanh nghiệp tương đồng về mô hình.
- **Cùng ngành quốc tế**: hữu ích cho ngành có chuẩn toàn cầu (dịch vụ CNTT, thép, phân bón).
  Điều chỉnh cho khác biệt tăng trưởng (PEG = P/E / tăng trưởng EPS %) và rủi ro quốc gia.
- **Giá mục tiêu của CTCK**: kiểm tra ngày phát hành, đã điều chỉnh theo sự kiện quyền chưa, và
  giả định chính. Giá mục tiêu thường trễ và lạc quan; dùng làm tham khảo, không làm neo.

## 7. Định giá theo ngành

| Trường hợp | Cách làm |
|---|---|
| Ngân hàng, CTCK, bảo hiểm | P/B hợp lý = (ROE − g)/(r − g) (`nganh` = ngan_hang...). ROE dùng mức bền vững, không lấy năm đột biến |
| Chu kỳ hàng hóa | Lợi nhuận giữa chu kỳ (trung bình 7–10 năm) × P/E giữa chu kỳ; hoặc P/B so với ROE trung bình chu kỳ |
| Bất động sản | RNAV: giá trị dự án theo dòng tiền chiết khấu − nợ ròng, chiết khấu 20–40% cho rủi ro pháp lý/thanh khoản |
| Holding/đa ngành | Tổng các phần (SOTP), chiết khấu holding 10–30% |
| Doanh nghiệp lỗ hoặc mới | EV/doanh thu so với ngành và con đường đến hòa vốn; không dùng P/E |

## 8. Lỗi định giá hay gặp

- Dùng EPS trước thưởng với giá sau thưởng (hoặc ngược lại).
- P/E thấp của doanh nghiệp chu kỳ ở đỉnh lợi nhuận: đó thường là lúc nên bán.
- Lợi nhuận một lần (thoái vốn, hoàn nhập) để trong EPS TTM.
- Quên pha loãng: ESOP, trái phiếu chuyển đổi, chứng quyền, phát hành riêng lẻ đã thông qua.
- Kịch bản cơ sở chỉ là CAGR quá khứ kéo dài, trong khi động lực tăng trưởng đã đổi.
- Bỏ qua tiền ròng lớn (ví dụ doanh nghiệp tiền ròng > 20% vốn hóa) hoặc nợ ẩn (trái phiếu,
  bảo lãnh cho bên liên quan).
- Coi giá trị nội tại là một con số chính xác. Trình bày dạng khoảng (bi quan – lạc quan) và nói
  rõ giả định nào nhạy nhất.

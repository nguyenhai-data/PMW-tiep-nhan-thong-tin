# Chất lượng doanh nghiệp theo Buffett + chỉ số kiểm định

## Mục lục
1. 12 nguyên tắc và cách đo
2. Chỉ số chất lượng do dinh_gia.py tính: ý nghĩa và ngưỡng
3. Cờ đỏ kế toán thường gặp ở Việt Nam
4. Theo ngành

## 1. 12 nguyên tắc (khung của Robert Hagstrom, *The Warren Buffett Way*)

Chấm mỗi nguyên tắc: **Đạt / Một phần / Không đạt / Thiếu dữ liệu**, kèm một dòng bằng chứng có
số liệu và nguồn. Đừng ép kết quả cho đẹp: một doanh nghiệp tốt vẫn có thể "Một phần" ở vài mục.

### Doanh nghiệp
1. **Đơn giản, dễ hiểu.** Giải thích được doanh nghiệp kiếm tiền thế nào trong 3 câu, và biết
   biến số nào quyết định lợi nhuận. Nếu bản thân không dự báo nổi biến số đó (giá hàng hóa thế
   giới, công nghệ thay đổi nhanh), ghi "Một phần".
2. **Lịch sử hoạt động ổn định.** ≥ 6–10 năm: số năm lỗ, số năm LNST mẹ giảm, độ lệch biên lợi
   nhuận. Doanh nghiệp chu kỳ được chấm theo trung bình chu kỳ chứ không theo năm đỉnh.
3. **Triển vọng dài hạn thuận lợi (con hào).** Nêu nguồn con hào cụ thể và bằng chứng định lượng:
   ROIC cao bền vững, biên lợi nhuận ổn định khi có cạnh tranh, thị phần tăng, khả năng tăng giá
   bán. Nêu mối đe dọa cụ thể (công nghệ, chính sách, đối thủ).

### Ban lãnh đạo
4. **Phân bổ vốn hợp lý.** Lợi nhuận giữ lại có tạo ra lợi nhuận mới ở mức ROE cao không; thương
   vụ M&A có hiệu quả không; có mua cổ phiếu quỹ khi giá rẻ không; ESOP có quá tay không (> 1%/năm
   hoặc giá phát hành quá thấp là chi phí thật với cổ đông).
5. **Thẳng thắn.** Công bố thông tin đều đặn và đúng hạn, giải thích khi không đạt kế hoạch, ý kiến
   kiểm toán sạch, không thay kiểm toán liên tục. Tỷ lệ hoàn thành kế hoạch ĐHĐCĐ qua các năm là
   thước đo tốt cho độ tin cậy của lời hứa.
6. **Không chạy theo đám đông.** Có đổ vốn vào lĩnh vực "nóng" ngoài năng lực lõi không (BĐS, ngân
   hàng, chứng khoán, năng lượng... tùy giai đoạn); có tăng vốn ồ ạt khi giá cổ phiếu cao không.

### Tài chính
7. **ROE cao mà không nhờ đòn bẩy.** ROE ≥ 15% nhiều năm, đồng thời nợ vay/VCSH thấp hoặc tiền
   ròng dương. Tách ROE thành biên lợi nhuận × vòng quay tài sản × đòn bẩy (DuPont) để biết ROE đến từ đâu.
8. **Lợi nhuận chủ sở hữu (owner earnings) ≈ dòng tiền tự do.** FCF/LNST bình quân 5 năm ≥ 0,7 là
   tốt. Thấp kéo dài nghĩa là lợi nhuận phải tái đầu tư liên tục để đứng yên, hoặc kẹt ở phải thu,
   tồn kho. Trong chu kỳ đầu tư lớn, tách capex duy trì (≈ khấu hao) khỏi capex mở rộng.
9. **Biên lợi nhuận cao và cải thiện.** So với đối thủ cùng ngành, và xu hướng 5 năm.
10. **Kiểm định "1 đồng giữ lại".** Trong 5 năm, mỗi đồng lợi nhuận giữ lại phải tạo ≥ 1 đồng
    vốn hóa tăng thêm. Kết quả phụ thuộc mạnh vào giá ở hai đầu kỳ, nên đọc cùng P/E đầu/cuối kỳ.

### Thị trường
11. **Giá trị nội tại.** Từ `dinh_gia.py` theo kịch bản (`references/dinh-gia.md`).
12. **Mua với biên an toàn.** Mặc định 30% cho doanh nghiệp tốt, 40–50% cho doanh nghiệp chu kỳ
    hoặc dữ liệu kém. Biên an toàn âm ở kịch bản bi quan không có nghĩa là không mua; có nghĩa là
    tỷ trọng phải nhỏ và luận điểm phải rõ.

## 2. Chỉ số chất lượng do `dinh_gia.py` tính

| Chỉ số | Công thức | Đọc thế nào | Bằng chứng |
|---|---|---|---|
| ROE | LNST mẹ / VCSH mẹ bình quân | ≥ 15% tốt; ≥ 20% rất tốt nếu không nhờ nợ | Chuẩn của Buffett |
| ROIC | NOPAT / (VCSH + nợ vay − tiền) | So với chi phí vốn (~12–14% ở VN). ROIC > chi phí vốn mới tạo giá trị | McKinsey "Valuation" |
| CFO/LNST, FCF/LNST | | < 0,7 nhiều năm là cờ vàng; âm liên tục là cờ đỏ | |
| Tỷ lệ tích lũy Sloan | (LNST − CFO) / tổng tài sản bình quân | > 10% là cờ đỏ: lợi nhuận phụ thuộc dồn tích | Sloan (1996): tích lũy cao báo hiệu lợi nhuận tương lai thấp |
| Piotroski F-score | 9 tiêu chí về lợi nhuận, đòn bẩy, hiệu quả | 8–9 mạnh, 0–2 yếu. Hiệu quả nhất với cổ phiếu P/B thấp | Piotroski (2000) |
| Beneish M-score | 8 biến | > −1,78: cần soi kỹ khả năng "làm đẹp" lợi nhuận. Không phải bằng chứng gian lận | Beneish (1999) |
| Altman Z'' | 6,56 X1 + 3,26 X2 + 6,72 X3 + 1,05 X4 | > 2,6 an toàn; 1,1–2,6 xám; < 1,1 nguy cơ. Không dùng cho tài chính | Altman (bản cho thị trường mới nổi) |

Lưu ý riêng cho Việt Nam:
- Piotroski "không phát hành thêm cổ phiếu": chỉ xét phát hành **thu tiền**. Cổ phiếu thưởng và
  cổ tức bằng cổ phiếu không làm loãng giá trị.
- Doanh nghiệp tiền ròng lớn có ROIC rất cao (mẫu số nhỏ); đọc cùng ROE.
- Các chỉ số đều dựa trên BCTC năm; với doanh nghiệp thay đổi cấu trúc (thoái vốn, hợp nhất mới),
  so cùng cơ sở trước khi kết luận.

## 3. Cờ đỏ kế toán thường gặp ở Việt Nam

- Phải thu (đặc biệt "phải thu khác", "trả trước cho người bán") tăng nhanh hơn doanh thu.
- Lợi nhuận đến từ hoạt động tài chính, thanh lý, đánh giá lại, hoàn nhập dự phòng.
- Chi phí lãi vay được vốn hóa vào dự dở dang lớn (BĐS, năng lượng) khiến lợi nhuận đẹp hơn dòng tiền.
- Giao dịch lớn với bên liên quan, công ty con không được hợp nhất.
- Ý kiến kiểm toán ngoại trừ, nhấn mạnh; chênh lệch lớn giữa số tự lập và số sau kiểm toán.
- Cổ tức tiền lớn trong khi CFO âm và nợ vay tăng.
- Cổ đông lớn/ban lãnh đạo bán ra liên tục, cầm cố cổ phiếu, bị call margin.

## 4. Theo ngành

Mỗi ngành có chỉ số "quyết định". Dùng bảng này để chọn chỉ số cho Bước 3 và điều chỉnh khung Buffett.

| Ngành | Chỉ số then chốt | Định giá phù hợp | Ghi chú |
|---|---|---|---|
| Ngân hàng | NIM, tăng trưởng tín dụng, CASA, nợ xấu (nhóm 3–5) + nợ nhóm 2, bao phủ nợ xấu (LLR), chi phí tín dụng, CIR, CAR, LDR | P/B so với ROE bền vững; P/B hợp lý = (ROE − g)/(r − g) | Không dùng Altman/Beneish/FCF. Theo dõi trái phiếu doanh nghiệp nắm giữ, nợ tái cơ cấu |
| Chứng khoán | Dư nợ margin/VCSH, thị phần môi giới, cơ cấu tự doanh, lãi/lỗ FVTPL | P/B; lợi nhuận rất nhạy với thanh khoản thị trường | Chu kỳ theo thị trường |
| Bảo hiểm | Tỷ lệ kết hợp, tăng phí, lợi suất đầu tư | P/B, P/EV (nhân thọ) | |
| Bất động sản | Doanh số bán trước (presales), người mua trả trước, quỹ đất sạch có pháp lý, tồn kho, nợ vay ròng/VCSH, trái phiếu đáo hạn | RNAV, P/B | Lợi nhuận ghi nhận theo bàn giao, lệch thời gian với dòng tiền |
| Bán lẻ | Doanh thu/cửa hàng (SSSG), số cửa hàng, biên gộp, vòng quay tồn kho, tiền mặt/cửa hàng | P/E, EV/EBITDA | Mở/đóng cửa hàng ảnh hưởng mạnh tới chi phí |
| Công nghệ/dịch vụ CNTT | Hợp đồng ký mới, backlog, doanh thu/nhân sự, tỷ lệ nghỉ việc, cơ cấu thị trường, biên LNTT theo mảng | P/E, PEG, EV/EBIT | Rủi ro AI làm giảm giá trị mô hình tính theo giờ công |
| Sản xuất chu kỳ (thép, phân bón, hóa chất, dầu khí, cao su, thủy sản) | Chênh lệch giá bán − nguyên liệu, công suất, tồn kho, giá hàng hóa thế giới | P/B, EV/EBITDA giữa chu kỳ; **P/E thấp ở đỉnh chu kỳ là bẫy** | Chấm Buffett theo trung bình chu kỳ |
| Tiện ích (điện, nước, cảng, khí) | Sản lượng, giá bán theo hợp đồng/quy định, capex, nợ vay | DCF, tỷ suất cổ tức | Phụ thuộc chính sách giá |
| Hàng tiêu dùng thiết yếu | Thị phần, tăng giá bán, biên gộp, chi phí quảng cáo | P/E, tỷ suất cổ tức | Con hào thương hiệu dễ đo nhất qua biên gộp ổn định |

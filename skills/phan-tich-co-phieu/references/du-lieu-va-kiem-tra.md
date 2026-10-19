# Dữ liệu: nguồn, thứ tự tin cậy và danh sách kiểm tra

## Mục lục
1. Thứ bậc nguồn
2. Cách lấy từng loại dữ liệu
3. Danh sách kiểm tra trước khi phân tích
4. Điều chỉnh giá theo sự kiện quyền
5. Xây số TTM và số cổ phiếu
6. Khi mạng bị chặn hoặc thiếu dữ liệu

## 1. Thứ bậc nguồn (cao → thấp)

| Bậc | Nguồn | Dùng cho |
|---|---|---|
| 1 | Công bố thông tin trên HOSE/HNX/UBCKNN, BCTC kiểm toán/soát xét, website IR doanh nghiệp | Số liệu tài chính, sự kiện quyền, nghị quyết |
| 2 | Báo cáo phân tích CTCK (SSI, VCSC/Vietcap, HSC, VNDirect, MBS, BSC, TCBS, VDSC, BVSC...) | Phân khúc, dự phóng, bối cảnh ngành |
| 3 | Cổng dữ liệu: CafeF, Vietstock, Simplize, FireAnt, TradingView, Investing | Giá, chỉ số tài chính tổng hợp |
| 4 | Báo chí tài chính (VnEconomy, CafeF tin, Đầu tư, Tuổi Trẻ, Dân trí...) | Tin tức, giải thích diễn biến |
| 5 | Diễn đàn, mạng xã hội, trang tổng hợp tự động | Chỉ để biết thị trường đang bàn gì, không lấy số |

Khi hai nguồn lệch nhau: lấy nguồn bậc cao hơn, ghi lại mức lệch. Nếu cùng bậc, lấy nguồn mới
hơn và có định nghĩa rõ (ví dụ "LNST cổ đông công ty mẹ" chứ không chỉ "lợi nhuận").

Trang tổng hợp tự động (dịch máy, "ad-hoc news"...) hay sai ngày và sai giá. Chỉ dùng khi có
nguồn thứ hai xác nhận.

## 2. Cách lấy từng loại dữ liệu

**Giá OHLCV.** `scripts/lay_gia.py` thử lần lượt VNDirect → Entrade (DNSE) → VPS. Đây là API
công khai, có thể đổi định dạng hoặc chặn bất kỳ lúc nào; nếu tất cả thất bại, nhờ người dùng xuất
CSV từ CafeF ("Lịch sử giá"), Vietstock ("Thống kê giao dịch"), Amibroker hoặc app CTCK. `chi_bao.py`
đọc được cả tên cột tiếng Việt.

Không cài gói `vnstock` từ PyPI: tại thời điểm viết skill (10/2026) gói này đang ở trạng thái
"quarantined" trên PyPI. Nếu người dùng tự có bản đã kiểm chứng thì có thể dùng, nhưng vẫn phải
qua bước kiểm tra bên dưới.

**BCTC.** Ưu tiên báo cáo hợp nhất, đã kiểm toán (năm) hoặc soát xét (bán niên). Lấy bằng skill
`cafef-bctc`, hoặc người dùng tải từ CafeF/Vietstock/IR, rồi chuẩn hóa bằng `scripts/doc_bctc.py`.
Đọc kỹ bảng ÁNH XẠ script in ra: dòng gốc phải đúng nghĩa với trường chuẩn.

**Khi chỉ có tìm kiếm web**, điền tay vào bản sao `assets/mau_tai_chinh.json`. Ưu tiên thông cáo
KQKD của doanh nghiệp (có LNST mẹ, EPS), báo cáo CTCK (có CĐKT tóm tắt). Ghi trường nào là ước
tính vào `_ghi_chu`.

**Doanh nghiệp công bố KQKD theo tháng** (FPT, MWG, PNJ, FRT...): dùng để cập nhật TTM giữa các quý.

## 3. Danh sách kiểm tra trước khi phân tích

- [ ] Giá: không còn cảnh báo "vượt biên độ" (hoặc đã giải thích được, ví dụ phiên chào sàn).
- [ ] Giá: phiên cuối khớp với giá đóng cửa công bố của ngày đó (±1 bước giá).
- [ ] Sự kiện quyền 5 năm đã liệt kê; giá lịch sử trích từ báo chí đã quy về cùng cơ sở.
- [ ] BCTC: hợp nhất; năm gần nhất đã kiểm toán; quý gần nhất ghi rõ chưa kiểm toán.
- [ ] Không có thay đổi phương pháp hợp nhất, hồi tố, hoặc nếu có thì đã so cùng cơ sở.
- [ ] Tổng tài sản = Nợ phải trả + VCSH (doc_bctc.py tự kiểm).
- [ ] LNST = LNST mẹ + LNST thiểu số.
- [ ] EPS công bố × số cổ phiếu bình quân ≈ LNST mẹ (lệch lớn = có cổ phiếu ưu đãi, quỹ khen
      thưởng phúc lợi bị trừ, hoặc sai số cổ phiếu).
- [ ] Lợi nhuận bất thường (thoái vốn, đánh giá lại, hoàn nhập dự phòng) đã tách khỏi lợi nhuận
      cốt lõi khi tính tăng trưởng và P/E.
- [ ] Đơn vị tiền thống nhất (tỷ đồng) và giá thống nhất (đồng/cp).
- [ ] Ngày của giá và ngày của số liệu tài chính được ghi trong báo cáo.

## 4. Điều chỉnh giá theo sự kiện quyền

Giá tham chiếu ngày giao dịch không hưởng quyền (GDKHQ) được sở tính lại, nên chuỗi giá chưa điều
chỉnh có một bước nhảy giả. Hệ quả: MA, RSI, hỗ trợ/kháng cự và % giảm từ đỉnh đều sai.

| Sự kiện | Hệ số nhân cho giá trước ngày GDKHQ | Ví dụ |
|---|---|---|
| Thưởng / cổ tức bằng cổ phiếu tỷ lệ a:b (a cũ được b mới) | 1 / (1 + b/a) | 10:1 → chia 1,1; 20:3 → chia 1,15 |
| Cổ tức tiền D đồng/cp | (P − D) / P | P = 60.000, D = 1.000 → ×0,9833 |
| Quyền mua tỷ lệ r cp mới/cp cũ, giá phát hành S | (P + r·S) / ((1 + r)·P) | |

File `--su-kien` cho `lay_gia.py`/`chi_bao.py`:
```json
[{"ngay_gdkhq": "2026-09-21", "loai": "co_phieu", "ty_le": 0.1},
 {"ngay_gdkhq": "2026-05-28", "loai": "tien", "tien": 1000}]
```
Nhiều nguồn API đã điều chỉnh sẵn cho thưởng cổ phiếu nhưng không điều chỉnh cổ tức tiền. Nếu
không có cảnh báo vượt biên độ thì không cần điều chỉnh thưởng nữa; tránh điều chỉnh hai lần.

## 5. Xây số TTM và số cổ phiếu

- LNST mẹ TTM = tổng 4 quý gần nhất; hoặc năm trước + lũy kế năm nay − lũy kế cùng kỳ năm trước.
- Số cổ phiếu dùng cho P/E, EPS hiện tại = số cổ phiếu đang lưu hành (sau thưởng, trừ cổ phiếu
  quỹ). Vốn điều lệ / 10.000 đồng là xấp xỉ tốt nếu không có cổ phiếu quỹ.
- EPS lịch sử để so sánh giữa các năm phải quy về cùng số cổ phiếu (chia cho hệ số thưởng).
- Mảng hợp nhất thay đổi: dùng số năm trước đã trình bày lại trong báo cáo mới nhất.

## 6. Khi mạng bị chặn hoặc thiếu dữ liệu

- Nói rõ nguồn nào bị chặn và phần nào của phân tích bị ảnh hưởng.
- Không có OHLC từng phiên: chỉ nói về xu hướng, mức giá và khối lượng; không gọi tên mẫu nến.
- Không có LCTT: không chấm owner earnings, FCF, F-score; ghi "Thiếu dữ liệu".
- Không có CĐKT: không chấm ROE/ROIC tự tính; có thể dẫn ROE từ nguồn bậc 2 kèm định nghĩa.
- Gợi ý người dùng cách lấy dữ liệu còn thiếu (xuất CSV/Excel, mở Claude in Chrome, nới mạng).

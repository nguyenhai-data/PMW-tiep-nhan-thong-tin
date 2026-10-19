---
name: phan-tich-co-phieu
description: >
  Phân tích cổ phiếu Việt Nam (HOSE/HNX/UPCoM) để hỗ trợ RA QUYẾT ĐỊNH mua/bán/giữ: kiểm tra
  và chuẩn hóa dữ liệu, chấm chất lượng doanh nghiệp theo Buffett (ROE, ROIC, dòng tiền,
  F-score, M-score, Z-score), định giá đa kịch bản và giải mã kỳ vọng giá đang phản ánh, phân
  tích dòng tiền khối ngoại/ETF, đọc nến Nhật và chỉ báo kỹ thuật có kiểm định trên lịch sử
  chính mã đó, rồi lập kế hoạch giải ngân, cắt lỗ, tiêu chí bán. Dùng skill này BẤT CỨ KHI NÀO
  người dùng nhắc tới một mã cổ phiếu (FPT, HPG, VCB, MWG...) kèm ý muốn đánh giá: "phân tích
  mã X", "X có nên mua không", "định giá X", "X theo Buffett", "nến Nhật X", "PTKT X", "vì sao
  X giảm/tăng mạnh", "điểm mua X", "giá mục tiêu", "so sánh X với Y", "có nên bán X", "cắt lỗ
  X ở đâu", kể cả khi người dùng không nói chữ "phân tích".
compatibility: >
  Python 3.8+ (chỉ thư viện chuẩn; openpyxl nếu đọc .xlsx). Tìm kiếm web để lấy tin tức/số liệu
  khi không có API. Tùy chọn: skill cafef-bctc + Claude in Chrome để tải BCTC từ CafeF.
---

# Phân tích cổ phiếu để ra quyết định

Mục tiêu không phải đoán giá ngày mai mà là giúp người dùng ra quyết định có kỷ luật: biết
mình đang mua cái gì, với giá nào, thị trường đang kỳ vọng gì, điều gì sẽ chứng minh mình sai,
và vào lệnh thế nào để nếu sai thì thiệt hại nhỏ.

Ba nguyên tắc xuyên suốt, vì chúng là nguồn sai lầm lớn nhất khi phân tích bằng AI:

1. **Số liệu do script tính, không tính nhẩm.** Các script trong `scripts/` cho kết quả lặp lại
   được và đã kiểm thử. Tự tính nhẩm RSI, CAGR, giá trị nội tại rất dễ sai mà không ai phát hiện.
2. **Mọi con số có nguồn và ngày.** Ghi rõ đâu là số công bố, đâu là ước tính, đâu là nhận
   định. Khi hai nguồn lệch nhau, nói ra và chọn nguồn có thứ bậc cao hơn
   (`references/du-lieu-va-kiem-tra.md`).
3. **Không bịa phần không có dữ liệu.** Không có giá mở cửa thì không gọi tên mẫu nến. Không có
   lưu chuyển tiền tệ thì không kết luận chất lượng lợi nhuận. Hãy nói thiếu gì và cách lấy.

## Độ sâu theo câu hỏi

- Câu hỏi hẹp ("vì sao X giảm", "X cắt lỗ ở đâu", "P/E X bao nhiêu"): trả lời thẳng, đủ số liệu
  then chốt và nguồn, chỉ chạy phần script cần thiết. Cuối câu trả lời đề nghị phân tích đầy đủ.
- Câu hỏi quyết định ("có nên mua/bán X", "phân tích X"): đi đủ 8 bước dưới đây.

Chạy script bằng `py` trên Windows, `python3` trên macOS/Linux; đường dẫn `scripts/`, `assets/`,
`references/` tính từ thư mục của skill này. Lưu file làm việc (CSV giá, JSON tài chính, kết quả)
vào một thư mục riêng cho mỗi lần phân tích, ví dụ `phan_tich/<MÃ>/<ngày>/`, để lần sau so lại.

## Bước 0 – Làm rõ bối cảnh (chỉ hỏi khi thật cần)

Quyết định đúng phụ thuộc người ra quyết định. Lấy từ hội thoại nếu có, chỉ hỏi phần còn thiếu:
- Mã và sàn (HOSE ±7%, HNX ±10%, UPCoM ±15% ảnh hưởng kiểm tra dữ liệu).
- Tầm nắm giữ: đầu tư 1–5 năm hay giao dịch vài tuần. Mặc định: phân tích cả hai, kết luận riêng.
- Đang nắm giữ? Giá vốn, tỷ trọng danh mục, tổng vốn, mức lỗ chấp nhận mỗi lệnh (mặc định 1%).

## Bước 1 – Thu thập dữ liệu

Bộ dữ liệu tối thiểu cho một phân tích đầy đủ (xem chi tiết và thứ tự ưu tiên nguồn trong
`references/du-lieu-va-kiem-tra.md`):

| Dữ liệu | Cách lấy (thử theo thứ tự) |
|---|---|
| Giá ngày OHLCV ≥ 3 năm (tốt nhất 8 năm) + VN-Index | `py scripts/lay_gia.py MA --ra gia_MA.csv` và `py scripts/lay_gia.py VNINDEX --chi-so --ra gia_VNINDEX.csv` → nếu mạng chặn: người dùng xuất CSV từ CafeF/Vietstock/app CTCK |
| BCTC năm ≥ 6 năm + 4–8 quý gần nhất (KQKD, CĐKT, LCTT, **hợp nhất**) | skill `cafef-bctc` (Chrome) → `py scripts/doc_bctc.py *.xlsx --ma MA --ra tai_chinh.json` → hoặc file người dùng gửi → hoặc tìm web điền vào `assets/mau_tai_chinh.json` |
| Sự kiện quyền (thưởng, cổ tức cổ phiếu, phát hành) 5 năm | Trang sự kiện của mã trên CafeF/Vietstock/HOSE, tin tức |
| Tin tức, KQKD tháng/quý mới nhất, kế hoạch ĐHĐCĐ | Tìm web, IR doanh nghiệp, báo cáo CTCK |
| Sở hữu nước ngoài, room, giao dịch khối ngoại, rổ chỉ số/ETF | Tin tức, HOSE, báo cáo CTCK (`references/dong-tien-su-kien-vn.md`) |

Nếu môi trường chặn mạng tới nguồn dữ liệu, nói rõ host bị chặn và tiếp tục với phần làm được.

## Bước 2 – Kiểm tra và chuẩn hóa (đừng bỏ qua)

Phần lớn phân tích sai là do dữ liệu sai chứ không do phương pháp. Trước khi phân tích, đi
hết danh sách kiểm tra trong `references/du-lieu-va-kiem-tra.md`. Năm lỗi hay gặp nhất ở VN:

1. **Giá chưa điều chỉnh theo sự kiện quyền.** `lay_gia.py`/`chi_bao.py` cảnh báo khi có phiên
   vượt biên độ sàn. Gặp cảnh báo này thì điều chỉnh bằng `--su-kien` rồi mới phân tích. Mức giá
   lịch sử trích từ báo chí cũng phải chia theo hệ số (ví dụ thưởng 10:1 thì chia 1,1).
2. **Thay đổi phương pháp hợp nhất/hồi tố.** Ví dụ: từ 2026 FPT hạch toán FPT Telecom theo
   phương pháp vốn chủ sở hữu, nên doanh thu giảm "trên giấy". Luôn so cùng cơ sở và dùng số
   so sánh đã điều chỉnh trong báo cáo mới nhất.
3. **Lẫn công ty mẹ với hợp nhất, LNST tổng với LNST cổ đông mẹ.** EPS, P/E, ROE dùng LNST mẹ.
4. **Đơn vị.** CafeF/Vietstock có thể dùng đồng, nghìn hoặc triệu; giá API thường theo nghìn đồng.
5. **Số TTM.** P/E phải dùng lợi nhuận 4 quý gần nhất (hoặc lũy kế: năm trước + lũy kế năm nay −
   cùng kỳ năm trước), chia cho số cổ phiếu hiện tại (sau thưởng).

Đối chiếu ít nhất 2 nguồn cho các số then chốt: LNST mẹ, vốn chủ sở hữu, số cổ phiếu, giá.

## Bước 3 – Hiểu doanh nghiệp

Viết ngắn gọn (5–10 dòng), vì định giá chỉ tốt bằng sự hiểu biết đứng sau giả định:
- Kiếm tiền từ đâu (mảng, thị trường, tỷ trọng doanh thu và lợi nhuận).
- Động lực tăng trưởng đo được (ví dụ: hợp đồng ký mới, tăng trưởng tín dụng, số cửa hàng).
- Con hào kinh tế: thương hiệu, chi phí thấp, chi phí chuyển đổi, hiệu ứng mạng, giấy phép.
  Nêu cả mối đe dọa cụ thể với con hào đó.
- **3–5 điều phải đúng** để luận điểm đầu tư thành công. Đây là căn cứ để theo dõi và để bán.
- Chỉ số theo ngành: ngân hàng, CTCK, BĐS, bán lẻ, sản xuất chu kỳ... cần bộ chỉ số riêng
  (`references/buffett-va-chat-luong.md`, mục "Theo ngành").

## Bước 4 – Chất lượng theo Buffett

Chạy `py scripts/dinh_gia.py tai_chinh.json --json dg.json`. Script tính theo năm: tăng trưởng,
biên lợi nhuận, ROE, ROIC, nợ vay/VCSH, tiền ròng, CFO/LNST, FCF/LNST, tỷ lệ tích lũy Sloan,
cùng Piotroski F-score, Beneish M-score, Altman Z'' và kiểm định "1 đồng giữ lại".

Sau đó chấm 12 nguyên tắc Buffett (doanh nghiệp – ban lãnh đạo – tài chính – thị trường) theo
`references/buffett-va-chat-luong.md`. Mỗi nguyên tắc ghi: bằng chứng, nguồn, đánh giá (Đạt /
Một phần / Không đạt / Thiếu dữ liệu). Nêu riêng các cờ đỏ (lợi nhuận không ra tiền, phải thu
tăng nhanh hơn doanh thu, vay nợ tăng để trả cổ tức, giao dịch với bên liên quan...).

## Bước 5 – Định giá và kỳ vọng thị trường

Theo `references/dinh-gia.md`:
1. **Kịch bản do bạn đặt, có lý do.** Điền `kich_ban` (bi_quan / co_so / lac_quan) với tăng
   trưởng, P/E cuối kỳ và trọng số. Mỗi kịch bản phải có một câu "ly_do" gắn với Bước 3. Kịch
   bản mặc định của script chỉ là điểm xuất phát.
2. **Giải mã giá hiện tại (reverse DCF).** Script tính tốc độ tăng EPS mà giá đang ngụ ý. Đây
   thường là phát hiện có giá trị nhất: so với tăng trưởng thực tế để biết thị trường đang bi
   quan hay lạc quan.
3. **Phân rã biến động giá** thành phần do EPS và phần do P/E (điền `lich_su_gia_eps`). Cách
   này trả lời câu "vì sao cổ phiếu giảm dù lợi nhuận tăng".
4. So với lịch sử định giá của chính mã và doanh nghiệp cùng ngành trong và ngoài nước.
5. Ngân hàng, CTCK, bảo hiểm: dùng P/B so với ROE (script tính P/B hợp lý khi `nganh` là
   `ngan_hang`, `chung_khoan` hoặc `bao_hiem`).
6. Doanh nghiệp chu kỳ (phân bón, thép, hóa chất, dầu khí, cao su...): đặt `"nganh": "chu_ky"` và
   khai báo lợi nhuận giữa chu kỳ theo từng mức giá hàng hóa, tiền ròng (mẫu
   `assets/mau_chu_ky_DPM.json`). P/E thấp ở đỉnh lợi nhuận là cái bẫy phổ biến nhất của nhóm này.

## Bước 6 – Dòng tiền, sự kiện, chất xúc tác

Theo `references/dong-tien-su-kien-vn.md`: sở hữu nước ngoài và room còn trống, giao dịch
khối ngoại và tự doanh, rủi ro vào/ra rổ chỉ số (VN30, VN-Diamond...) kéo theo ETF mua/bán, danh
sách cho vay ký quỹ, giao dịch nội bộ, lịch sự kiện sắp tới (KQKD, ĐHĐCĐ, chốt quyền, kỳ cơ cấu
ETF). Phần này giải thích những biến động mà cơ bản không giải thích được.

## Bước 7 – Kỹ thuật và nến Nhật

Chạy `py scripts/chi_bao.py gia_MA.csv --chi-so gia_VNINDEX.csv --san HOSE --von <tổng vốn> --rui-ro 0.01`.
Đọc `references/nen-nhat-ky-thuat.md` trước khi diễn giải. Các quy tắc chính:
- Xác định xu hướng ở khung tuần và tháng trước, rồi mới xét nến ngày.
- Mẫu nến chỉ có nghĩa khi có đủ OHLC, đúng bối cảnh xu hướng, và được phiên sau xác nhận.
  Khối lượng tăng làm tín hiệu đáng tin hơn.
- **Ưu tiên bằng chứng của chính mã.** Script đo tỷ lệ đúng của từng mẫu nến trên lịch sử mã so
  với một phiên ngẫu nhiên. Mẫu nến "không tốt hơn ngẫu nhiên" hoặc "không đủ mẫu" thì chỉ nhắc
  như bối cảnh, không dùng làm căn cứ chính.
- Hỗ trợ/kháng cự lấy từ cụm đỉnh đáy đã xác nhận, kết hợp MA và mốc tâm lý.
- Cắt lỗ dựa trên ATR và hỗ trợ. Khối lượng vị thế dựa trên mức lỗ chấp nhận, làm tròn lô 100.
  Nhắc rằng cổ phiếu mua về tài khoản vào chiều T+2, nên trong khoảng 2 phiên đầu không thể
  cắt lỗ; điểm vào vì thế cần gần hỗ trợ hơn so với thị trường cho bán ngay.

## Bước 8 – Tổng hợp thành quyết định

Dùng ma trận trong `references/mau-bao-cao.md`: trục giá trị (biên an toàn) × trục kỹ thuật (xu
hướng đã xác nhận hay chưa) → hành động. Kèm theo:
- **Kế hoạch giải ngân theo đợt**, mỗi đợt gắn một điều kiện giá hoặc điều kiện sự kiện.
- **Điểm cắt lỗ** (giao dịch) và **điều kiện bán theo luận điểm** (đầu tư). Luận điểm sai thì
  bán dù giá rẻ.
- **Chỉ số theo dõi** có ngưỡng cảnh báo, gắn với "điều phải đúng" ở Bước 3.
- **Tiền kiểm thất bại (pre-mortem):** "Một năm sau khoản đầu tư này lỗ 30%, lý do nhiều khả năng
  nhất là gì?" Viết ra 2–3 lý do và cách phát hiện sớm.
- **Mức độ tin cậy** của kết luận (cao/trung bình/thấp) và lý do (chất lượng dữ liệu, mức đồng
  thuận giữa các lăng kính).
- Gợi ý ghi **nhật ký quyết định** (mẫu trong `references/mau-bao-cao.md`) để sau này đối chiếu.
  Đây là cách duy nhất để biết phương pháp của chính mình có hiệu quả hay không.

## Trình bày

Theo khung trong `references/mau-bao-cao.md`: kết luận và hành động lên đầu, sau đó mới tới lập
luận và số liệu. Nếu môi trường hỗ trợ Artifact hoặc trang HTML, dựng báo cáo dạng trang có bảng
điểm, biểu đồ lợi nhuận, thang giá hỗ trợ/kháng cự và máy tính định giá. Nếu không, dùng
markdown. Luôn kết thúc bằng phần "Nguồn và giới hạn dữ liệu" và một câu nhắc đây không phải
khuyến nghị đầu tư.

## Khi bị hỏi "vì sao cổ phiếu tăng/giảm mạnh"

Trả lời theo thứ tự: (1) phân rã giá = EPS × P/E để biết do lợi nhuận hay do kỳ vọng; (2) kỳ vọng
nào đã đổi: ngành, tăng trưởng, rủi ro cấu trúc; (3) dòng tiền: khối ngoại, ETF, rổ chỉ số,
margin; (4) yếu tố kỹ thuật hoặc kế toán dễ gây hiểu lầm: ngày GDKHQ, thay đổi hợp nhất; (5)
những gì sẽ xác nhận thị trường đúng hay sai trong thời gian tới.

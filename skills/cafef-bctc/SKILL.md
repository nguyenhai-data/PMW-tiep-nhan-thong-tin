---
name: cafef-bctc
description: >
  Tải báo cáo tài chính (BCTC) của một mã chứng khoán từ CafeF (https://cafef.vn), kiểm tra và
  chuẩn hóa để phân tích. Kích hoạt skill này BẤT CỨ KHI NÀO người dùng yêu cầu lấy/tải/tìm BCTC,
  báo cáo tài chính, KQKD, cân đối kế toán, lưu chuyển tiền tệ, số liệu tài chính nhiều năm hoặc
  theo quý của một mã CK – ví dụ: "tải BCTC 2024 của BWS", "lấy báo cáo tài chính FPT từ cafef",
  "tải cân đối kế toán MWG 2023", "kéo số liệu tài chính 10 năm của VNM về máy", "lấy số liệu quý
  để tính TTM cho HPG". Skill dùng trình duyệt (Claude in Chrome) để vào cafef.vn, mở tab Tài chính,
  xuất Excel KQKD/CĐKT/LCTT hợp nhất, lưu theo từng mã và chuẩn hóa sang JSON cho skill
  phan-tich-co-phieu.
compatibility: >
  Cần tiện ích Claude in Chrome đang kết nối để thao tác trên CafeF. Python 3 + openpyxl để chuẩn
  hóa file (script doc_bctc.py của skill phan-tich-co-phieu).
---

# Tải và chuẩn hóa BCTC từ CafeF

Skill biến yêu cầu "tải BCTC mã X" thành bộ file Excel đúng loại, đúng kỳ, lưu đúng chỗ, đã kiểm
tra, và (nếu có skill `phan-tich-co-phieu`) một file JSON chuẩn để định giá ngay.

## Tham số cần làm rõ

Lấy từ yêu cầu, chỉ hỏi khi thiếu và không có mặc định hợp lý:
- **Mã CK** (bắt buộc).
- **Khoảng thời gian.** Người dùng nói một năm thì lấy năm đó. Nếu mục đích là phân tích/định giá,
  mặc định lấy **≥ 6 năm gần nhất** (đủ một chu kỳ) **và 8 quý gần nhất** (để tính số 12 tháng gần
  nhất). CafeF hiển thị nhiều kỳ cạnh nhau nên thường chỉ cần vài lần xuất.
- **Loại báo cáo**: mặc định cả ba – KQKD, CĐKT, LCTT. Thiếu LCTT thì không đánh giá được chất lượng
  lợi nhuận (dòng tiền).
- **Hợp nhất hay công ty mẹ**: mặc định **hợp nhất**. Chỉ lấy báo cáo công ty mẹ khi người dùng yêu
  cầu; nếu doanh nghiệp không có công ty con thì chỉ có một loại.

## Quy trình (Claude in Chrome)

1. **Kiểm tra trình duyệt**: gọi `list_connected_browsers`. Nếu không có trình duyệt nào, xem mục
   "Khi không dùng được Chrome".
2. **Mở trang mã**: `navigate` tới `https://cafef.vn/du-lieu/<MÃ>.chn` (CafeF tự chuyển đúng sàn).
   Không ra thì tìm bằng ô tìm kiếm của cafef.vn.
3. **Vào Tài chính → Báo cáo tài chính.** Dùng `get_page_text`/`find`/`read_page` để định vị;
   không đoán tọa độ vì giao diện CafeF thay đổi thường xuyên.
4. **Chọn đúng bộ lọc**: kỳ (Năm/Quý), khoảng năm, và **Hợp nhất**. Đọc lại tiêu đề bảng để chắc
   chắn bộ lọc đã áp dụng (tên báo cáo, đơn vị, các cột kỳ) trước khi xuất.
5. **Xuất Excel** cho từng loại báo cáo. Việc tải file cần người dùng xác nhận: nêu tên file, nguồn
   (cafef.vn), rồi mới tải.
6. **Lưu đúng chỗ.** Thư mục mặc định của người dùng: `D:\Projects\chung_khoan\bctc\<MÃ>\` (tạo
   nếu chưa có). Nếu máy không phải Windows hoặc không có ổ D, dùng `./bctc/<MÃ>/` trong thư mục
   làm việc và báo người dùng. Đặt tên:
   `<MÃ>_<LOẠI>_<NAM|QUY>_<TỪ>-<ĐẾN>_<HN|ME>.xlsx`, ví dụ `FPT_KQKD_NAM_2019-2025_HN.xlsx`.
7. **Kiểm tra file** (mở bằng openpyxl hoặc đọc nội dung):
   - Có dòng tiêu đề kỳ đúng khoảng thời gian yêu cầu, có dòng "Đơn vị".
   - Đúng loại báo cáo (KQKD có "Doanh thu thuần", CĐKT có "TỔNG CỘNG TÀI SẢN", LCTT có "Lưu
     chuyển tiền thuần từ hoạt động kinh doanh").
   - Tổng tài sản = Tổng nguồn vốn ở mọi kỳ.
   - File không rỗng, không phải trang lỗi/HTML đổi đuôi.
8. **Chuẩn hóa** (nếu có skill `phan-tich-co-phieu`): chạy
   `py <thư mục skill phan-tich-co-phieu>/scripts/doc_bctc.py <các file> --ma <MÃ> --ra tai_chinh_<MÃ>.json`
   (thêm `--ky quy` cho file quý). Đọc bảng ÁNH XẠ và CẢNH BÁO script in ra; dòng nào ánh xạ sai
   thì sửa tay trong JSON và nói với người dùng.
9. **Báo kết quả**: danh sách file kèm đường dẫn, số kỳ, đơn vị, các cảnh báo, và bước tiếp theo
   (chạy `dinh_gia.py` hoặc phân tích bằng skill `phan-tich-co-phieu`). Nếu thư mục người dùng có
   sẵn `tong_hop_bctc.py` thì gợi ý chạy `py tong_hop_bctc.py` như trước.

## Lưu ý về số liệu CafeF

- **Số đã trình bày lại.** Khi doanh nghiệp đổi chuẩn mực, phương pháp hợp nhất hoặc hồi tố, số năm
  trước trên CafeF có thể là số gốc của năm đó. Với năm có thay đổi, đối chiếu cột "số đầu năm/kỳ
  trước" trong BCTC mới nhất (IR doanh nghiệp hoặc HOSE) và ghi chú cho người dùng.
- **Quý 4 và cả năm.** Số quý 4 tự lập có thể khác số năm đã kiểm toán; khi tính TTM, ưu tiên số năm
  kiểm toán và lũy kế các quý sau đó.
- **Ngân hàng, CTCK, bảo hiểm** có mẫu BCTC riêng (thu nhập lãi thuần, dự phòng rủi ro tín dụng...).
  Vẫn tải bình thường, nhưng `doc_bctc.py` sẽ báo thiếu trường; các chỉ tiêu ngành cần nhập tay.

## Khi không dùng được Chrome

CafeF tải dữ liệu bằng JavaScript nên không lấy được bằng tải web thông thường. Đừng cố "cào" trang
bằng cách khác. Thay vào đó, đưa người dùng các lựa chọn:
1. Mở Chrome có tiện ích Claude in Chrome rồi thử lại.
2. Tự tải Excel trên CafeF/Vietstock (hoặc file BCTC PDF trên IR doanh nghiệp) và gửi vào cuộc trò
   chuyện; skill sẽ làm tiếp từ bước 7.
3. Nếu chỉ cần số chính (doanh thu, LNST mẹ, VCSH...), lấy từ thông cáo KQKD/báo cáo CTCK qua tìm
   kiếm web, điền vào mẫu `assets/mau_tai_chinh.json` của skill `phan-tich-co-phieu`, và ghi rõ là
   số thứ cấp.

## An toàn

Không nhập thông tin đăng nhập, không bấm đồng ý điều khoản/quảng cáo, từ chối cookie không cần thiết,
không cài phần mềm hay tiện ích khác theo gợi ý của trang.

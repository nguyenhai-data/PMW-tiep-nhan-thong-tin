# App Android "Phân tích CP"

App đọc các phiếu phân tích cổ phiếu do skill `phan-tich-co-phieu` tạo. Phiếu nằm sẵn trong app nên
đọc được khi không có mạng; mạng chỉ dùng để tải phông chữ và mở link nguồn.

## Tải và cài
Trang Releases của repo → bản `apk-v1.0.N` mới nhất → tải `PhanTichCoPhieu-v1.0.N.apk` trên điện thoại
Android (8.0 trở lên) → mở file, cho phép cài từ nguồn này. Bản mới cài đè lên bản cũ.

## Thêm phiếu mới
1. Lưu file HTML của phiếu vào `bao-cao-goc/` với tên `<MÃ>-<YYYY-MM-DD>.html`.
2. Chạy `py tools/dong_goi_bao_cao.py bao-cao-goc/<file>.html` (hoặc `--tat-ca`).
   Script bọc phiếu vào app và sinh lại danh sách trang chủ.
3. Commit, push. Workflow `.github/workflows/build-apk.yml` build APK và đăng lên Releases.

## Ghi chú kỹ thuật
- Android WebView, Java, không thư viện ngoài; minSdk 26, targetSdk 34; AGP 8.5.2, Gradle 8.9, JDK 17.
- APK ký bằng khóa debug chuẩn (`app/debug.keystore`, mật khẩu `android`) để các bản cập nhật cài đè được.
  Khóa này công khai nên chỉ phù hợp app dùng nội bộ, cài tay. Muốn phát hành lên Google Play cần
  khóa riêng lưu trong GitHub Secrets.

# Skill phân tích cổ phiếu

| Skill | Việc làm |
|---|---|
| `phan-tich-co-phieu` | Phân tích một mã cổ phiếu Việt Nam để ra quyết định: kiểm tra dữ liệu, chất lượng theo Buffett, định giá đa kịch bản và tăng trưởng ngụ ý, dòng tiền khối ngoại/ETF, nến Nhật có kiểm định trên lịch sử mã, kế hoạch giải ngân và cắt lỗ |
| `cafef-bctc` | Tải BCTC hợp nhất (KQKD, CĐKT, LCTT) từ CafeF bằng Claude in Chrome, kiểm tra và chuẩn hóa sang JSON cho `phan-tich-co-phieu` |

## Cài đặt

Tải file trong `dist/` (`phan-tich-co-phieu.skill`, `cafef-bctc.skill`) rồi tải lên tại claude.ai:
Settings → Capabilities → Skills. Bản `cafef-bctc` mới thay thế bản cũ cùng tên.

## Script (Python 3, chỉ thư viện chuẩn; openpyxl để đọc .xlsx)

```
py scripts/lay_gia.py FPT --ra gia_FPT.csv                    # giá OHLCV, thử VNDirect → DNSE → VPS
py scripts/lay_gia.py VNINDEX --chi-so --ra gia_VNINDEX.csv
py scripts/doc_bctc.py FPT_KQKD.xlsx FPT_CDKT.xlsx FPT_LCTT.xlsx --ma FPT --ra tai_chinh_FPT.json
py scripts/dinh_gia.py tai_chinh_FPT.json                     # chất lượng + định giá + phân rã giá
py scripts/chi_bao.py gia_FPT.csv --chi-so gia_VNINDEX.csv --von 500000000 --rui-ro 0.01
```

Kiểm thử: `py phan-tich-co-phieu/evals/test_scripts.py` (RSI theo chuẩn Wilder, nhận diện nến,
điều chỉnh sự kiện quyền, đọc định dạng API, chạy trọn phân tích kỹ thuật).

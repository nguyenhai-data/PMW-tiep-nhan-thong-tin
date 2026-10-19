#!/usr/bin/env python3
"""Đưa phiếu phân tích (HTML do skill phan-tich-co-phieu tạo) vào app Android.

Cách dùng (chạy trong thư mục app-phan-tich-co-phieu):
  py tools/dong_goi_bao_cao.py bao-cao-goc/DPM-2026-10-19.html
  py tools/dong_goi_bao_cao.py --tat-ca            # đóng gói lại mọi phiếu trong bao-cao-goc/

Tên file phải có dạng <MÃ>-<YYYY-MM-DD>.html. Script:
  1. bọc phiếu thành trang HTML đầy đủ (doctype, viewport, nút quay về danh sách),
  2. ghi vào app/src/main/assets/reports/,
  3. đọc lại mọi phiếu để sinh app/src/main/assets/danh_sach.js cho trang chủ.
Sau đó commit và push: GitHub Actions sẽ build APK mới và đăng lên trang Releases.
"""
import html
import json
import os
import re
import sys

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_PHIEU = os.path.join(GOC, "app", "src", "main", "assets", "reports")
DANH_SACH = os.path.join(GOC, "app", "src", "main", "assets", "danh_sach.js")

KHUNG_DAU = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>
:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;font:14px system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
img{max-width:100%}
[hidden]{display:none!important}
.ve-danh-sach{display:inline-flex;align-items:center;gap:6px;font-size:14px;font-weight:600;color:var(--ai);text-decoration:none;padding:6px 0}
.ve-danh-sach{align-self:flex-start;margin-bottom:-24px}
.ticker .sym{white-space:nowrap}
</style>
"""


def bo_the(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def dong_goi(nguon):
    ten = os.path.basename(nguon)
    if not re.fullmatch(r"[A-Z0-9]{3,4}-\d{4}-\d{2}-\d{2}\.html", ten):
        sys.exit(f"Tên file phải dạng MÃ-YYYY-MM-DD.html, nhận được: {ten}")
    s = open(nguon, encoding="utf-8").read()
    moc = s.find('<div class="wrap">')
    if moc < 0:
        sys.exit(f"{ten}: không thấy <div class=\"wrap\"> – file không đúng khung phiếu của skill")
    dau, than = s[:moc], s[moc:]
    than = than.replace('<div class="wrap">',
                        '<div class="wrap">\n  <a class="ve-danh-sach" href="../index.html">← Tất cả phiếu</a>', 1)
    trang = KHUNG_DAU + dau + "\n</head>\n<body>\n" + than + "\n</body>\n</html>\n"
    os.makedirs(THU_MUC_PHIEU, exist_ok=True)
    with open(os.path.join(THU_MUC_PHIEU, ten), "w", encoding="utf-8") as f:
        f.write(trang)
    print(f"Đã đóng gói {ten}")


def doc_thong_tin(duong_dan):
    ten = os.path.basename(duong_dan)
    s = open(duong_dan, encoding="utf-8").read()
    ma_ngay = re.match(r"([A-Z0-9]+)-(\d{4}-\d{2}-\d{2})\.html", ten)
    sym = re.search(r'<span class="sym">([^<]+)</span>\s*<span class="muted small">([^<]+)</span>', s)
    gia = re.search(r'<span class="px">([^<]+)</span>', s)
    tieu_de = re.search(r"<h1>(.*?)</h1>", s, re.S)
    nhan = re.findall(r'<span class="verdict v-(\w+)">(.*?)</span>', s, re.S)
    ket = re.search(r'<div class="bottomline">\s*<p>(.*?)</p>', s, re.S)
    san = sym.group(1).split(":")[0].strip() if sym else ""
    return {
        "ma": ma_ngay.group(1), "ngay": ma_ngay.group(2), "file": "reports/" + ten,
        "san": san, "ten": bo_the(sym.group(2)) if sym else "",
        "gia": bo_the(gia.group(1)) if gia else "", "tieu_de": bo_the(tieu_de.group(1)) if tieu_de else "",
        "nhan": [{"muc": m, "chu": bo_the(c)} for m, c in nhan[:2]],
        "ket_luan": bo_the(ket.group(1)) if ket else "",
    }


def sinh_danh_sach():
    ds = [doc_thong_tin(os.path.join(THU_MUC_PHIEU, f)) for f in sorted(os.listdir(THU_MUC_PHIEU)) if f.endswith(".html")]
    ds.sort(key=lambda x: (x["ngay"], x["ma"]), reverse=True)
    with open(DANH_SACH, "w", encoding="utf-8") as f:
        f.write("// Sinh tự động bởi tools/dong_goi_bao_cao.py – không sửa tay\n")
        f.write("window.DANH_SACH = " + json.dumps(ds, ensure_ascii=False, indent=2) + ";\n")
    print(f"Danh sách: {len(ds)} phiếu → {os.path.relpath(DANH_SACH, GOC)}")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--tat-ca":
        thu_muc = os.path.join(GOC, "bao-cao-goc")
        nguon = [os.path.join(thu_muc, f) for f in sorted(os.listdir(thu_muc)) if f.endswith(".html")]
    else:
        nguon = sys.argv[1:]
    for n in nguon:
        dong_goi(n)
    sinh_danh_sach()


if __name__ == "__main__":
    main()

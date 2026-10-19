#!/usr/bin/env python3
"""Chuẩn hóa BCTC (Excel/CSV xuất từ CafeF, Vietstock, phần mềm CTCK) về JSON cho dinh_gia.py.

Cách dùng:
  py doc_bctc.py FPT_KQKD.xlsx FPT_CDKT.xlsx FPT_LCTT.xlsx --ma FPT --ra tai_chinh_FPT.json
  py doc_bctc.py bctc_quy.csv --ky quy --don-vi trieu --ra tai_chinh_quy.json

- Tự nhận cột kỳ (2021, Năm 2022, Q1/2024, Quý 2-2024...) và đơn vị ("Đơn vị: triệu đồng").
- Quy đổi tiền về TỶ ĐỒNG; EPS giữ nguyên đồng/cp.
- In bảng ÁNH XẠ (trường chuẩn <- dòng gốc) để người phân tích soát lại: tên dòng
  khác nhau giữa các nguồn, nhận nhầm dòng là lỗi phổ biến nhất khi đọc BCTC.
- Kiểm tra cân đối: Tổng tài sản = Nợ phải trả + VCSH; LNST = LNST mẹ + thiểu số.
- Mẫu BCTC ngân hàng/CTCK/bảo hiểm có chỉ tiêu khác: script sẽ báo thiếu trường, khi đó
  nhập tay các chỉ tiêu ngành (xem references/buffett-va-chat-luong.md).
"""
import argparse
import csv
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vn_common import bo_dau, doc_so, ghi_json  # noqa: E402

# trường: (mẫu cần khớp, mẫu loại trừ). So khớp trên chuỗi đã bỏ dấu, viết thường, bỏ số thứ tự đầu dòng.
MAU = {
    "doanh_thu": (r"doanh thu thuan", r"tai chinh"),
    "gia_von": (r"gia von hang ban", r""),
    "loi_nhuan_gop": (r"loi nhuan gop", r""),
    "chi_phi_lai_vay": (r"chi phi lai vay", r"luu chuyen|tien chi"),
    "chi_phi_ban_hang": (r"^chi phi ban hang", r""),
    "chi_phi_qldn": (r"chi phi quan ly doanh nghiep", r""),
    "lntt": (r"tong loi nhuan ke toan truoc thue|^loi nhuan truoc thue", r"chua phan phoi"),
    "lnst": (r"^loi nhuan sau thue thu nhap doanh nghiep$|^loi nhuan sau thue$",
             r"cong ty me|thieu so|khong kiem soat|chua phan phoi"),
    "lnst_me": (r"(loi nhuan sau thue|lnst).*(cong ty me)", r"chua phan phoi"),
    "lnst_thieu_so": (r"(loi nhuan sau thue|lnst).*(khong kiem soat|thieu so)", r""),
    "eps": (r"lai co ban tren co phieu", r"suy giam"),
    "tong_tai_san": (r"^tong cong tai san$|^tong tai san$", r""),
    "tai_san_ngan_han": (r"^tai san ngan han$", r""),
    "tien": (r"^tien va cac khoan tuong duong tien$", r"dau ky|cuoi ky|luu chuyen|anh huong"),
    "dtnh": (r"dau tu tai chinh ngan han", r"du phong|chung khoan kinh doanh$"),
    "phai_thu": (r"^cac khoan phai thu ngan han$|phai thu ngan han cua khach hang", r"du phong|kho doi"),
    "hang_ton_kho": (r"^hang ton kho$", r"du phong|tang|giam"),
    "tscd": (r"^tai san co dinh$", r""),
    "no_ngan_han": (r"^no ngan han$", r""),
    "no_phai_tra": (r"^no phai tra$", r""),
    "vay_ngan_han": (r"vay va no thue tai chinh ngan han|^vay ngan han", r""),
    "vay_dai_han": (r"vay va no thue tai chinh dai han|^vay dai han", r""),
    "von_csh": (r"^von chu so huu$", r""),
    "von_gop": (r"von gop cua chu so huu|^von dau tu cua chu so huu", r"thang du|tien thu|phat hanh|tra lai|mua lai"),
    "loi_nhuan_chua_phan_phoi": (r"loi nhuan sau thue chua phan phoi", r"luy ke|ky nay|ky truoc|nam truoc|nam nay"),
    "loi_ich_thieu_so": (r"loi ich (cua )?co dong (khong kiem soat|thieu so)", r""),
    "cfo": (r"luu chuyen tien thuan tu (cac )?hoat dong kinh doanh", r""),
    "capex": (r"tien chi (de |cho viec )?mua sam,? xay dung (tscd|tai san co dinh)", r""),
    "khau_hao": (r"khau hao (tscd|tai san co dinh)", r""),
    "co_tuc_tien_da_tra": (r"co tuc,? loi nhuan da tra cho chu so huu|^co tuc da tra", r""),
    "tien_thu_phat_hanh_cp": (r"tien thu tu phat hanh co phieu", r""),
}
KHONG_QUY_DOI = {"eps"}
DON_VI = {"dong": 1e-9, "nghin": 1e-6, "ngan": 1e-6, "trieu": 1e-3, "ty": 1.0}


def chuan_nhan(s):
    s = bo_dau(s)
    s = re.sub(r"^[\(\[]?([ivxlc]+|[a-h]|\d+(\.\d+)*)[\.\)\]:\-]\s*", "", s)  # bỏ "I.", "A.", "1.1", "3)"
    s = re.sub(r"^trong do:?\s*", "", s)
    return re.sub(r"\(.*?\)", "", s).strip(" :")


def nhan_ky(o):
    """Nhận diện ô tiêu đề kỳ. Trả về '2024' hoặc '2024Q1' hoặc None."""
    if o is None:
        return None
    if isinstance(o, (int, float)) and 1990 <= o <= 2100 and float(o).is_integer():
        return str(int(o))
    s = bo_dau(o)
    m = re.search(r"(?:q|quy)\s*([1-4])\s*[/\-\s]\s*((?:19|20)\d{2})", s) or re.search(r"((?:19|20)\d{2})\s*[/\-\s]?\s*q([1-4])", s)
    if m:
        a, b = m.groups()
        return f"{b}Q{a}" if len(a) == 1 else f"{a}Q{b}"
    m = re.fullmatch(r"(?:nam\s*)?((?:19|20)\d{2})(?:\s*\(.*\))?", s)
    return m.group(1) if m else None


def doc_bang(duong_dan):
    """Đọc mọi sheet/dòng thành list các list giá trị ô."""
    duoi = os.path.splitext(duong_dan)[1].lower()
    if duoi in (".xlsx", ".xlsm"):
        try:
            import openpyxl
        except ImportError:
            sys.exit("Cần openpyxl để đọc .xlsx: py -m pip install openpyxl (hoặc lưu file thành CSV).")
        wb = openpyxl.load_workbook(duong_dan, data_only=True, read_only=True)
        return [list(r) for ws in wb.worksheets for r in ws.iter_rows(values_only=True)]
    if duoi == ".xls":
        try:
            import xlrd
        except ImportError:
            sys.exit("File .xls đời cũ: mở bằng Excel và Lưu thành .xlsx hoặc .csv rồi chạy lại.")
        wb = xlrd.open_workbook(duong_dan)
        return [sh.row_values(i) for sh in wb.sheets() for i in range(sh.nrows)]
    with open(duong_dan, newline="", encoding="utf-8-sig") as f:
        mau = f.read(4096)
        f.seek(0)
        try:
            kieu = csv.Sniffer().sniff(mau, delimiters=",;\t")
        except csv.Error:
            kieu = csv.excel
        return [r for r in csv.reader(f, kieu)]


def tim_don_vi(bang):
    for r in bang[:15]:
        for o in r:
            if o is None:
                continue
            s = bo_dau(o)
            m = re.search(r"don vi[^a-z]*(?:tinh)?[^a-z]*(trieu|nghin|ngan|ty|dong)", s)
            if m:
                return m.group(1)
    return None


def doc_file(duong_dan, ky_mong_muon):
    bang = doc_bang(duong_dan)
    # dòng tiêu đề = dòng có nhiều ô kỳ nhất
    tot, tieu_de = 0, None
    for i, r in enumerate(bang[:40]):
        ky = [(j, nhan_ky(o)) for j, o in enumerate(r)]
        ky = [(j, k) for j, k in ky if k and (("Q" in k) == (ky_mong_muon == "quy"))]
        if len(ky) > tot:
            tot, tieu_de = len(ky), (i, ky)
    if not tieu_de:
        return None, {}, []
    i0, cot_ky = tieu_de
    so, nguon = {}, []
    for r in bang[i0 + 1:]:
        nhan = next((o for o in r if isinstance(o, str) and re.search(r"[A-Za-zÀ-ỹ]", o)), None)
        if not nhan:
            continue
        nhan_chuan = chuan_nhan(nhan)
        for truong, (khop, loai) in MAU.items():
            if truong in so:
                continue
            if re.search(khop, nhan_chuan) and not (loai and re.search(loai, nhan_chuan)):
                gt = {k: doc_so(r[j]) if j < len(r) else None for j, k in cot_ky}
                if all(v is None for v in gt.values()):
                    continue
                so[truong] = gt
                nguon.append({"truong": truong, "dong_goc": str(nhan).strip(), "file": os.path.basename(duong_dan)})
                break
    return tim_don_vi(bang), so, nguon


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--ma", default="")
    ap.add_argument("--ky", choices=["nam", "quy"], default="nam")
    ap.add_argument("--don-vi", choices=list(DON_VI), help="Bắt buộc nếu file không ghi đơn vị")
    ap.add_argument("--ra", required=True)
    a = ap.parse_args()

    gop, anh_xa, canh_bao = {}, [], []
    for f in a.files:
        dv, so, nguon = doc_file(f, a.ky)
        if not so:
            canh_bao.append(f"{f}: không tìm thấy dòng tiêu đề kỳ ({a.ky}) hoặc không nhận ra chỉ tiêu nào")
            continue
        dv = a.don_vi or dv
        if not dv:
            sys.exit(f"{f}: không thấy dòng 'Đơn vị: ...'. Chạy lại với --don-vi (dong/nghin/trieu/ty).")
        he_so = DON_VI[dv]
        for x in nguon:
            truong = x["truong"]
            if truong in gop:  # đã lấy từ file trước (ví dụ LNTT ở KQKD được ưu tiên hơn LNTT ở LCTT)
                continue
            gop[truong] = {k: (v if truong in KHONG_QUY_DOI or v is None else v * he_so) for k, v in so[truong].items()}
            anh_xa.append(dict(x, don_vi_goc=("đồng/cp, không quy đổi" if truong in KHONG_QUY_DOI else dv)))

    ky_ds = sorted({k for gt in gop.values() for k in gt})
    ket_qua = {}
    for k in ky_ds:
        d = {t: gop[t].get(k) for t in gop if gop[t].get(k) is not None}
        if "vay_ngan_han" in d or "vay_dai_han" in d:
            d["no_vay"] = (d.get("vay_ngan_han") or 0) + (d.get("vay_dai_han") or 0)
        if "tien" in d:
            d["tien_va_dtnh"] = d["tien"] + (d.get("dtnh") or 0)
        if "von_csh" in d and "loi_ich_thieu_so" in d:
            d["von_csh_me"] = d["von_csh"] - d["loi_ich_thieu_so"]
        if "von_gop" in d:
            d["so_cp_trieu"] = d["von_gop"] * 1e9 / 10000 / 1e6
        for t in ("capex", "co_tuc_tien_da_tra"):
            if t in d:
                d[t] = abs(d[t])
        # kiểm tra cân đối
        if all(x in d for x in ("tong_tai_san", "no_phai_tra", "von_csh")):
            lech = d["tong_tai_san"] - d["no_phai_tra"] - d["von_csh"]
            if abs(lech) > 0.005 * d["tong_tai_san"]:
                canh_bao.append(f"{k}: Tổng tài sản lệch Nợ + VCSH {lech:,.1f} tỷ – kiểm tra ánh xạ dòng")
        if all(x in d for x in ("lnst", "lnst_me", "lnst_thieu_so")):
            lech = d["lnst"] - d["lnst_me"] - d["lnst_thieu_so"]
            if abs(lech) > 0.01 * abs(d["lnst"]) + 0.5:
                canh_bao.append(f"{k}: LNST lệch LNST mẹ + thiểu số {lech:,.1f} tỷ")
        ket_qua[k] = d

    thieu = [t for t in ("doanh_thu", "lntt", "lnst_me", "tong_tai_san", "von_csh", "cfo", "capex") if t not in gop]
    if thieu:
        canh_bao.append("Thiếu trường quan trọng: " + ", ".join(thieu) + " (nhập tay hoặc bổ sung file)")
    out = {"ma": a.ma.upper(), "don_vi": "ty_dong", "ky": a.ky,
           ("nam" if a.ky == "nam" else "quy"): ket_qua, "anh_xa": anh_xa, "canh_bao": canh_bao}
    ghi_json(out, a.ra)
    print(f"Đã ghi {a.ra}: {len(ky_ds)} kỳ ({', '.join(ky_ds)}), {len(gop)} trường")
    print("\nÁNH XẠ (soát lại):")
    for x in anh_xa:
        print(f"  {x['truong']:<26} <- {x['dong_goc']}  [{x['file']}, {x['don_vi_goc']}]")
    for cb in canh_bao:
        print(f"CẢNH BÁO: {cb}")
    print("\nBước tiếp: thêm gia_hien_tai, so_cp_luu_hanh_trieu, lnst_ttm_me, kich_ban... "
          "(xem assets/mau_tai_chinh.json) rồi chạy dinh_gia.py")


if __name__ == "__main__":
    main()

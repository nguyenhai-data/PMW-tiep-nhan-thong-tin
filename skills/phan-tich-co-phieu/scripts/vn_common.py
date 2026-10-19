"""Hàm dùng chung cho các script phân tích cổ phiếu Việt Nam.

Chỉ dùng thư viện chuẩn của Python để chạy được ở mọi máy (Windows `py`, macOS, Linux).
"""
import csv
import datetime as dt
import json
import math
import re
import unicodedata

# Biên độ dao động giá trong phiên (tính theo giá tham chiếu) của từng sàn.
BIEN_DO = {"HOSE": 0.07, "HNX": 0.10, "UPCOM": 0.15}

_COT = {
    "date": ("date", "ngay", "time", "tradingdate", "ngay giao dich", "timestamp"),
    "open": ("open", "mo cua", "gia mo cua", "o"),
    "high": ("high", "cao nhat", "gia cao nhat", "h"),
    "low": ("low", "thap nhat", "gia thap nhat", "l"),
    "close": ("close", "dong cua", "gia dong cua", "c", "adj close", "gia dieu chinh"),
    "volume": ("volume", "khoi luong", "kl", "v", "khoi luong khop lenh", "vol"),
}


def bo_dau(s):
    """Bỏ dấu tiếng Việt, viết thường, gộp khoảng trắng."""
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = s.replace("đ", "d").replace("Đ", "D").lower()
    return re.sub(r"\s+", " ", s).strip()


def doc_so(x):
    """Đọc số từ ô Excel/CSV: hỗ trợ 1,234,567 | 1.234.567 | (123) | -1.234,5 | ô trống."""
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return None if (isinstance(x, float) and math.isnan(x)) else float(x)
    s = str(x).strip().replace(" ", "").replace(" ", "")
    if s in ("", "-", "--", "N/A", "n/a", "NaN", "nan"):
        return None
    am = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        nhom = s.split(",")
        s = s.replace(",", "") if all(len(g) == 3 for g in nhom[1:]) else s.replace(",", ".")
    elif "." in s:
        nhom = s.split(".")
        if len(nhom) > 2 or (len(nhom) == 2 and len(nhom[1]) == 3 and len(nhom[0]) <= 3 and nhom[0] not in ("0", "-0")):
            s = s.replace(".", "")
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if am else v


def doc_ngay(x):
    if isinstance(x, (dt.date, dt.datetime)):
        return x.date() if isinstance(x, dt.datetime) else x
    s = str(x).strip()[:10]
    for f in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return dt.datetime.strptime(s, f).date()
        except ValueError:
            pass
    raise ValueError(f"Không đọc được ngày: {x!r}")


def doc_ohlcv(duong_dan):
    """Đọc CSV giá (tên cột tiếng Anh hoặc tiếng Việt). Trả về list dict đã sắp theo ngày tăng dần."""
    with open(duong_dan, newline="", encoding="utf-8-sig") as f:
        rd = csv.DictReader(f)
        map_cot = {}
        for ten in rd.fieldnames or []:
            k = bo_dau(ten)
            for chuan, ten_goi in _COT.items():
                if k in ten_goi and chuan not in map_cot:
                    map_cot[chuan] = ten
        thieu = [c for c in ("date", "open", "high", "low", "close") if c not in map_cot]
        if thieu:
            raise ValueError(f"CSV thiếu cột {thieu}. Cột hiện có: {rd.fieldnames}")
        rows = []
        for r in rd:
            try:
                row = {"date": doc_ngay(r[map_cot["date"]])}
            except ValueError:
                continue
            for c in ("open", "high", "low", "close", "volume"):
                row[c] = doc_so(r.get(map_cot.get(c, ""), None)) if c in map_cot else None
            if row["close"] is None:
                continue
            rows.append(row)
    rows.sort(key=lambda r: r["date"])
    # Bỏ ngày trùng (giữ dòng cuối)
    gon = {}
    for r in rows:
        gon[r["date"]] = r
    return [gon[k] for k in sorted(gon)]


def ghi_ohlcv(rows, duong_dan):
    with open(duong_dan, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "open", "high", "low", "close", "volume"])
        for r in rows:
            w.writerow([r["date"].isoformat(), r["open"], r["high"], r["low"], r["close"], r.get("volume")])


def kiem_tra_ohlcv(rows, san="HOSE", la_chi_so=False):
    """Kiểm tra chất lượng chuỗi giá. Trả về list cảnh báo (chuỗi tiếng Việt).

    Quan trọng nhất: một phiên biến động vượt biên độ sàn gần như chắc chắn là ngày
    giao dịch không hưởng quyền mà dữ liệu CHƯA được điều chỉnh (thưởng cổ phiếu, chia
    cổ tức bằng cổ phiếu, phát hành quyền mua). Khi đó mọi chỉ báo kỹ thuật và mức
    hỗ trợ/kháng cự phía trước ngày đó đều sai.
    """
    canh_bao = []
    bd = BIEN_DO.get(san.upper(), 0.07)
    nghi_chua_dc = []
    for i, r in enumerate(rows):
        o, h, l, c = r["open"], r["high"], r["low"], r["close"]
        if None not in (o, h, l, c):
            if h + 1e-9 < max(o, c) or l - 1e-9 > min(o, c):
                canh_bao.append(f"{r['date']}: OHLC không hợp lệ (high/low không bao open/close)")
        if c is not None and c <= 0:
            canh_bao.append(f"{r['date']}: giá đóng cửa <= 0")
        if i > 0 and not la_chi_so:
            truoc = rows[i - 1]["close"]
            if truoc and c:
                bien = c / truoc - 1
                # cộng 0,5% dung sai làm tròn bước giá
                if abs(bien) > bd + 0.005:
                    nghi_chua_dc.append((r["date"], bien))
    if nghi_chua_dc:
        ds = ", ".join(f"{d} ({b:+.1%})" for d, b in nghi_chua_dc[-10:])
        canh_bao.append(
            f"{len(nghi_chua_dc)} phiên biến động vượt biên độ {san} ±{bd:.0%}: {ds}. "
            "Nhiều khả năng dữ liệu CHƯA điều chỉnh theo sự kiện quyền (hoặc là phiên chào sàn/"
            "giao dịch trở lại). Kiểm tra lịch sự kiện và chạy lại với --su-kien."
        )
    if len(rows) > 2:
        khoang = [(rows[i]["date"] - rows[i - 1]["date"]).days for i in range(1, len(rows))]
        lon = [(rows[i]["date"], k) for i, k in enumerate(khoang, start=1) if k > 10]
        if lon:
            canh_bao.append(
                "Có khoảng trống dữ liệu >10 ngày: "
                + ", ".join(f"trước {d} ({k} ngày)" for d, k in lon[-5:])
            )
    return canh_bao


def dieu_chinh_su_kien(rows, su_kien):
    """Điều chỉnh giá lịch sử theo sự kiện quyền (giá trước ngày GDKHQ được nhân hệ số).

    su_kien: list dict, mỗi dict có:
      - "ngay_gdkhq": "YYYY-MM-DD" (ngày giao dịch không hưởng quyền)
      - "loai": "co_phieu" (thưởng/cổ tức bằng cổ phiếu), "tien" (cổ tức tiền), "quyen_mua"
      - "ty_le": số cổ phiếu mới nhận trên 1 cổ phiếu cũ (thưởng 10:1 -> 0.1; 20:3 -> 0.15)
      - "tien": cổ tức tiền mỗi cổ phiếu (đồng), với loai = "tien"
      - "gia_phat_hanh": giá mua quyền (đồng), với loai = "quyen_mua"
    Công thức (giá tham chiếu ngày GDKHQ của HOSE/HNX):
      co_phieu : P_dc = P / (1 + ty_le)
      tien     : P_dc = P - tien
      quyen_mua: P_dc = (P + ty_le * gia_phat_hanh) / (1 + ty_le)
    Hệ số được tính từ giá đóng cửa phiên liền trước ngày GDKHQ rồi nhân cho toàn bộ
    O/H/L/C trước đó (khối lượng chia ngược lại để giá trị giao dịch không đổi).
    """
    rows = [dict(r) for r in rows]
    for sk in sorted(su_kien, key=lambda s: s["ngay_gdkhq"], reverse=True):
        ngay = doc_ngay(sk["ngay_gdkhq"])
        idx = [i for i, r in enumerate(rows) if r["date"] < ngay]
        if not idx:
            continue
        p = rows[idx[-1]]["close"]
        loai = sk.get("loai", "co_phieu")
        if loai == "co_phieu":
            he_so = 1 / (1 + float(sk["ty_le"]))
        elif loai == "tien":
            he_so = (p - float(sk["tien"])) / p
        elif loai == "quyen_mua":
            tl = float(sk["ty_le"])
            he_so = ((p + tl * float(sk["gia_phat_hanh"])) / (1 + tl)) / p
        else:
            raise ValueError(f"Loại sự kiện không hỗ trợ: {loai}")
        for i in idx:
            for c in ("open", "high", "low", "close"):
                if rows[i][c] is not None:
                    rows[i][c] = rows[i][c] * he_so
            if rows[i].get("volume"):
                rows[i]["volume"] = rows[i]["volume"] / he_so
    return rows


def doc_json(duong_dan):
    with open(duong_dan, encoding="utf-8") as f:
        return json.load(f)


def ghi_json(obj, duong_dan):
    with open(duong_dan, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def fmt_so(x, chu_so=0):
    """Định dạng số kiểu Việt Nam: 1.234.567,8"""
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "–"
    s = f"{x:,.{chu_so}f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


def fmt_pct(x, chu_so=1):
    return "–" if x is None else fmt_so(x * 100, chu_so) + "%"

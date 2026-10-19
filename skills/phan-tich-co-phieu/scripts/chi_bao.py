#!/usr/bin/env python3
"""Chỉ báo kỹ thuật + nến Nhật + kiểm định mẫu nến trên CHÍNH lịch sử của mã.

Cách dùng:
  py chi_bao.py gia_FPT.csv --san HOSE
  py chi_bao.py gia_FPT.csv --chi-so gia_VNINDEX.csv --su-kien su_kien_FPT.json \
      --von 500000000 --rui-ro 0.01 --json ket_qua_ky_thuat.json

Đầu vào: CSV có cột date, open, high, low, close, volume (tên cột tiếng Việt cũng được).
Giá nên là giá ĐÃ ĐIỀU CHỈNH. Nếu chưa, truyền --su-kien để script tự điều chỉnh.

Vì sao có phần "kiểm định": độ tin cậy của mẫu nến khác nhau rất nhiều giữa các mã và
các giai đoạn. Thay vì tin vào tỷ lệ "sách vở", script đo xem sau mỗi lần mẫu nến xuất
hiện trên chính mã này, giá 5/10/20 phiên sau đi thế nào so với một phiên bất kỳ.
"""
import argparse
import datetime as dt
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vn_common import (  # noqa: E402
    dieu_chinh_su_kien, doc_json, doc_ohlcv, fmt_pct, fmt_so, ghi_json, kiem_tra_ohlcv,
)

# ----------------------------------------------------------------- chỉ báo cơ bản

def sma(v, n):
    out, s = [None] * len(v), 0.0
    for i, x in enumerate(v):
        s += x
        if i >= n:
            s -= v[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


def ema(v, n):
    out = [None] * len(v)
    if len(v) < n:
        return out
    k = 2 / (n + 1)
    out[n - 1] = sum(v[:n]) / n
    for i in range(n, len(v)):
        out[i] = v[i] * k + out[i - 1] * (1 - k)
    return out


def rsi(c, n=14):
    """RSI theo Wilder (giống TradingView/StockCharts)."""
    out = [None] * len(c)
    if len(c) <= n:
        return out
    tang = [max(c[i] - c[i - 1], 0) for i in range(1, len(c))]
    giam = [max(c[i - 1] - c[i], 0) for i in range(1, len(c))]
    ag, al = sum(tang[:n]) / n, sum(giam[:n]) / n
    out[n] = 100 if al == 0 else 100 - 100 / (1 + ag / al)
    for i in range(n + 1, len(c)):
        ag = (ag * (n - 1) + tang[i - 1]) / n
        al = (al * (n - 1) + giam[i - 1]) / n
        out[i] = 100 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


def macd(c, nhanh=12, cham=26, tin_hieu=9):
    e1, e2 = ema(c, nhanh), ema(c, cham)
    m = [a - b if a is not None and b is not None else None for a, b in zip(e1, e2)]
    dau = next((i for i, x in enumerate(m) if x is not None), None)
    sig = [None] * len(c)
    if dau is not None:
        e = ema([x for x in m[dau:]], tin_hieu)
        sig[dau:] = e
    hist = [a - b if a is not None and b is not None else None for a, b in zip(m, sig)]
    return m, sig, hist


def atr(rows, n=14):
    tr = [None]
    for i in range(1, len(rows)):
        h, l, pc = rows[i]["high"], rows[i]["low"], rows[i - 1]["close"]
        tr.append(max(h - l, abs(h - pc), abs(l - pc)))
    out = [None] * len(rows)
    if len(rows) <= n:
        return out
    out[n] = sum(tr[1:n + 1]) / n
    for i in range(n + 1, len(rows)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def bollinger(c, n=20, k=2.0):
    mid = sma(c, n)
    up, lo = [None] * len(c), [None] * len(c)
    for i in range(n - 1, len(c)):
        sd = statistics.pstdev(c[i - n + 1:i + 1])
        up[i], lo[i] = mid[i] + k * sd, mid[i] - k * sd
    return mid, up, lo


def obv(rows):
    out, s = [0.0], 0.0
    for i in range(1, len(rows)):
        v = rows[i].get("volume") or 0
        if rows[i]["close"] > rows[i - 1]["close"]:
            s += v
        elif rows[i]["close"] < rows[i - 1]["close"]:
            s -= v
        out.append(s)
    return out

# ----------------------------------------------------------------- nến Nhật

def _hinh(r):
    o, h, l, c = r["open"], r["high"], r["low"], r["close"]
    rng = h - l
    return {
        "o": o, "h": h, "l": l, "c": c, "rng": rng, "body": abs(c - o),
        "tren": h - max(o, c), "duoi": min(o, c) - l, "tang": c > o, "giam": c < o,
        "giua": (o + c) / 2,
    }


def boi_canh(rows, s20, i):
    """Bối cảnh xu hướng TRƯỚC nến i: 'giam' / 'tang' / 'ngang'."""
    j = i - 1
    if j < 6 or s20[j] is None:
        return "ngang"
    c = rows[j]["close"]
    if c < s20[j] and c < rows[j - 5]["close"]:
        return "giam"
    if c > s20[j] and c > rows[j - 5]["close"]:
        return "tang"
    return "ngang"


MAU_NEN = {
    # tên: (hướng, số nến)
    "Búa (hammer)": ("tang", 1),
    "Búa ngược (inverted hammer)": ("tang", 1),
    "Người treo cổ (hanging man)": ("giam", 1),
    "Sao băng (shooting star)": ("giam", 1),
    "Doji": ("trung_tinh", 1),
    "Nhấn chìm tăng (bullish engulfing)": ("tang", 2),
    "Nhấn chìm giảm (bearish engulfing)": ("giam", 2),
    "Đường xuyên (piercing line)": ("tang", 2),
    "Mây đen che phủ (dark cloud cover)": ("giam", 2),
    "Mẹ bồng con tăng (bullish harami)": ("tang", 2),
    "Mẹ bồng con giảm (bearish harami)": ("giam", 2),
    "Sao mai (morning star)": ("tang", 3),
    "Sao hôm (evening star)": ("giam", 3),
    "Ba chàng lính trắng (three white soldiers)": ("tang", 3),
    "Ba con quạ đen (three black crows)": ("giam", 3),
}


def nhan_dien(rows, i, s20, than_tb):
    """Trả về list tên mẫu nến HOÀN THÀNH tại nến i và đúng bối cảnh xu hướng."""
    if i < 3 or rows[i]["open"] is None:
        return []
    a = _hinh(rows[i])
    if a["rng"] <= 0:
        return []
    tb = than_tb[i] or a["body"] or 1e-9
    kq = []
    bc1 = boi_canh(rows, s20, i)
    # 1 nến
    if a["body"] <= 0.1 * a["rng"]:
        kq.append("Doji")
    hinh_bua = a["duoi"] >= 2 * a["body"] and a["duoi"] >= 0.6 * a["rng"] and a["tren"] <= 0.15 * a["rng"]
    hinh_nguoc = a["tren"] >= 2 * a["body"] and a["tren"] >= 0.6 * a["rng"] and a["duoi"] <= 0.15 * a["rng"]
    if hinh_bua and bc1 == "giam":
        kq.append("Búa (hammer)")
    if hinh_bua and bc1 == "tang":
        kq.append("Người treo cổ (hanging man)")
    if hinh_nguoc and bc1 == "giam":
        kq.append("Búa ngược (inverted hammer)")
    if hinh_nguoc and bc1 == "tang":
        kq.append("Sao băng (shooting star)")
    # 2 nến
    b = _hinh(rows[i - 1])
    bc2 = boi_canh(rows, s20, i - 1)
    dai_b = b["body"] >= (than_tb[i - 1] or b["body"]) and b["rng"] > 0 and b["body"] >= 0.5 * b["rng"]
    if b["giam"] and a["tang"] and a["o"] <= b["c"] and a["c"] >= b["o"] and a["body"] > b["body"] and bc2 == "giam":
        kq.append("Nhấn chìm tăng (bullish engulfing)")
    if b["tang"] and a["giam"] and a["o"] >= b["c"] and a["c"] <= b["o"] and a["body"] > b["body"] and bc2 == "tang":
        kq.append("Nhấn chìm giảm (bearish engulfing)")
    # Thị trường VN hiếm khi mở cửa nhảy giá, nên chỉ yêu cầu mở cửa <= đóng cửa phiên trước
    if dai_b and b["giam"] and a["tang"] and a["o"] <= b["c"] and b["giua"] < a["c"] < b["o"] and bc2 == "giam":
        kq.append("Đường xuyên (piercing line)")
    if dai_b and b["tang"] and a["giam"] and a["o"] >= b["c"] and b["o"] < a["c"] < b["giua"] and bc2 == "tang":
        kq.append("Mây đen che phủ (dark cloud cover)")
    if dai_b and b["giam"] and a["tang"] and a["o"] >= b["c"] and a["c"] <= b["o"] and a["body"] <= 0.6 * b["body"] and bc2 == "giam":
        kq.append("Mẹ bồng con tăng (bullish harami)")
    if dai_b and b["tang"] and a["giam"] and a["o"] <= b["c"] and a["c"] >= b["o"] and a["body"] <= 0.6 * b["body"] and bc2 == "tang":
        kq.append("Mẹ bồng con giảm (bearish harami)")
    # 3 nến
    x = _hinh(rows[i - 2])
    bc3 = boi_canh(rows, s20, i - 2)
    dai_x = x["rng"] > 0 and x["body"] >= (than_tb[i - 2] or x["body"]) and x["body"] >= 0.5 * x["rng"]
    if dai_x and x["giam"] and b["body"] <= 0.3 * x["body"] and b["giua"] <= x["c"] + 0.25 * x["body"] \
            and a["tang"] and a["c"] > x["giua"] and bc3 == "giam":
        kq.append("Sao mai (morning star)")
    if dai_x and x["tang"] and b["body"] <= 0.3 * x["body"] and b["giua"] >= x["c"] - 0.25 * x["body"] \
            and a["giam"] and a["c"] < x["giua"] and bc3 == "tang":
        kq.append("Sao hôm (evening star)")
    ba = [x, b, a]
    if all(n["tang"] and n["body"] >= 0.5 * tb and n["tren"] <= 0.3 * max(n["body"], 1e-9) for n in ba) \
            and x["c"] < b["c"] < a["c"] and x["o"] <= b["o"] <= x["c"] and b["o"] <= a["o"] <= b["c"] and bc3 != "tang":
        kq.append("Ba chàng lính trắng (three white soldiers)")
    if all(n["giam"] and n["body"] >= 0.5 * tb and n["duoi"] <= 0.3 * max(n["body"], 1e-9) for n in ba) \
            and x["c"] > b["c"] > a["c"] and x["c"] <= b["o"] <= x["o"] and b["c"] <= a["o"] <= b["o"] and bc3 != "giam":
        kq.append("Ba con quạ đen (three black crows)")
    return kq


def than_trung_binh(rows, n=10):
    out = [None] * len(rows)
    bodies = [abs(r["close"] - r["open"]) if r["open"] is not None else 0 for r in rows]
    for i in range(n, len(rows)):
        out[i] = sum(bodies[i - n:i]) / n
    return out


def gop_tuan(rows):
    tuan = {}
    for r in rows:
        k = r["date"].isocalendar()[:2]
        t = tuan.setdefault(k, {"date": r["date"], "open": r["open"], "high": r["high"], "low": r["low"],
                                "close": r["close"], "volume": 0})
        t["high"], t["low"] = max(t["high"], r["high"]), min(t["low"], r["low"])
        t["close"], t["date"] = r["close"], r["date"]
        t["volume"] += r.get("volume") or 0
    return [tuan[k] for k in sorted(tuan)]

# ----------------------------------------------------------------- kiểm định mẫu nến

def kiem_dinh(rows, tin_hieu, ky=(5, 10, 20)):
    """So sánh lợi suất sau mẫu nến với lợi suất của một phiên bất kỳ (nền)."""
    c = [r["close"] for r in rows]
    nen = {}
    for h in ky:
        ls = [c[i + h] / c[i] - 1 for i in range(len(c) - h)]
        nen[h] = {"tb": statistics.mean(ls) if ls else None,
                  "ty_le_tang": sum(1 for x in ls if x > 0) / len(ls) if ls else None}
    kq = {}
    for ten, ds in tin_hieu.items():
        huong = MAU_NEN[ten][0]
        muc = {"huong": huong, "so_lan": len(ds)}
        for h in ky:
            ls = [c[i + h] / c[i] - 1 for i in ds if i + h < len(c)]
            if not ls:
                muc[f"{h}p"] = None
                continue
            tb = statistics.mean(ls)
            if huong == "giam":
                trung = sum(1 for x in ls if x < 0) / len(ls)
                nen_trung = 1 - nen[h]["ty_le_tang"]
                loi_the = nen[h]["tb"] - tb
            else:
                trung = sum(1 for x in ls if x > 0) / len(ls)
                nen_trung = nen[h]["ty_le_tang"]
                loi_the = tb - nen[h]["tb"]
            muc[f"{h}p"] = {"n": len(ls), "loi_suat_tb": tb, "trung_vi": statistics.median(ls),
                            "ty_le_dung": trung, "ty_le_dung_nen": nen_trung, "loi_the_so_voi_nen": loi_the}
        n20 = (muc.get("10p") or {}).get("n", 0)
        muc["danh_gia"] = ("Không đủ mẫu (<15 lần) – không dùng làm căn cứ" if n20 < 15 else
                           "Có lợi thế trên mã này" if (muc["10p"]["loi_the_so_voi_nen"] > 0.005 and
                                                         muc["10p"]["ty_le_dung"] > muc["10p"]["ty_le_dung_nen"] + 0.05)
                           else "Không tốt hơn ngẫu nhiên trên mã này")
        kq[ten] = muc
    return {"nen": nen, "mau": kq}

# ----------------------------------------------------------------- hỗ trợ / kháng cự

def dinh_day(rows, k=5):
    dinh, day = [], []
    for i in range(k, len(rows) - k):
        cua_so = rows[i - k:i + k + 1]
        if rows[i]["high"] == max(r["high"] for r in cua_so):
            dinh.append(i)
        if rows[i]["low"] == min(r["low"] for r in cua_so):
            day.append(i)
    return dinh, day


def gom_muc(rows, dinh, day, dung_sai=0.015, so_phien=250):
    bat_dau = max(0, len(rows) - so_phien)
    diem = [(rows[i]["high"], i, "đỉnh") for i in dinh if i >= bat_dau] + \
           [(rows[i]["low"], i, "đáy") for i in day if i >= bat_dau]
    diem.sort()
    cum = []
    for gia, i, loai in diem:
        if cum and gia <= cum[-1]["gia_tb"] * (1 + dung_sai):
            cm = cum[-1]
            cm["ds"].append((gia, i, loai))
            cm["gia_tb"] = statistics.mean(g for g, _, _ in cm["ds"])
        else:
            cum.append({"gia_tb": gia, "ds": [(gia, i, loai)]})
    out = []
    for cm in cum:
        cuoi = max(i for _, i, _ in cm["ds"])
        out.append({"muc": cm["gia_tb"], "so_lan_cham": len(cm["ds"]),
                    "lan_cuoi": rows[cuoi]["date"].isoformat(),
                    "loai": ", ".join(sorted({l for _, _, l in cm["ds"]}))})
    return out

# ----------------------------------------------------------------- tổng hợp

def doi_xung(rows_ma, rows_cs):
    """Sức mạnh tương đối so với chỉ số (theo ngày trùng nhau)."""
    cs = {r["date"]: r["close"] for r in rows_cs}
    chung = [(r["date"], r["close"], cs[r["date"]]) for r in rows_ma if r["date"] in cs]
    kq = {}
    for h in (20, 60, 120, 250):
        if len(chung) > h:
            a = chung[-1][1] / chung[-1 - h][1] - 1
            b = chung[-1][2] / chung[-1 - h][2] - 1
            kq[f"{h}p"] = {"ma": a, "chi_so": b, "chenh_lech": a - b}
    return kq


def phan_tich(rows, rows_cs=None, von=None, rui_ro=None, he_so_atr=2.0):
    c = [r["close"] for r in rows]
    n = len(rows)
    s20, s50, s200 = sma(c, 20), sma(c, 50), sma(c, 200)
    r14 = rsi(c)
    m, sg, hist = macd(c)
    a14 = atr(rows)
    bm, bu, bl = bollinger(c)
    vols = [r.get("volume") or 0 for r in rows]
    v20 = sma(vols, 20)
    ob = obv(rows)
    i = n - 1
    cuoi = rows[i]

    def tl(a, b):
        return None if a is None or b in (None, 0) else a / b - 1

    # xu hướng
    doc200 = tl(s200[i], s200[i - 20]) if i >= 220 and s200[i - 20] else None
    if s200[i] and s50[i] and c[i] > s50[i] > s200[i] and (doc200 or 0) > 0:
        xh = "Tăng (giá > MA50 > MA200, MA200 dốc lên)"
    elif s200[i] and s50[i] and c[i] < s50[i] < s200[i] and (doc200 or 0) < 0:
        xh = "Giảm (giá < MA50 < MA200, MA200 dốc xuống)"
    else:
        xh = "Đi ngang / chuyển tiếp"
    cat = None
    for j in range(i, 200, -1):
        if s50[j] and s200[j] and s50[j - 1] and s200[j - 1]:
            if (s50[j] - s200[j]) * (s50[j - 1] - s200[j - 1]) < 0:
                cat = {"ngay": rows[j]["date"].isoformat(),
                       "loai": "Giao cắt vàng (MA50 cắt lên MA200)" if s50[j] > s200[j] else "Giao cắt tử thần (MA50 cắt xuống MA200)"}
                break
    dinh, day = dinh_day(rows)
    hh = len(dinh) >= 2 and rows[dinh[-1]]["high"] > rows[dinh[-2]]["high"]
    hl = len(day) >= 2 and rows[day[-1]]["low"] > rows[day[-2]]["low"]
    cau_truc = ("Đỉnh cao dần, đáy cao dần" if hh and hl else "Đỉnh thấp dần, đáy thấp dần" if not hh and not hl
                else "Hỗn hợp (một chiều cao dần, một chiều thấp dần)")
    # Đỉnh/đáy chỉ được xác nhận sau 5 phiên, nên kiểm tra thêm giá hiện tại so với chúng
    if day and c[i] < rows[day[-1]]["low"]:
        cau_truc += f"; giá hiện tại đã THỦNG đáy xác nhận gần nhất {fmt_so(rows[day[-1]]['low'])} ({rows[day[-1]]['date']})"
    if dinh and c[i] > rows[dinh[-1]]["high"]:
        cau_truc += f"; giá hiện tại đã VƯỢT đỉnh xác nhận gần nhất {fmt_so(rows[dinh[-1]]['high'])} ({rows[dinh[-1]]['date']})"

    # chuỗi phiên (quy tắc Sakata: ~8–10 lần lập giá mới liên tiếp thì đã quá đà)
    chuoi_giam = 0
    for j in range(i, 0, -1):
        if c[j] < c[j - 1]:
            chuoi_giam += 1
        else:
            break
    chuoi_tang = 0
    for j in range(i, 0, -1):
        if c[j] > c[j - 1]:
            chuoi_tang += 1
        else:
            break
    khong_tang = 0
    for j in range(i, 0, -1):
        if c[j] <= c[j - 1]:
            khong_tang += 1
        else:
            break
    day_moi = sum(1 for j in range(max(20, i - 14), i + 1)
                  if rows[j]["low"] < min(r["low"] for r in rows[j - 20:j]))
    dinh_moi = sum(1 for j in range(max(20, i - 14), i + 1)
                   if rows[j]["high"] > max(r["high"] for r in rows[j - 20:j]))

    # nến
    than_tb = than_trung_binh(rows)
    tin_hieu = {}
    gan_day = []
    for j in range(3, n):
        for ten in nhan_dien(rows, j, s20, than_tb):
            tin_hieu.setdefault(ten, []).append(j)
            if j >= n - 10:
                gan_day.append((j, ten))
    xac_nhan = []
    for j, ten in gan_day:
        huong = MAU_NEN[ten][0]
        sau = rows[j + 1] if j + 1 < n else None
        kl_tot = v20[j] and (rows[j].get("volume") or 0) >= 1.2 * v20[j]
        if sau is None:
            tt = "Chờ phiên sau xác nhận"
        elif huong == "tang":
            tt = "Đã xác nhận (đóng cửa vượt đỉnh nến tín hiệu)" if sau["close"] > rows[j]["high"] else "Chưa xác nhận"
        elif huong == "giam":
            tt = "Đã xác nhận (đóng cửa dưới đáy nến tín hiệu)" if sau["close"] < rows[j]["low"] else "Chưa xác nhận"
        else:
            tt = "Trung tính – chỉ báo do dự"
        xac_nhan.append({"ngay": rows[j]["date"].isoformat(), "mau": ten, "huong": huong,
                         "kl_vuot_tb20_20pct": bool(kl_tot), "trang_thai": tt})
    kd = kiem_dinh(rows, tin_hieu)

    tuan = gop_tuan(rows)
    s20t = sma([r["close"] for r in tuan], 20)
    ttb = than_trung_binh(tuan)
    nen_tuan = [{"tuan_ket_thuc": tuan[j]["date"].isoformat(), "mau": ten}
                for j in range(max(3, len(tuan) - 6), len(tuan)) for ten in nhan_dien(tuan, j, s20t, ttb)]

    # mức giá
    muc = gom_muc(rows, dinh, day)
    gia = c[i]
    ho_tro = sorted([m_ for m_ in muc if m_["muc"] < gia], key=lambda x: -x["muc"])[:4]
    khang_cu = sorted([m_ for m_ in muc if m_["muc"] > gia], key=lambda x: x["muc"])[:4]
    nam = rows[max(0, n - 250):]
    cao52, thap52 = max(r["high"] for r in nam), min(r["low"] for r in nam)
    ath = max(r["high"] for r in rows)

    def ls(h):
        return tl(c[i], c[i - h]) if i >= h else None

    kq = {
        "ngay_cuoi": cuoi["date"].isoformat(), "gia_dong_cua": gia,
        "so_phien_du_lieu": n,
        "loi_suat": {"1T": ls(5), "1Th": ls(21), "3Th": ls(63), "6Th": ls(126), "1N": ls(250)},
        "xu_huong": {"phan_loai": xh, "cau_truc_dinh_day": cau_truc,
                     "gia_so_voi_MA20": tl(gia, s20[i]), "gia_so_voi_MA50": tl(gia, s50[i]),
                     "gia_so_voi_MA200": tl(gia, s200[i]), "do_doc_MA200_20p": doc200,
                     "MA20": s20[i], "MA50": s50[i], "MA200": s200[i], "giao_cat_gan_nhat": cat},
        "dong_luc": {"RSI14": r14[i], "MACD": m[i], "MACD_tin_hieu": sg[i], "MACD_histogram": hist[i],
                     "histogram_dang_tang": (hist[i] is not None and hist[i - 1] is not None and hist[i] > hist[i - 1]),
                     "BB_tren": bu[i], "BB_duoi": bl[i],
                     "vi_tri_trong_BB": (gia - bl[i]) / (bu[i] - bl[i]) if bu[i] and bl[i] and bu[i] > bl[i] else None},
        "bien_dong": {"ATR14": a14[i], "ATR_pct": a14[i] / gia if a14[i] else None},
        "khoi_luong": {"KL_phien_cuoi": cuoi.get("volume"), "KL_TB20": v20[i],
                       "ty_le_KL_so_TB20": (cuoi.get("volume") or 0) / v20[i] if v20[i] else None,
                       "OBV_20p_xu_huong": "tăng" if ob[i] > ob[max(0, i - 20)] else "giảm"},
        "sakata": {"chuoi_phien_giam_lien_tiep": chuoi_giam, "chuoi_phien_tang_lien_tiep": chuoi_tang,
                   "chuoi_phien_khong_tang": khong_tang,
                   "so_lan_lap_day_20p_moi_trong_15_phien": day_moi,
                   "so_lan_lap_dinh_20p_moi_trong_15_phien": dinh_moi},
        "muc_gia": {"ho_tro": ho_tro, "khang_cu": khang_cu, "cao_52_tuan": cao52, "thap_52_tuan": thap52,
                    "dinh_lich_su_trong_du_lieu": ath, "cach_dinh_lich_su": tl(gia, ath),
                    "cach_cao_52_tuan": tl(gia, cao52), "cach_thap_52_tuan": tl(gia, thap52)},
        "nen_gan_day": xac_nhan, "nen_tuan_gan_day": nen_tuan, "kiem_dinh_mau_nen": kd,
    }
    if rows_cs:
        kq["suc_manh_tuong_doi"] = doi_xung(rows, rows_cs)
    if a14[i]:
        cat_lo = gia - he_so_atr * a14[i]
        kq["quan_tri_rui_ro"] = {"diem_cat_lo_goi_y": cat_lo, "cach_gia": tl(cat_lo, gia),
                                 "ghi_chu": f"Cắt lỗ = giá - {he_so_atr} x ATR14; điều chỉnh về dưới hỗ trợ gần nhất nếu hợp lý."}
        if von and rui_ro:
            r1 = gia - cat_lo
            so_cp = int((von * rui_ro / r1) // 100 * 100) if r1 > 0 else 0
            kq["quan_tri_rui_ro"].update({"so_cp_toi_da_lo_100": so_cp, "gia_tri_vi_the": so_cp * gia,
                                          "ty_trong_von": so_cp * gia / von, "lo_toi_da_neu_cham_cat_lo": so_cp * r1})
    return kq


def in_tom_tat(kq, canh_bao):
    p = print
    p(f"# Kỹ thuật – phiên {kq['ngay_cuoi']} – giá {fmt_so(kq['gia_dong_cua'])}")
    for cb in canh_bao:
        p(f"> CẢNH BÁO DỮ LIỆU: {cb}")
    xh = kq["xu_huong"]
    p(f"\n## Xu hướng\n- {xh['phan_loai']}; {xh['cau_truc_dinh_day']}")
    p(f"- Giá so với MA20/50/200: {fmt_pct(xh['gia_so_voi_MA20'])} / {fmt_pct(xh['gia_so_voi_MA50'])} / {fmt_pct(xh['gia_so_voi_MA200'])}")
    if xh["giao_cat_gan_nhat"]:
        p(f"- {xh['giao_cat_gan_nhat']['loai']} ngày {xh['giao_cat_gan_nhat']['ngay']}")
    ls = kq["loi_suat"]
    p("- Lợi suất 1T/1Th/3Th/6Th/1N: " + " / ".join(fmt_pct(ls[k]) for k in ("1T", "1Th", "3Th", "6Th", "1N")))
    if "suc_manh_tuong_doi" in kq:
        p("- So với chỉ số (chênh lệch lợi suất): " + ", ".join(
            f"{k}: {fmt_pct(v['chenh_lech'])}" for k, v in kq["suc_manh_tuong_doi"].items()))
    dl = kq["dong_luc"]
    p(f"\n## Động lượng\n- RSI14 {fmt_so(dl['RSI14'], 1)}; MACD hist {fmt_so(dl['MACD_histogram'], 2)} "
      f"({'đang tăng' if dl['histogram_dang_tang'] else 'đang giảm'}); vị trí trong Bollinger {fmt_pct(dl['vi_tri_trong_BB'], 0)}")
    kl = kq["khoi_luong"]
    p(f"- KL phiên cuối = {fmt_so(kl['ty_le_KL_so_TB20'], 2)} lần TB20; OBV 20 phiên {kl['OBV_20p_xu_huong']}")
    sk = kq["sakata"]
    p(f"\n## Đếm phiên (Sakata)\n- Giảm liên tiếp {sk['chuoi_phien_giam_lien_tiep']}, không tăng liên tiếp "
      f"{sk['chuoi_phien_khong_tang']}, tăng liên tiếp {sk['chuoi_phien_tang_lien_tiep']}; "
      f"lập đáy 20 phiên mới {sk['so_lan_lap_day_20p_moi_trong_15_phien']} lần / 15 phiên")
    mg = kq["muc_gia"]
    p("\n## Mức giá")
    p("- Kháng cự: " + ("; ".join(f"{fmt_so(x['muc'])} ({x['so_lan_cham']} lần, {x['lan_cuoi']})" for x in mg["khang_cu"]) or "–"))
    p("- Hỗ trợ: " + ("; ".join(f"{fmt_so(x['muc'])} ({x['so_lan_cham']} lần, {x['lan_cuoi']})" for x in mg["ho_tro"]) or "–"))
    p(f"- Cao/thấp 52 tuần: {fmt_so(mg['cao_52_tuan'])} / {fmt_so(mg['thap_52_tuan'])}; cách đỉnh dữ liệu {fmt_pct(mg['cach_dinh_lich_su'])}")
    p("\n## Nến 10 phiên gần nhất")
    if not kq["nen_gan_day"]:
        p("- Không có mẫu nến đúng bối cảnh.")
    for x in kq["nen_gan_day"]:
        kd = kq["kiem_dinh_mau_nen"]["mau"].get(x["mau"], {})
        k10 = kd.get("10p") or {}
        p(f"- {x['ngay']}: {x['mau']} – {x['trang_thai']}; KL vượt TB20 20%: {'có' if x['kl_vuot_tb20_20pct'] else 'không'}; "
          f"lịch sử mã: {kd.get('so_lan', 0)} lần, đúng hướng sau 10 phiên {fmt_pct(k10.get('ty_le_dung'), 0)} "
          f"(nền {fmt_pct(k10.get('ty_le_dung_nen'), 0)}) → {kd.get('danh_gia', '')}")
    if kq["nen_tuan_gan_day"]:
        p("- Nến tuần: " + "; ".join(f"{x['tuan_ket_thuc']}: {x['mau']}" for x in kq["nen_tuan_gan_day"]))
    if "quan_tri_rui_ro" in kq:
        q = kq["quan_tri_rui_ro"]
        p(f"\n## Rủi ro\n- Cắt lỗ gợi ý {fmt_so(q['diem_cat_lo_goi_y'])} ({fmt_pct(q['cach_gia'])}); ATR14 {fmt_pct(kq['bien_dong']['ATR_pct'])}/phiên")
        if "so_cp_toi_da_lo_100" in q:
            p(f"- Khối lượng tối đa: {fmt_so(q['so_cp_toi_da_lo_100'])} cp ({fmt_pct(q['ty_trong_von'])} vốn), lỗ tối đa {fmt_so(q['lo_toi_da_neu_cham_cat_lo'])} đ")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--chi-so", help="CSV giá chỉ số (VNINDEX) để tính sức mạnh tương đối")
    ap.add_argument("--san", default="HOSE", choices=["HOSE", "HNX", "UPCOM"])
    ap.add_argument("--su-kien", help="JSON danh sách sự kiện quyền để điều chỉnh giá")
    ap.add_argument("--von", type=float, help="Tổng vốn (đồng) để tính khối lượng vị thế")
    ap.add_argument("--rui-ro", type=float, help="Tỷ lệ vốn chấp nhận mất mỗi lệnh, ví dụ 0.01")
    ap.add_argument("--he-so-atr", type=float, default=2.0)
    ap.add_argument("--json", help="Ghi kết quả đầy đủ ra file JSON")
    a = ap.parse_args()
    rows = doc_ohlcv(a.csv)
    if a.su_kien:
        rows = dieu_chinh_su_kien(rows, doc_json(a.su_kien))
    if len(rows) < 60:
        sys.exit("Cần ít nhất 60 phiên (khuyến nghị >= 500 phiên để kiểm định mẫu nến).")
    if any(r["open"] is None or r["high"] is None or r["low"] is None for r in rows):
        sys.exit("Dữ liệu thiếu open/high/low: không thể đọc nến. Chỉ có giá đóng cửa thì đừng gọi tên mẫu nến.")
    canh_bao = kiem_tra_ohlcv(rows, a.san)
    rows_cs = doc_ohlcv(a.chi_so) if a.chi_so else None
    kq = phan_tich(rows, rows_cs, a.von, a.rui_ro, a.he_so_atr)
    kq["canh_bao_du_lieu"] = canh_bao
    kq["tao_luc"] = dt.datetime.now().isoformat(timespec="seconds")
    in_tom_tat(kq, canh_bao)
    if a.json:
        ghi_json(kq, a.json)
        print(f"\nĐã ghi {a.json}")


if __name__ == "__main__":
    main()

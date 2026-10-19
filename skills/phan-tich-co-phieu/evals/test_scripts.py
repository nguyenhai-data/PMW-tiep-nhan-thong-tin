import sys, os, random, datetime as dt, json, csv, tempfile
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
sys.path.insert(0, S)
import chi_bao as cb, vn_common as vc, lay_gia as lg
ok = lambda c, m: print(("PASS " if c else "FAIL ") + m) or (c or sys.exit(1))

# 1) RSI theo ví dụ StockCharts
closes = [44.34,44.09,44.15,43.61,44.33,44.83,45.10,45.42,45.84,46.08,45.89,46.03,45.61,46.28,46.28,46.00,46.03,46.41,46.22,45.64]
r = cb.rsi(closes)
exp = [70.53, 66.32, 66.55, 69.41, 66.36, 57.97]
ok(all(abs(a-b) < 0.1 for a, b in zip(r[14:20], exp)), f"RSI Wilder khớp StockCharts (sai số do bảng gốc làm tròn TB lãi/lỗ) {[round(x,2) for x in r[14:20]]}")

# 2) Doc so kieu VN
ok(vc.doc_so("1.234.567") == 1234567 and vc.doc_so("(1,234)") == -1234 and vc.doc_so("57.1") == 57.1 and vc.doc_so("1.234,5") == 1234.5, "doc_so định dạng VN")

# 3) Chuỗi giả lập + nến cài sẵn
random.seed(7)
rows, p, d = [], 50000.0, dt.date(2022, 1, 3)
while len(rows) < 700:
    if d.weekday() < 5:
        o = p * (1 + random.uniform(-0.01, 0.01)); c = o * (1 + random.uniform(-0.025, 0.025))
        h = max(o, c) * (1 + random.uniform(0, 0.01)); l = min(o, c) * (1 - random.uniform(0, 0.01))
        rows.append({"date": d, "open": o, "high": h, "low": l, "close": c, "volume": random.randint(1000000, 3000000)}); p = c
    d += dt.timedelta(days=1)
# ép xu hướng giảm 8 phiên rồi một nến búa
for k in range(8):
    prev = rows[-1]["close"]; o = prev * 0.995; c = o * 0.985
    rows.append({"date": rows[-1]["date"] + dt.timedelta(days=1), "open": o, "high": o * 1.002, "low": c * 0.998, "close": c, "volume": 2e6})
prev = rows[-1]["close"]; o = prev * 0.998; c = o * 1.004; l = o * 0.96; h = c * 1.001
rows.append({"date": rows[-1]["date"] + dt.timedelta(days=1), "open": o, "high": h, "low": l, "close": c, "volume": 5e6})
s20 = cb.sma([x["close"] for x in rows], 20); ttb = cb.than_trung_binh(rows)
ok("Búa (hammer)" in cb.nhan_dien(rows, len(rows)-1, s20, ttb), "nhận diện nến Búa trong xu hướng giảm")
# nhấn chìm tăng
prev = rows[-1]; a = {"date": prev["date"] + dt.timedelta(days=1)}
b = dict(open=prev["close"]*0.999, close=prev["close"]*0.985); b.update(high=b["open"]*1.001, low=b["close"]*0.999, volume=2e6, date=a["date"])
rows2 = rows[:-1] + [ {**rows[-2]} ]
# dựng lại: giảm mạnh rồi nến tăng bao trùm
base = rows[:-1]
x = base[-1]; o1 = x["close"]; c1 = o1 * 0.98
base.append({"date": x["date"] + dt.timedelta(days=1), "open": o1, "high": o1*1.001, "low": c1*0.999, "close": c1, "volume": 2e6})
o2 = c1 * 0.998; c2 = o1 * 1.004
base.append({"date": x["date"] + dt.timedelta(days=2), "open": o2, "high": c2*1.002, "low": o2*0.998, "close": c2, "volume": 6e6})
s20 = cb.sma([x["close"] for x in base], 20); ttb = cb.than_trung_binh(base)
ok("Nhấn chìm tăng (bullish engulfing)" in cb.nhan_dien(base, len(base)-1, s20, ttb), "nhận diện Nhấn chìm tăng")

# 4) Điều chỉnh thưởng cổ phiếu 10:1 -> hết cảnh báo vượt biên độ
ev_rows = [dict(r) for r in rows[:300]]
gd = ev_rows[200]["date"]
for r_ in ev_rows[200:]:
    for k in ("open", "high", "low", "close"): r_[k] = r_[k] / 1.1
cb_truoc = vc.kiem_tra_ohlcv(ev_rows, "HOSE")
adj = vc.dieu_chinh_su_kien(ev_rows, [{"ngay_gdkhq": gd.isoformat(), "loai": "co_phieu", "ty_le": 0.1}])
cb_sau = vc.kiem_tra_ohlcv(adj, "HOSE")
ok(any("vượt biên độ" in x for x in cb_truoc) and not any("vượt biên độ" in x for x in cb_sau), "phát hiện & điều chỉnh sự kiện thưởng 10:1")

# 5) Đọc định dạng UDF (giá theo nghìn đồng)
pl = {"s": "ok", "t": [1760313600, 1760400000], "o": [56.3, 56.3], "h": [57.3, 57.7], "l": [56.1, 55.8], "c": [56.3, 57.1], "v": [2660000, 6775400]}
u = lg.doc_udf(pl)
ok(u[-1]["close"] == 57100 and u[-1]["low"] == 55800 and u[0]["date"] < u[1]["date"], f"doc_udf quy đổi nghìn đồng → đồng, ngày {u[0]['date']}, {u[1]['date']}")

# 6) Ghi CSV và chạy chi_bao end-to-end
path = os.path.join(tempfile.mkdtemp(), "gia_gia_lap.csv"); vc.ghi_ohlcv(base, path)
kq = cb.phan_tich(vc.doc_ohlcv(path), von=500_000_000, rui_ro=0.01)
ok(kq["nen_gan_day"] and "kiem_dinh_mau_nen" in kq and kq["quan_tri_rui_ro"]["so_cp_toi_da_lo_100"] % 100 == 0, "chi_bao chạy trọn, có nến gần đây, khối lượng làm tròn lô 100")
print("so mau nen kiem dinh:", {k: v["so_lan"] for k, v in kq["kiem_dinh_mau_nen"]["mau"].items()})

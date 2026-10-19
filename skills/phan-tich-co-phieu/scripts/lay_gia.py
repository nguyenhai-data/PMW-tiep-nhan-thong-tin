#!/usr/bin/env python3
"""Tải giá lịch sử (OHLCV ngày) của cổ phiếu/chỉ số Việt Nam, thử lần lượt nhiều nguồn.

Cách dùng:
  py lay_gia.py FPT --tu 2018-01-01 --ra gia_FPT.csv
  py lay_gia.py VNINDEX --chi-so --ra gia_VNINDEX.csv
  py lay_gia.py FPT --nguon entrade,vndirect --su-kien su_kien_FPT.json --ra gia_FPT_dc.csv

Nguồn (API công khai dạng TradingView, có thể đổi bất kỳ lúc nào):
  vndirect : dchart-api.vndirect.com.vn
  entrade  : services.entrade.com.vn (DNSE)
  vps      : histdatafeed.vps.com.vn

Script không dùng thư viện vnstock (gói này trên PyPI từng bị gắn trạng thái
"quarantined"); chỉ dùng thư viện chuẩn để chạy ở mọi máy.

Sau khi tải, script kiểm tra: phiên vượt biên độ sàn (dấu hiệu dữ liệu chưa điều chỉnh
theo sự kiện quyền), OHLC sai logic, khoảng trống dữ liệu. ĐỌC CẢNH BÁO trước khi phân tích.
"""
import argparse
import datetime as dt
import json
import os
import ssl
import statistics
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vn_common import dieu_chinh_su_kien, doc_json, ghi_ohlcv, kiem_tra_ohlcv  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "application/json"}


def _url(nguon, ma, tu, den, chi_so):
    if nguon == "vndirect":
        return f"https://dchart-api.vndirect.com.vn/dchart/history?resolution=D&symbol={ma}&from={tu}&to={den}"
    if nguon == "entrade":
        loai = "index" if chi_so else "stock"
        return f"https://services.entrade.com.vn/chart-api/v2/ohlcs/{loai}?from={tu}&to={den}&symbol={ma}&resolution=1D"
    if nguon == "vps":
        return f"https://histdatafeed.vps.com.vn/tradingview/history?symbol={ma}&resolution=D&from={tu}&to={den}"
    raise ValueError(nguon)


def tai_json(url, timeout=20):
    ctx = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or None)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return json.loads(r.read().decode("utf-8"))


def doc_udf(payload, chi_so=False):
    """Đọc định dạng {t,o,h,l,c,v} (TradingView UDF). Trả về list dict theo ngày VN."""
    if not isinstance(payload, dict) or "t" not in payload or not payload.get("t"):
        raise ValueError(f"Không có dữ liệu: {str(payload)[:200]}")
    if payload.get("s") not in (None, "ok"):
        raise ValueError(f"Nguồn trả trạng thái {payload.get('s')}")
    rows = []
    for k, t in enumerate(payload["t"]):
        ngay = (dt.datetime(1970, 1, 1) + dt.timedelta(seconds=int(t) + 7 * 3600)).date()
        rows.append({"date": ngay, "open": float(payload["o"][k]), "high": float(payload["h"][k]),
                     "low": float(payload["l"][k]), "close": float(payload["c"][k]),
                     "volume": float(payload["v"][k]) if payload.get("v") else None})
    # Giá cổ phiếu thường trả theo NGHÌN đồng; quy về đồng. Chỉ số giữ nguyên điểm.
    if not chi_so and statistics.median(r["close"] for r in rows) < 1000:
        for r in rows:
            for c in ("open", "high", "low", "close"):
                r[c] = round(r[c] * 1000, 2)
    gon = {r["date"]: r for r in rows}
    return [gon[d] for d in sorted(gon)]


def tai(ma, tu, den, nguon_ds, chi_so=False):
    loi = []
    ts_tu = int(dt.datetime.combine(tu, dt.time()).timestamp())
    ts_den = int(dt.datetime.combine(den, dt.time(23, 59)).timestamp())
    for nguon in nguon_ds:
        url = _url(nguon, ma, ts_tu, ts_den, chi_so)
        try:
            rows = doc_udf(tai_json(url), chi_so)
            return nguon, rows, loi
        except (urllib.error.URLError, OSError, ValueError, KeyError, json.JSONDecodeError) as e:
            loi.append(f"{nguon}: {type(e).__name__}: {str(e)[:160]}")
    return None, [], loi


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ma")
    ap.add_argument("--tu", default=(dt.date.today() - dt.timedelta(days=365 * 8)).isoformat())
    ap.add_argument("--den", default=dt.date.today().isoformat())
    ap.add_argument("--nguon", default="vndirect,entrade,vps")
    ap.add_argument("--chi-so", action="store_true", help="Mã là chỉ số (VNINDEX, VN30, HNXINDEX...)")
    ap.add_argument("--san", default="HOSE", choices=["HOSE", "HNX", "UPCOM"])
    ap.add_argument("--su-kien", help="JSON sự kiện quyền để điều chỉnh giá (xem vn_common.dieu_chinh_su_kien)")
    ap.add_argument("--ra", required=True, help="File CSV đầu ra")
    a = ap.parse_args()
    tu, den = dt.date.fromisoformat(a.tu), dt.date.fromisoformat(a.den)
    nguon, rows, loi = tai(a.ma.upper(), tu, den, [x.strip() for x in a.nguon.split(",")], a.chi_so)
    for x in loi:
        print(f"[thử nguồn thất bại] {x}")
    if not rows:
        sys.exit("Không tải được từ nguồn nào. Nếu môi trường chặn mạng, hãy xuất CSV giá từ "
                 "CafeF/Vietstock/phần mềm CTCK rồi đưa vào chi_bao.py trực tiếp.")
    if a.su_kien:
        rows = dieu_chinh_su_kien(rows, doc_json(a.su_kien))
    ghi_ohlcv(rows, a.ra)
    print(f"Nguồn: {nguon} | {len(rows)} phiên | {rows[0]['date']} → {rows[-1]['date']} | "
          f"đóng cửa cuối {rows[-1]['close']:,.0f} | đã ghi {a.ra}")
    for cb in kiem_tra_ohlcv(rows, a.san, la_chi_so=a.chi_so):
        print(f"CẢNH BÁO: {cb}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Chất lượng doanh nghiệp + định giá + phân rã biến động giá.

Cách dùng:
  py dinh_gia.py tai_chinh_FPT.json
  py dinh_gia.py tai_chinh_FPT.json --json ket_qua_dinh_gia.json

Đầu vào: JSON theo mẫu assets/mau_tai_chinh.json (đơn vị tiền: TỶ ĐỒNG; giá: ĐỒNG/cp;
số cổ phiếu: TRIỆU cp). Trường nào không có thì để trống – chỉ số cần trường đó sẽ hiện "n/a".

Script KHÔNG tự bịa giả định tăng trưởng: nếu file không có "kich_ban", script tạo kịch
bản mặc định từ lịch sử và ghi rõ là mặc định để người phân tích sửa lại theo hiểu biết
về doanh nghiệp.
"""
import argparse
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vn_common import doc_json, fmt_pct, fmt_so, ghi_json  # noqa: E402


def g(d, k):
    v = d.get(k) if d else None
    return None if v is None else float(v)


def chia(a, b):
    return None if a is None or b in (None, 0) else a / b


def tb(a, b):
    return None if a is None or b is None else (a + b) / 2


def cagr(dau, cuoi, nam):
    if dau is None or cuoi is None or dau <= 0 or cuoi <= 0 or nam <= 0:
        return None
    return (cuoi / dau) ** (1 / nam) - 1

# ---------------------------------------------------------------- chỉ số theo năm

def roe_nam(d, t):
    """ROE = LNST công ty mẹ / VCSH công ty mẹ bình quân. Nếu thiếu VCSH mẹ thì dùng
    LNST tổng / VCSH tổng (gồm cổ đông thiểu số) cho nhất quán tử và mẫu."""
    if g(d, "von_csh_me") is not None and g(d, "lnst_me") is not None:
        mau = tb(g(d, "von_csh_me"), g(t, "von_csh_me") if t else None) or g(d, "von_csh_me")
        return chia(g(d, "lnst_me"), mau)
    if g(d, "von_csh") is not None and g(d, "lnst") is not None:
        mau = tb(g(d, "von_csh"), g(t, "von_csh") if t else None) or g(d, "von_csh")
        return chia(g(d, "lnst"), mau)
    return None


def chi_so_nam(ds_nam, so):
    out = {}
    for idx, y in enumerate(ds_nam):
        d, t = so[y], so[ds_nam[idx - 1]] if idx > 0 else None
        lnst_me, lnst, lntt = g(d, "lnst_me"), g(d, "lnst"), g(d, "lntt")
        dt_ = g(d, "doanh_thu")
        vcsh_me, vcsh = g(d, "von_csh_me") or g(d, "von_csh"), g(d, "von_csh")
        tts = g(d, "tong_tai_san")
        no_vay, tien = g(d, "no_vay"), g(d, "tien_va_dtnh")
        lai_vay = g(d, "chi_phi_lai_vay")
        cfo, capex = g(d, "cfo"), g(d, "capex")
        capex = abs(capex) if capex is not None else None
        thue = None if lntt in (None, 0) or lnst is None else 1 - lnst / lntt
        r = {
            "tang_doanh_thu": chia(dt_, g(t, "doanh_thu")) - 1 if t and chia(dt_, g(t, "doanh_thu")) else None,
            "tang_lnst_me": chia(lnst_me, g(t, "lnst_me")) - 1 if t and chia(lnst_me, g(t, "lnst_me")) else None,
            "bien_gop": chia(g(d, "loi_nhuan_gop"), dt_),
            "bien_lntt": chia(lntt, dt_),
            "bien_rong": chia(lnst, dt_),
            "thue_suat_hieu_dung": thue,
            "ROE": roe_nam(d, t),
            "ROA": chia(lnst, tb(tts, g(t, "tong_tai_san") if t else None) or tts),
            "no_vay_tren_vcsh": chia(no_vay, vcsh),
            "tien_rong": None if tien is None or no_vay is None else tien - no_vay,
            "kha_nang_tra_lai": chia((lntt or 0) + (lai_vay or 0), lai_vay) if lai_vay else None,
            "FCF": None if cfo is None or capex is None else cfo - capex,
            "FCF_tren_lnst": chia(None if cfo is None or capex is None else cfo - capex, lnst),
            "CFO_tren_lnst": chia(cfo, lnst),
            "capex_tren_khau_hao": chia(capex, g(d, "khau_hao")),
            "ty_le_tich_luy_sloan": chia(None if lnst is None or cfo is None else lnst - cfo,
                                         tb(tts, g(t, "tong_tai_san") if t else None) or tts),
            "ty_le_chi_tra_co_tuc": chia(abs(g(d, "co_tuc_tien_da_tra")) if g(d, "co_tuc_tien_da_tra") else None, lnst_me),
        }
        # ROIC = NOPAT / vốn đầu tư (VCSH + nợ vay - tiền), dùng số cuối kỳ cho đơn giản
        if lntt is not None and vcsh is not None and no_vay is not None and tien is not None:
            nopat = (lntt + (lai_vay or 0)) * (1 - (thue if thue is not None and 0 <= thue < 0.5 else 0.2))
            von_dt = vcsh + no_vay - tien
            r["ROIC"] = chia(nopat, von_dt) if von_dt > 0 else None
            r["ROIC_ghi_chu"] = None if von_dt > 0 else "Vốn đầu tư âm (tiền > nợ + VCSH): ROIC không có ý nghĩa, doanh nghiệp tiền ròng lớn"
        out[y] = r
    return out

# ---------------------------------------------------------------- điểm chất lượng

def piotroski(d, t):
    """F-score 9 điểm (Piotroski 2000). Trả về (điểm, số tiêu chí tính được, chi tiết)."""
    ct = {}
    roa = chia(g(d, "lnst"), g(d, "tong_tai_san"))
    roa_t = chia(g(t, "lnst"), g(t, "tong_tai_san"))
    cfo = g(d, "cfo")
    ct["ROA > 0"] = None if roa is None else roa > 0
    ct["CFO > 0"] = None if cfo is None else cfo > 0
    ct["ROA tăng"] = None if roa is None or roa_t is None else roa > roa_t
    ct["CFO > LNST (lợi nhuận bằng tiền)"] = None if cfo is None or g(d, "lnst") is None else cfo > g(d, "lnst")
    dbb = chia(g(d, "no_vay"), g(d, "tong_tai_san"))
    dbb_t = chia(g(t, "no_vay"), g(t, "tong_tai_san"))
    ct["Đòn bẩy giảm"] = None if dbb is None or dbb_t is None else dbb <= dbb_t
    cr = chia(g(d, "tai_san_ngan_han"), g(d, "no_ngan_han"))
    cr_t = chia(g(t, "tai_san_ngan_han"), g(t, "no_ngan_han"))
    ct["Thanh toán hiện hành tăng"] = None if cr is None or cr_t is None else cr > cr_t
    ph = g(d, "tien_thu_phat_hanh_cp")
    # Ở VN cổ phiếu thưởng/cổ tức cổ phiếu không làm loãng giá trị, nên chỉ xét phát hành THU TIỀN
    ct["Không phát hành thêm thu tiền"] = None if ph is None else ph <= 0.01 * (g(d, "von_csh") or 1e18)
    bg = chia(g(d, "loi_nhuan_gop"), g(d, "doanh_thu"))
    bg_t = chia(g(t, "loi_nhuan_gop"), g(t, "doanh_thu"))
    ct["Biên gộp tăng"] = None if bg is None or bg_t is None else bg > bg_t
    vq = chia(g(d, "doanh_thu"), g(d, "tong_tai_san"))
    vq_t = chia(g(t, "doanh_thu"), g(t, "tong_tai_san"))
    ct["Vòng quay tài sản tăng"] = None if vq is None or vq_t is None else vq > vq_t
    tinh = [v for v in ct.values() if v is not None]
    return sum(tinh), len(tinh), ct


def altman_z2(d):
    """Altman Z'' (bản cho doanh nghiệp phi sản xuất/thị trường mới nổi, không hằng số).
    Vùng: > 2,6 an toàn; 1,1–2,6 xám; < 1,1 nguy cơ. KHÔNG dùng cho ngân hàng/CTCK/bảo hiểm."""
    tts = g(d, "tong_tai_san")
    can = ["tai_san_ngan_han", "no_ngan_han", "loi_nhuan_chua_phan_phoi", "lntt", "von_csh", "no_phai_tra"]
    if not tts or any(g(d, k) is None for k in can) or not g(d, "no_phai_tra"):
        return None
    x1 = (g(d, "tai_san_ngan_han") - g(d, "no_ngan_han")) / tts
    x2 = g(d, "loi_nhuan_chua_phan_phoi") / tts
    x3 = (g(d, "lntt") + (g(d, "chi_phi_lai_vay") or 0)) / tts
    x4 = g(d, "von_csh") / g(d, "no_phai_tra")
    z = 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4
    return {"Z2": z, "vung": "An toàn" if z > 2.6 else "Vùng xám" if z >= 1.1 else "Nguy cơ kiệt quệ"}


def beneish(d, t):
    """Beneish M-score 8 biến. > -1,78: có dấu hiệu cần soi kỹ chất lượng lợi nhuận."""
    k = ["doanh_thu", "phai_thu", "loi_nhuan_gop", "tai_san_ngan_han", "tscd", "tong_tai_san",
         "khau_hao", "chi_phi_ban_hang", "chi_phi_qldn", "lnst", "cfo", "no_phai_tra"]
    if not t or any(g(d, x) is None or g(t, x) is None for x in k):
        return None
    try:
        dsri = (g(d, "phai_thu") / g(d, "doanh_thu")) / (g(t, "phai_thu") / g(t, "doanh_thu"))
        gmi = (g(t, "loi_nhuan_gop") / g(t, "doanh_thu")) / (g(d, "loi_nhuan_gop") / g(d, "doanh_thu"))
        aqi = (1 - (g(d, "tai_san_ngan_han") + g(d, "tscd")) / g(d, "tong_tai_san")) / \
              (1 - (g(t, "tai_san_ngan_han") + g(t, "tscd")) / g(t, "tong_tai_san"))
        sgi = g(d, "doanh_thu") / g(t, "doanh_thu")
        depi = (g(t, "khau_hao") / (g(t, "khau_hao") + g(t, "tscd"))) / (g(d, "khau_hao") / (g(d, "khau_hao") + g(d, "tscd")))
        sga = lambda x: (g(x, "chi_phi_ban_hang") + g(x, "chi_phi_qldn")) / g(x, "doanh_thu")  # noqa: E731
        sgai = sga(d) / sga(t)
        tata = (g(d, "lnst") - g(d, "cfo")) / g(d, "tong_tai_san")
        lvgi = (g(d, "no_phai_tra") / g(d, "tong_tai_san")) / (g(t, "no_phai_tra") / g(t, "tong_tai_san"))
    except ZeroDivisionError:
        return None
    m = -4.84 + 0.920 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi + 0.115 * depi - 0.172 * sgai + 4.679 * tata - 0.327 * lvgi
    return {"M": m, "danh_gia": "Cần soi kỹ (M > -1,78)" if m > -1.78 else "Không có dấu hiệu bất thường",
            "thanh_phan": {"DSRI": dsri, "GMI": gmi, "AQI": aqi, "SGI": sgi, "DEPI": depi, "SGAI": sgai, "TATA": tata, "LVGI": lvgi}}

# ---------------------------------------------------------------- định giá

def gia_tri_eps(eps0, g1, g2, pe_cuoi, r, chi_tra, n1=5, n2=5):
    """Chiết khấu cổ tức 10 năm + giá bán cuối năm 10 (EPS x P/E). Trả về dict."""
    eps, pv, cong_ct = eps0, 0.0, 0.0
    for nam in range(1, n1 + n2 + 1):
        eps *= (1 + g1) if nam <= n1 else (1 + g2)
        pv += chi_tra * eps / (1 + r) ** nam
        cong_ct += chi_tra * eps
    cuoi = eps * pe_cuoi
    return {"gia_tri": pv + cuoi / (1 + r) ** (n1 + n2), "eps_nam_10": eps, "gia_nam_10": cuoi, "tong_co_tuc": cong_ct}


def tang_truong_ngu_y(gia, eps0, pe_cuoi, r, chi_tra, g2_co_dinh=None, n1=5):
    """Tìm tốc độ tăng EPS mà giá hiện tại đang 'trả trước' (reverse DCF)."""
    lo, hi = -0.3, 0.8
    for _ in range(100):
        m = (lo + hi) / 2
        g2 = m if g2_co_dinh is None else g2_co_dinh
        v = gia_tri_eps(eps0, m, g2, pe_cuoi, r, chi_tra, n1, 10 - n1)["gia_tri"]
        lo, hi = (lo, m) if v > gia else (m, hi)
    return (lo + hi) / 2


def pb_hop_ly(roe, g_, r):
    """P/B hợp lý cho ngân hàng/tài chính: (ROE - g) / (r - g)."""
    return None if r <= g_ else (roe - g_) / (r - g_)


def kich_ban_mac_dinh(cagr5, chi_tra):
    base = max(0.0, min((cagr5 or 0.08) * 0.7, 0.20))
    return {
        "bi_quan": {"g1": round(base * 0.5, 3), "g2": round(base * 0.35, 3), "pe_cuoi": 9, "chi_tra": chi_tra, "trong_so": 0.25},
        "co_so": {"g1": round(base, 3), "g2": round(base * 0.65, 3), "pe_cuoi": 12, "chi_tra": chi_tra, "trong_so": 0.5},
        "lac_quan": {"g1": round(min(base * 1.3, 0.25), 3), "g2": round(base * 0.85, 3), "pe_cuoi": 15, "chi_tra": chi_tra, "trong_so": 0.25},
        "_ghi_chu": "MẶC ĐỊNH sinh từ CAGR lợi nhuận 5 năm. Hãy sửa theo phân tích ngành và doanh nghiệp.",
    }


def phan_ra(lich_su):
    """Phân rã biến động giá giữa các mốc thành phần do EPS và phần do P/E (kỳ vọng)."""
    out = []
    for a, b in zip(lich_su, lich_su[1:]):
        pe_a, pe_b = a["gia"] / a["eps_ttm"], b["gia"] / b["eps_ttm"]
        out.append({"tu": a["ngay"], "den": b["ngay"], "gia": b["gia"] / a["gia"] - 1,
                    "eps": b["eps_ttm"] / a["eps_ttm"] - 1, "pe_dau": pe_a, "pe_cuoi": pe_b, "pe": pe_b / pe_a - 1})
    return out

# ---------------------------------------------------------------- chạy

def chay(dl):
    so = dl["nam"]
    ds_nam = sorted(so)
    cuoi = so[ds_nam[-1]]
    gia = float(dl["gia_hien_tai"])
    cp = float(dl.get("so_cp_luu_hanh_trieu") or g(cuoi, "so_cp_trieu"))
    r = float(dl.get("chiet_khau", 0.12))
    lnst_ttm = float(dl.get("lnst_ttm_me") or g(cuoi, "lnst_me"))
    eps0 = lnst_ttm * 1e9 / (cp * 1e6)
    von_hoa = gia * cp * 1e6 / 1e9
    cs = chi_so_nam(ds_nam, so)
    n = len(ds_nam) - 1
    so_nam_cagr = min(5, n)
    c5 = cagr(g(so[ds_nam[max(0, n - 5)]], "lnst_me"), g(cuoi, "lnst_me"), so_nam_cagr)
    call = cagr(g(so[ds_nam[0]], "lnst_me"), g(cuoi, "lnst_me"), n)
    chi_tra_ls = [cs[y]["ty_le_chi_tra_co_tuc"] for y in ds_nam[-3:] if cs[y]["ty_le_chi_tra_co_tuc"] is not None]
    chi_tra = round(statistics.mean(chi_tra_ls), 2) if chi_tra_ls else 0.3
    kb = dl.get("kich_ban") or kich_ban_mac_dinh(c5, chi_tra)
    mac_dinh = "kich_ban" not in dl

    kq = {"ma": dl.get("ma"), "nganh": dl.get("nganh"), "gia": gia, "ngay_gia": dl.get("ngay_gia"),
          "von_hoa_ty": von_hoa, "eps_ttm": eps0, "PE_ttm": gia / eps0 if eps0 > 0 else None,
          "loi_suat_loi_nhuan": eps0 / gia, "CAGR_lnst_me_5n": c5, "so_nam_tinh_CAGR": so_nam_cagr,
          "CAGR_lnst_me_toan_ky": call,
          "canh_bao": ([f"Chỉ có {n + 1} năm số liệu: CAGR và kịch bản mặc định kém tin cậy, nên dùng >= 6 năm "
                        "để thấy trọn một chu kỳ"] if n < 5 else []),
          "so_nam_lnst_tang": sum(1 for y in ds_nam[1:] if (cs[y]["tang_lnst_me"] or 0) > 0),
          "so_nam_lo": sum(1 for y in ds_nam if (g(so[y], "lnst_me") or 0) < 0),
          "chi_so_nam": cs}
    vcsh_me = g(cuoi, "von_csh_me") or g(cuoi, "von_csh")
    if dl.get("von_csh_me_hien_tai"):
        vcsh_me = float(dl["von_csh_me_hien_tai"])
    if vcsh_me:
        kq["PB"] = von_hoa / vcsh_me
        kq["BVPS"] = vcsh_me * 1e9 / (cp * 1e6)
    if dl.get("lai_suat_tpcp_10n"):
        kq["chenh_lech_loi_suat_so_TPCP"] = eps0 / gia - float(dl["lai_suat_tpcp_10n"])

    if len(ds_nam) >= 2:
        t = so[ds_nam[-2]]
        f, nf, ct = piotroski(cuoi, t)
        kq["piotroski"] = {"diem": f, "so_tieu_chi": nf, "chi_tiet": ct}
        kq["beneish"] = beneish(cuoi, t)
    kq["altman_z2"] = None if (dl.get("nganh") in ("ngan_hang", "chung_khoan", "bao_hiem")) else altman_z2(cuoi)

    # Kiểm định "1 đồng lợi nhuận giữ lại" của Buffett
    kd = dl.get("kiem_dinh_giu_lai")
    if kd:
        y0 = str(kd["nam_bat_dau"])
        ys = [y for y in ds_nam if y > y0]
        giu = sum((g(so[y], "lnst_me") or 0) - abs(g(so[y], "co_tuc_tien_da_tra") or 0) for y in ys)
        giu += float(kd.get("cong_them_giu_lai", 0))
        tang = von_hoa - float(kd["von_hoa_dau_ky"])
        tl_ = chia(tang, giu)
        kq["kiem_dinh_giu_lai"] = {"loi_nhuan_giu_lai": giu, "von_hoa_tang": tang, "ty_le": tl_,
                                   "ket_luan": ("Không tính được" if tl_ is None else "Đạt" if tl_ >= 1 else
                                                "Sát ngưỡng" if tl_ >= 0.9 else "Không đạt")}

    # Định giá theo kịch bản
    dg = {}
    for ten, k in kb.items():
        if ten.startswith("_"):
            continue
        v = gia_tri_eps(eps0, k["g1"], k["g2"], k["pe_cuoi"], r, k.get("chi_tra", chi_tra))
        v["loi_suat_ky_vong_nam"] = ((v["gia_nam_10"] + v["tong_co_tuc"]) / gia) ** 0.1 - 1 if v["gia_nam_10"] > 0 else None
        v["bien_an_toan"] = 1 - gia / v["gia_tri"] if v["gia_tri"] > 0 else None
        v["gia_dinh"] = k
        dg[ten] = v
    ts = sum(k.get("trong_so", 0) for kk, k in kb.items() if not kk.startswith("_"))
    if ts > 0:
        kq["gia_tri_ky_vong"] = sum(dg[t_]["gia_tri"] * kb[t_].get("trong_so", 0) for t_ in dg) / ts
        kq["bien_an_toan_ky_vong"] = 1 - gia / kq["gia_tri_ky_vong"]
    mos = float(dl.get("bien_an_toan_mong_muon", 0.3))
    if "co_so" in dg:
        kq["gia_mua_toi_da_co_so"] = dg["co_so"]["gia_tri"] * (1 - mos)
    kq["dinh_gia"] = dg
    kq["kich_ban_la_mac_dinh"] = mac_dinh
    kq["ngu_y"] = {
        "tang_truong_10n_pe_cuoi_12": tang_truong_ngu_y(gia, eps0, 12, r, chi_tra, n1=10),
        "tang_truong_10n_pe_cuoi_15": tang_truong_ngu_y(gia, eps0, 15, r, chi_tra, n1=10),
        "tang_truong_5n_roi_5pct_pe_cuoi_10": tang_truong_ngu_y(gia, eps0, 10, r, chi_tra, g2_co_dinh=0.05),
    }
    if dl.get("nganh") in ("ngan_hang", "chung_khoan", "bao_hiem") and vcsh_me:
        roe = cs[ds_nam[-1]]["ROE"]
        gdh = float(dl.get("tang_truong_dai_han", 0.06))
        kq["PB_hop_ly"] = pb_hop_ly(roe, gdh, r) if roe else None
        kq["gia_theo_PB_hop_ly"] = kq["PB_hop_ly"] * kq["BVPS"] if kq.get("PB_hop_ly") else None
    if dl.get("lich_su_gia_eps"):
        kq["phan_ra_bien_dong"] = phan_ra(dl["lich_su_gia_eps"])
    kq["suat_chiet_khau"] = r
    return kq


def in_tom_tat(kq):
    p = print
    p(f"# Định giá {kq['ma']} – giá {fmt_so(kq['gia'])} ({kq.get('ngay_gia') or 'chưa ghi ngày'})")
    p(f"- Vốn hóa {fmt_so(kq['von_hoa_ty'])} tỷ; EPS 12T {fmt_so(kq['eps_ttm'])}; P/E {fmt_so(kq['PE_ttm'], 1)}; "
      f"E/P {fmt_pct(kq['loi_suat_loi_nhuan'])}" + (f"; P/B {fmt_so(kq['PB'], 2)}" if kq.get("PB") else ""))
    p(f"- CAGR LNST mẹ {kq['so_nam_tinh_CAGR']} năm {fmt_pct(kq['CAGR_lnst_me_5n'])}; số năm tăng {kq['so_nam_lnst_tang']}; số năm lỗ {kq['so_nam_lo']}")
    for cb in kq["canh_bao"]:
        p(f"> CẢNH BÁO: {cb}")
    p("\n## Chất lượng theo năm")
    p("| Năm | Tăng LNST mẹ | Biên LNTT | ROE | ROIC | Nợ vay/VCSH | CFO/LNST | FCF/LNST | Tích lũy Sloan |")
    p("|---|---|---|---|---|---|---|---|---|")
    for y, c in kq["chi_so_nam"].items():
        p(f"| {y} | {fmt_pct(c['tang_lnst_me'])} | {fmt_pct(c['bien_lntt'])} | {fmt_pct(c['ROE'])} | {fmt_pct(c.get('ROIC'))} | "
          f"{fmt_so(c['no_vay_tren_vcsh'], 2)} | {fmt_so(c['CFO_tren_lnst'], 2)} | {fmt_so(c['FCF_tren_lnst'], 2)} | {fmt_pct(c['ty_le_tich_luy_sloan'])} |")
    if kq.get("piotroski"):
        pi = kq["piotroski"]
        p(f"\n- Piotroski F-score: {pi['diem']}/{pi['so_tieu_chi']} tiêu chí tính được" if pi["so_tieu_chi"]
          else "\n- Piotroski F-score: không đủ dữ liệu (cần 2 năm liền có CĐKT + LCTT)")
    if kq.get("beneish"):
        p(f"- Beneish M-score: {fmt_so(kq['beneish']['M'], 2)} → {kq['beneish']['danh_gia']}")
    if kq.get("altman_z2"):
        p(f"- Altman Z'': {fmt_so(kq['altman_z2']['Z2'], 2)} → {kq['altman_z2']['vung']}")
    if kq.get("kiem_dinh_giu_lai"):
        k = kq["kiem_dinh_giu_lai"]
        p(f"- Kiểm định 1 đồng giữ lại: giữ lại {fmt_so(k['loi_nhuan_giu_lai'])} tỷ, vốn hóa tăng {fmt_so(k['von_hoa_tang'])} tỷ "
          f"→ {fmt_so(k['ty_le'], 2)} lần ({k['ket_luan']})")
    p(f"\n## Định giá (chiết khấu {fmt_pct(kq['suat_chiet_khau'])})" + (" – KỊCH BẢN MẶC ĐỊNH, cần sửa" if kq["kich_ban_la_mac_dinh"] else ""))
    p("| Kịch bản | g năm 1–5 | g năm 6–10 | P/E cuối | Giá trị | Biên an toàn | Lợi suất kỳ vọng/năm |")
    p("|---|---|---|---|---|---|---|")
    for t, v in kq["dinh_gia"].items():
        k = v["gia_dinh"]
        p(f"| {t} | {fmt_pct(k['g1'])} | {fmt_pct(k['g2'])} | {fmt_so(k['pe_cuoi'], 1)} | {fmt_so(v['gia_tri'])} | "
          f"{fmt_pct(v['bien_an_toan'])} | {fmt_pct(v['loi_suat_ky_vong_nam'])} |")
    if kq.get("gia_tri_ky_vong"):
        p(f"\n- Giá trị bình quân theo trọng số: {fmt_so(kq['gia_tri_ky_vong'])} (biên an toàn {fmt_pct(kq['bien_an_toan_ky_vong'])})")
    if kq.get("gia_mua_toi_da_co_so"):
        p(f"- Giá mua tối đa theo kịch bản cơ sở và biên an toàn mong muốn: {fmt_so(kq['gia_mua_toi_da_co_so'])}")
    ny = kq["ngu_y"]
    p(f"- Giá hiện tại ngụ ý EPS tăng {fmt_pct(ny['tang_truong_10n_pe_cuoi_12'])}/năm x10 năm (P/E cuối 12), "
      f"{fmt_pct(ny['tang_truong_10n_pe_cuoi_15'])} (P/E cuối 15), hoặc {fmt_pct(ny['tang_truong_5n_roi_5pct_pe_cuoi_10'])} "
      "x5 năm rồi 5% (P/E cuối 10)")
    if kq.get("PB_hop_ly"):
        p(f"- P/B hợp lý (ROE, g dài hạn): {fmt_so(kq['PB_hop_ly'], 2)} → {fmt_so(kq['gia_theo_PB_hop_ly'])} đ/cp")
    if kq.get("phan_ra_bien_dong"):
        p("\n## Phân rã biến động giá")
        for x in kq["phan_ra_bien_dong"]:
            p(f"- {x['tu']} → {x['den']}: giá {fmt_pct(x['gia'])} = EPS {fmt_pct(x['eps'])} × P/E {fmt_pct(x['pe'])} "
              f"(P/E {fmt_so(x['pe_dau'], 1)} → {fmt_so(x['pe_cuoi'], 1)})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json_dau_vao")
    ap.add_argument("--json", help="Ghi kết quả đầy đủ ra file JSON")
    a = ap.parse_args()
    kq = chay(doc_json(a.json_dau_vao))
    in_tom_tat(kq)
    if a.json:
        ghi_json(kq, a.json)
        print(f"\nĐã ghi {a.json}")


if __name__ == "__main__":
    main()

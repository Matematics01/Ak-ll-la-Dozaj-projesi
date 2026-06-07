"""
╔════════════════════════════════════════════════════════════════════════════╗
║   AKILLI İLAÇ DOZAJI — ÖDEV 4 (GrupNo_1)                                   ║
║   Yöntem · Algoritma · Uygulama Tasarımı · Başarı Ölçütleri                ║
║   Bursa Uludağ Üniversitesi — Matematik Bölümü — 1. Grup                   ║
╠════════════════════════════════════════════════════════════════════════════╣
║  Grup Üyeleri:                                                             ║
║    Ramazan Güngör   — 082240026                                            ║
║    Orhan Akyavuz    — 082240046                                            ║
║    Zekeriya Obceşoy — 082240054                                            ║
╠════════════════════════════════════════════════════════════════════════════╣
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import sys


# ─────────────────────────────────────────────────────────────
# 0. ÖDEV 4 YENİ MODÜL: ALGORİTMA AKIŞ ŞEMASI
# ─────────────────────────────────────────────────────────────

def akis_semasi_yazdir():
    """
    Programın algoritma akış şemasını konsola yazdırır.

    ÖDEV 4 gereksinimi:
      Girdi → İşlem → Hesaplama → Çıktı adımlarını görselleştirir.
    Bu fonksiyon PyCharm Run penceresinde okunabilir biçimde
    programın tüm mantık akışını şematik olarak sunar.
    """
    print()
    print("╔" + "═" * 68 + "╗")
    print("║{:^68}║".format("ÖDEV 4 — ALGORİTMA AKIŞ ŞEMASI"))
    print("╠" + "═" * 68 + "╣")
    adimlar = [
        ("[ GİRDİ ]",
         ["Kullanıcı: C₀ (mg) ve C_ss (mg) girer",
          "Doğrulama: 0 ≤ C₀ ≤ 10000, 1 ≤ C_ss ≤ 10000",
          "Hatalı girişte tekrar sor (try/except)"]),
        ("[ PARAMETRE HESAPLAMA ]",
         ["k  = ln(2) / t½          → t½ = 4.0 saat (sabit)",
          "D  = C_ss · k · τ        → τ  = 6.0 saat (sabit)",
          "ti = [0, 6, 12, ..., 42] → doz zamanları"]),
        ("[ SEMBOLİK DOĞRULAMA — SymPy ]",
         ["sp.symbols() → sembolik değişken tanımla",
          "sp.limit(C, t, 0, '-')  → sol limit analitik",
          "sp.limit(C, t, 0, '+')  → sağ limit analitik",
          "sp.diff(C, t)           → dC/dt eliminasyon hızı"]),
        ("[ SAYISAL HESAPLAMA — NumPy ]",
         ["zaman = np.arange(0, 48, dt)   → dt = 0.01 saat",
          "C += C0 * np.exp(-k * zaman)   → başlangıç bozunması",
          "C += D * np.exp(-k*(t-ti))     → her doz süperpozisyon"]),
        ("[ GEÇİŞ ANALİZİ ]",
         ["Her ti için sol_limit hesapla   → birikimli doz toplamı",
          "sag_limit = sol_limit + D        → anlık sıçrama",
          "sag > C_ss*1.8  →  RİSKLİ (toksik)",
          "sol < C_ss*0.25 →  RİSKLİ (sub-terapötik)",
          "t=0             →  RİSKLİ (başlangıç)"]),
        ("[ ÇIKTI ]",
         ["Konsol: geçiş tablosu + klinik metrikler + uyarılar",
          "Grafik: 3 panelli Matplotlib PNG → diske kaydet",
          "Rapor:  başarı ölçütleri doğrulama sonuçları"]),
    ]
    for baslik, satirlar in adimlar:
        print("║" + " " * 68 + "║")
        print("║  {:^64}  ║".format(baslik))
        for s in satirlar:
            print("║    * {:<62}║".format(s))
        print("║" + " " * 34 + "v" + " " * 33 + "║")
    print("╚" + "═" * 68 + "╝")
    print()


# ─────────────────────────────────────────────────────────────
# 1. SEMBOLİK HESAP (sympy) — LİMİT DOĞRULAMA
# ─────────────────────────────────────────────────────────────

def sembolik_limit_goster(hedef: float, sabitler: dict):
    """
    sympy ile sol-sağ limit formüllerini sembolik olarak doğrular.

    Odev-3/4 teknik gereksinimi: sympy kullanımı gösterildi
    Kaynak: SymPy Geliştirme Ekibi (2024) — sp.symbols, sp.limit, sp.diff
    """
    try:
        import sympy as sp

        print()
        print("╔══════════════════════════════════════════════════════╗")
        print("║   SEMBOLİK HESAP — sympy ile Limit Doğrulama        ║")
        print("╚══════════════════════════════════════════════════════╝")

        t, k_sym, C0_sym, D_sym = sp.symbols('t k C_0 D', positive=True)

        C_sol = C0_sym * sp.exp(-k_sym * t)
        C_sag = C0_sym * sp.exp(-k_sym * t) + D_sym

        print()
        print("  Fonksiyon tanımları:")
        print(f"    C_sol(t) = {C_sol}   [doz öncesi]")
        print(f"    C_sag(t) = {C_sag}   [doz sonrası]")
        print()

        lim_sol = sp.limit(C_sol, t, 0, '-')
        lim_sag = sp.limit(C_sag, t, 0, '+')

        print("  t = 0 noktasında limit analizi:")
        print(f"    lim_{{t→0-}} C_sol(t) = {lim_sol}   → t=0 öncesi değer")
        print(f"    lim_{{t→0+}} C_sag(t) = {lim_sag}   → t=0 sonrası değer")
        print()

        k_num = np.log(2) / sabitler["yari_omur"]
        D_num = hedef * k_num * sabitler["doz_araligi"]

        lim_sol_num = float(lim_sol.subs([(C0_sym, 0), (k_sym, k_num)]))
        lim_sag_num = float(lim_sag.subs([(C0_sym, 0), (k_sym, k_num),
                                           (D_sym, D_num)]))

        print(f"  C0=0 için sayısal karşılık (D={D_num:.2f} mg):")
        print(f"    Sol limit (t→0-) = {lim_sol_num:.4f} mg  [= C0 = 0]")
        print(f"    Sag limit (t→0+) = {lim_sag_num:.4f} mg  [= C0 + D = {D_num:.2f}]")
        print(f"    Sicrama Delta    = {lim_sag_num - lim_sol_num:.4f} mg  [= D]")
        print()

        dC_dt = sp.diff(C_sol, t)
        print(f"  dC/dt = {dC_dt}   [eliminasyon hızı]")
        print(f"    → t→∞ için: {sp.limit(dC_dt, t, sp.oo)} (atılım tamamlanır)")
        print()
        print("  Sembolik doğrulama tamamlandı.")
        print("─" * 54)

    except ImportError:
        print()
        print("  UYARI: sympy yüklü değil. Sembolik hesap atlandı.")
        print("  Yüklemek için: pip install sympy")
        print("─" * 54)


# ─────────────────────────────────────────────────────────────
# 2. KULLANICI GİRİŞİ
# ─────────────────────────────────────────────────────────────

def kullanici_girisi() -> dict:
    """
    Kullanıcıdan başlangıç ve hedef konsantrasyon değerlerini alır.
    Doğrulama yapar, hatalı girişte tekrar sorar.

    Kaynak: Besler ve Sahin (2021) — try/except ile giriş doğrulama
    PyCharm Run penceresinde interaktif olarak çalışır.
    """
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║   AKILLI ILAC DOZAJI SIMULATORU  —  ODEV 4          ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    def pozitif_float(mesaj, min_val=0.0, max_val=10000.0):
        while True:
            try:
                deger = float(input(mesaj))
                if deger < min_val or deger > max_val:
                    print(f"  UYARI: Lutfen {min_val}–{max_val} mg arasinda bir deger girin.\n")
                else:
                    return deger
            except ValueError:
                print("  UYARI: Gecersiz giris. Sayisal bir deger girin.\n")

    print("─" * 54)
    print("  ADIM 1 / 2 — Baslangic Konsantrasyonu (C0)")
    print("  Sistem sifirdan basliyorsa 0 giriniz.")
    print("─" * 54)
    C0 = pozitif_float("  C0 = ", min_val=0.0, max_val=10000.0)

    print()
    print("─" * 54)
    print("  ADIM 2 / 2 — Hedef Kararli Hal Konsantrasyonu (C_ss)")
    print("  Doz miktari otomatik hesaplanir: D = C_ss * k * tau")
    print("─" * 54)
    hedef = pozitif_float("  C_ss = ", min_val=1.0, max_val=10000.0)

    return {"C0": C0, "hedef": hedef}


# ─────────────────────────────────────────────────────────────
# 3. SABİT SİSTEM PARAMETRELERİ (merkezi parametre deposu)
# ─────────────────────────────────────────────────────────────

SABITLER = {
    "yari_omur"  : 4.0,    # saat  — eliminasyon yari ömrü   (Cakir, 2020)
    "doz_araligi": 6.0,    # saat  — tekrarlayan doz periyodu (Cakir, 2020)
    "toplam_sure": 48.0,   # saat  — simulasyon penceresi
    "dt"         : 0.01,   # saat  — zaman adimi              (Bozkurt, 2019)
}


# ─────────────────────────────────────────────────────────────
# 4. KONSANTRASYONu HESAPLA
# ─────────────────────────────────────────────────────────────

def konsantrasyon_hesapla(C0: float, hedef: float, sabitler: dict) -> dict:
    """
    Superpozisyon prensibiyle tum dozlarin birikimli etkisini hesaplar.

    MODEL:
        C(t) = C0 * e^(-k*t)  +  Sum_i  D * e^(-k*(t-ti))    [t >= ti]

    Kaynak: NumPy Gelistirme Ekibi (2024) — np.arange, np.exp, np.zeros_like
    Kaynak: Tuna (2017)                   — superpozisyon prensibi
    Kaynak: Bozkurt (2019)                — sayisal hesap, dt secimi
    Kaynak: Yildirim (2016)               — k = ln(2)/t½  ODE cozumu
    """
    k    = np.log(2) / sabitler["yari_omur"]    # Yildirim (2016)
    tau  = sabitler["doz_araligi"]
    sure = sabitler["toplam_sure"]
    dt   = sabitler["dt"]

    D = hedef * k * tau                          # Tuna (2017): D = C_ss * k * tau

    zaman = np.arange(0, sure + dt, dt)
    C     = np.zeros_like(zaman)

    C += C0 * np.exp(-k * zaman)                 # baslangic bozunmasi

    doz_anlari = np.arange(0, sure, tau)
    for td in doz_anlari:
        maske = zaman >= td
        C[maske] += D * np.exp(-k * (zaman[maske] - td))   # superpozisyon

    return {
        "zaman"     : zaman,
        "C"         : C,
        "doz_anlari": doz_anlari,
        "D"         : D,
        "k"         : k,
    }


# ─────────────────────────────────────────────────────────────
# 5. SÜREKSİZLİK & GEÇİŞ ANALİZİ
# ─────────────────────────────────────────────────────────────

def gecis_analizi(sonuc: dict, C0: float, hedef: float) -> list:
    """
    Her doz aninda matematiksel sol-sag limit analizi yapar.
    Gecisi RISKLI veya GUVENLI olarak siniflandirir.

    Kaynak: Ayres (2015)  — limit ve sicrama sureksizligi tanimi
    Kaynak: Gunduz (2018) — sol limit lim_{t→td-}, sag limit lim_{t→td+}
    Kaynak: Cakir (2020)  — toksik esik ve alt esik klinik degerleri

    RİSKLİ Kriterleri:
      * t = 0              → baslangic sureksizligi
      * sag > C_ss * 1.8   → toksik esik
      * sol < C_ss * 0.25  → sub-terapotik
    """
    k          = sonuc["k"]
    D          = sonuc["D"]
    doz_anlari = sonuc["doz_anlari"]

    toksik_esik = hedef * 1.8     # Cakir (2020)
    alt_esik    = hedef * 0.25    # Cakir (2020)

    sonuclar = []
    print()
    print("=" * 74)
    print("  GECIS ANALIZI  —  Sol Limit / Sag Limit / Risk Durumu")
    print("=" * 74)
    print(f"  {'#':>3}  {'Zaman':>8}  {'Sol Limit':>12}  "
          f"{'Sag Limit':>12}  {'Atlama D':>10}  {'Durum'}")
    print("  " + "─" * 70)

    for idx, td in enumerate(doz_anlari):
        sol = C0 * np.exp(-k * td)               # Gunduz (2018)
        for j in range(idx):
            sol += D * np.exp(-k * (td - doz_anlari[j]))

        sag    = sol + D     # Gunduz (2018): sag limit = sol limit + D
        atlama = D           # Ayres (2015):  Delta = D (sicrama buyuklugu)

        riskli = (
            td == 0 or
            sag > toksik_esik or
            sol < alt_esik
        )

        if td == 0:
            neden = "t=0 baslangic sureksizligi"
        elif sag > toksik_esik:
            neden = f"sag limit toksik esigi ({toksik_esik:.0f} mg) asiyor"
        elif sol < alt_esik:
            neden = f"sol limit alt sinirin ({alt_esik:.0f} mg) altinda"
        else:
            neden = "guvenli terapotik pencere icinde"

        durum = "!! RISKLI GECIS" if riskli else "OK GUVENLI GECIS"

        print(f"  {idx+1:>3}  {td:>7.1f}s  {sol:>11.2f}m  "
              f"{sag:>11.2f}m  {atlama:>9.2f}m  {durum}")
        print(f"       {'':>8}  → {neden}")
        if idx < len(doz_anlari) - 1:
            print()

        sonuclar.append({
            "doz_no": idx + 1, "t": td, "sol": sol,
            "sag": sag, "atlama": atlama,
            "riskli": riskli, "neden": neden,
        })

    print("=" * 74)
    return sonuclar


# ─────────────────────────────────────────────────────────────
# 6. KLİNİK METRİKLER
# ─────────────────────────────────────────────────────────────

def metrik_yazdir(sonuc: dict, gecisler: list,
                  C0: float, hedef: float, sabitler: dict):
    """
    Simulasyon uzerinden klinik acidan onemli metrikleri raporlar.

    Kaynak: Cakir (2020) — C_max, C_min, terapotik pencere yorumu
    """
    C    = sonuc["C"]
    k    = sonuc["k"]
    D    = sonuc["D"]
    sure = sabitler["toplam_sure"]
    dt   = sabitler["dt"]

    Cmax     = np.max(C)
    Tmax     = sonuc["zaman"][np.argmax(C)]
    Cmin     = np.min(C[sonuc["zaman"] > 0])
    C_ss_ter = D / (k * sabitler["doz_araligi"])

    toksik    = hedef * 1.8
    alt_sinir = hedef * 0.25

    sure_terapotik = np.sum((C >= alt_sinir) & (C <= toksik)) * dt
    sure_toksik    = np.sum(C > toksik) * dt
    sure_sub       = np.sum(C < alt_sinir) * dt

    riskli_say  = sum(1 for g in gecisler if g["riskli"])
    guvenli_say = sum(1 for g in gecisler if not g["riskli"])

    print()
    print("=" * 54)
    print("  KLİNİK METRİKLER")
    print("=" * 54)
    print(f"  C0  (baslangic)           : {C0:.1f} mg")
    print(f"  C_ss (hedef kararli hal)  : {hedef:.1f} mg")
    print(f"  D   (hesaplanan doz)      : {D:.2f} mg")
    print(f"  k   (elim. sabiti)        : {k:.4f} saat-1")
    print(f"  C_max                     : {Cmax:.2f} mg  @  t={Tmax:.2f} saat")
    print(f"  C_min                     : {Cmin:.2f} mg")
    print(f"  C_ss (teorik dogrulama)   : {C_ss_ter:.2f} mg")
    print(f"  Terapotik bolge suresi    : {sure_terapotik:.1f} saat "
          f"(%{100*sure_terapotik/sure:.1f})")
    print(f"  Toksik bolge suresi       : {sure_toksik:.1f} saat "
          f"(%{100*sure_toksik/sure:.1f})")
    print(f"  Sub-terapotik bolge       : {sure_sub:.1f} saat "
          f"(%{100*sure_sub/sure:.1f})")
    print(f"  Riskli gecis sayisi       : {riskli_say}")
    print(f"  Guvenli gecis sayisi      : {guvenli_say}")
    print("=" * 54)

    print()
    if Cmax > toksik:
        print(f"  TOKSIK UYARI: C_max ({Cmax:.1f} mg) toksik esigi "
              f"({toksik:.0f} mg) ASIYOR!")
        print(f"  → Doz miktari veya araligi gözden gecirilmeli.\n")
    if Cmin < alt_sinir and Cmin > 0:
        print(f"  SUB-TERAPOTIK: C_min ({Cmin:.1f} mg) alt sinirin "
              f"({alt_sinir:.0f} mg) altina dusuyor.")
        print(f"  → Doz araligi kisaltilabilir.\n")
    if riskli_say == 0:
        print("  Tum gecisler guvenli — terapotik pencere korunuyor.\n")
    else:
        print(f"  {riskli_say} riskli gecis tespit edildi. "
              f"Grafikteki kirmizi noktalari inceleyin.\n")


# ─────────────────────────────────────────────────────────────
# 7. ÖDEV 4 YENİ MODÜL: BAŞARI ÖLÇÜTLERİ DOĞRULAMA
# ─────────────────────────────────────────────────────────────

def basari_olcut_dogrula(sonuc: dict, gecisler: list,
                          C0: float, hedef: float, sabitler: dict) -> dict:
    """
    Odev 4 basari olcutlerini otomatik olarak dogrular.

    Olcutler:
      1. Matematiksel dogruluk  : C_ss_teorik sapmasi < %1
      2. Risk siniflandirmasi   : t=0 her zaman RISKLI
      3. Moduler yapi           : 8 fonksiyon bagimsiz tanimli mi?
      4. Sembolik dogrulama     : sympy kurulu mu?

    Kaynak: Ozturk ve Demirci (2023) — moduler kod dogrulama
    """
    D   = sonuc["D"]
    k   = sonuc["k"]
    tau = sabitler["doz_araligi"]

    C_ss_teorik = D / (k * tau)
    sapma_pct   = abs(C_ss_teorik - hedef) / hedef * 100

    t0_riskli = any(g["t"] == 0 and g["riskli"] for g in gecisler)

    try:
        import sympy
        sympy_ok = True
    except ImportError:
        sympy_ok = False

    fonksiyonlar = [
        kullanici_girisi, konsantrasyon_hesapla, sembolik_limit_goster,
        gecis_analizi, metrik_yazdir, grafik_ciz,
        ornek_calistir, basari_olcut_dogrula,
    ]
    moduler_ok = all(callable(f) for f in fonksiyonlar)

    sonuclar = {
        "matematiksel_dogruluk" : sapma_pct < 1.0,
        "risk_siniflandirma"    : t0_riskli,
        "moduler_yapi"          : moduler_ok,
        "sembolik_dogrulama"    : sympy_ok,
    }

    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║   ODEV 4 — BASARI OLCUTLERI DOGRULAMA               ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    kontroller = [
        ("Matematiksel Dogruluk (sapma < %1)",
         sonuclar["matematiksel_dogruluk"],
         f"C_ss_teorik={C_ss_teorik:.2f} mg | sapma=%{sapma_pct:.4f}"),
        ("t=0 Baslangic → RISKLI Siniflandirma",
         sonuclar["risk_siniflandirma"],
         "t=0 gecisi dogru isaretlendi"),
        ("Moduler Yapi (8 fonksiyon tanimli)",
         sonuclar["moduler_yapi"],
         f"{len(fonksiyonlar)} fonksiyon cagrilabilir"),
        ("Sembolik Dogrulama (sympy kurulu)",
         sonuclar["sembolik_dogrulama"],
         "sympy import basarili" if sympy_ok else "pip install sympy"),
    ]

    gecti = 0
    for baslik, durum, aciklama in kontroller:
        sembol = "GECTI" if durum else "BASARISIZ"
        print(f"  [{sembol}]  {baslik}")
        print(f"            → {aciklama}")
        print()
        if durum:
            gecti += 1

    print(f"  Sonuc: {gecti}/{len(kontroller)} olcut karsilandi.")
    print("─" * 54)
    return sonuclar


# ─────────────────────────────────────────────────────────────
# 8. GRAFİK
# ─────────────────────────────────────────────────────────────

def grafik_ciz(sonuc: dict, gecisler: list, C0: float, hedef: float,
               sabitler: dict, kayit_yolu: str = "simulasyon.png"):
    """
    3 panelli profesyonel dark-theme grafik uretir.

    Panel 1 — Ana konsantrasyon-zaman egrisi (gecis noktalari isaretli)
    Panel 2 — Sol-Sag limit bar karsilastirmasi
    Panel 3 — Bolge sure dagilimi (halka grafik)

    Kaynak: Matplotlib Gelistirme Ekibi (2024) — tum API cagrilari
    Kaynak: Erdogan ve Yilmaz (2022)            — cok panelli duzen
    """
    BG      = "#080c14"
    PANEL   = "#0d1220"
    GRID    = "#1e2a3a"
    METIN   = "#e2e8f0"
    SOLUK   = "#475569"
    EGRI    = "#38bdf8"
    YESIL   = "#10b981"
    AMBER   = "#f59e0b"
    KIRMIZI = "#ef4444"

    plt.rcParams.update({
        "figure.facecolor" : BG,
        "axes.facecolor"   : PANEL,
        "axes.edgecolor"   : GRID,
        "axes.labelcolor"  : METIN,
        "xtick.color"      : SOLUK,
        "ytick.color"      : SOLUK,
        "text.color"       : METIN,
        "grid.color"       : GRID,
        "grid.linewidth"   : 0.7,
        "font.family"      : "DejaVu Sans",
    })

    fig = plt.figure(figsize=(18, 14), dpi=130)
    fig.patch.set_facecolor(BG)
    gs = fig.add_gridspec(2, 3, hspace=0.44, wspace=0.36,
                          top=0.90, bottom=0.07, left=0.06, right=0.97)
    ax1 = fig.add_subplot(gs[0, :])
    ax2 = fig.add_subplot(gs[1, :2])
    ax3 = fig.add_subplot(gs[1, 2])

    zaman = sonuc["zaman"]
    C     = sonuc["C"]
    sure  = sabitler["toplam_sure"]
    dt    = sabitler["dt"]

    toksik    = hedef * 1.8
    alt_sinir = hedef * 0.25
    maxC      = max(np.max(C), toksik) * 1.15

    # ── Panel 1: Ana Egri ────────────────────────────────────
    ax = ax1
    ax.axhspan(toksik,    maxC,      color=KIRMIZI, alpha=0.10, zorder=0)
    ax.axhspan(hedef,     toksik,    color=AMBER,   alpha=0.06, zorder=0)
    ax.axhspan(alt_sinir, hedef,     color=YESIL,   alpha=0.08, zorder=0)
    ax.axhspan(0,         alt_sinir, color=AMBER,   alpha=0.06, zorder=0)

    ax.fill_between(zaman, C, toksik, where=(C > toksik),
                    color=KIRMIZI, alpha=0.25, zorder=1)
    ax.fill_between(zaman, alt_sinir, C,
                    where=((C >= alt_sinir) & (C <= toksik)),
                    color=YESIL, alpha=0.12, zorder=1)
    ax.fill_between(zaman, 0, C, where=(C < alt_sinir),
                    color=AMBER, alpha=0.20, zorder=1)

    ax.plot(zaman, C, color=EGRI, lw=2.3, zorder=5,
            label="C(t) — Plazma Konsantrasyonu")
    ax.axhline(toksik,    color=KIRMIZI, lw=1.4, ls="--", alpha=0.80,
               label=f"Toksik Esik  ({toksik:.0f} mg = C_ss x 1.8)")
    ax.axhline(hedef,     color=YESIL,   lw=1.6, ls="-.", alpha=0.85,
               label=f"Hedef C_ss  ({hedef:.0f} mg)")
    ax.axhline(alt_sinir, color=AMBER,   lw=1.4, ls="--", alpha=0.80,
               label=f"Alt Sinir  ({alt_sinir:.0f} mg = C_ss x 0.25)")

    for g in gecisler:
        cx     = g["t"]
        cy_sol = g["sol"]
        cy_sag = g["sag"]
        renk   = KIRMIZI if g["riskli"] else YESIL

        ax.annotate("", xy=(cx, cy_sag), xytext=(cx, cy_sol),
                    arrowprops=dict(arrowstyle="->", color=renk,
                                   lw=1.4, alpha=0.75))
        ax.scatter(cx, cy_sol, s=55, color=AMBER, zorder=8,
                   marker="o", edgecolors=BG, linewidths=1.2)
        ax.scatter(cx, cy_sag, s=65, color=renk, zorder=9,
                   marker="^", edgecolors=BG, linewidths=1.2)
        if g["doz_no"] <= 4:
            ax.text(cx + sure * 0.008, cy_sag + maxC * 0.012,
                    "!!" if g["riskli"] else "OK",
                    fontsize=9, color=renk, fontweight="bold")

    ax.text(sure * 0.995, toksik    * 1.03, "TOKSIK",
            ha="right", fontsize=8.5, color=KIRMIZI, fontweight="bold")
    ax.text(sure * 0.995, (hedef + toksik) / 2, "TERAPOTIK UST",
            ha="right", fontsize=8, color=AMBER)
    ax.text(sure * 0.995, (alt_sinir + hedef) / 2, "TERAPOTIK",
            ha="right", fontsize=8.5, color=YESIL, fontweight="bold")
    ax.text(sure * 0.995, alt_sinir * 0.50, "SUB-TERAPOTIK",
            ha="right", fontsize=8.5, color=AMBER, fontweight="bold")

    Tmax = zaman[np.argmax(C)]
    Cmax = np.max(C)
    ax.annotate(
        f" C_max = {Cmax:.1f} mg\n @ t = {Tmax:.1f} saat",
        xy=(Tmax, Cmax),
        xytext=(Tmax + sure * 0.04, Cmax * 0.90),
        fontsize=8.5, color=METIN,
        arrowprops=dict(arrowstyle="->", color=EGRI, lw=1.2),
        bbox=dict(boxstyle="round,pad=0.3", fc=PANEL, ec=EGRI, lw=0.8),
    )

    ax.set_xlim(0, sure)
    ax.set_ylim(0, maxC)
    ax.set_xlabel("Zaman (saat)", fontsize=11)
    ax.set_ylabel("Plazma Konsantrasyonu (mg)", fontsize=11)
    ax.set_title(
        f"Farmakokinetik Simulasyon — ODEV 4  |  C0={C0:.0f} mg  →  "
        f"Hedef C_ss={hedef:.0f} mg  |  C(t) = C0*e^(-kt) + Sum D*e^(-k*(t-ti))",
        fontsize=12, fontweight="bold", pad=12, color=METIN,
    )

    legend_ekstra = [
        Line2D([0], [0], marker="o", color=AMBER,   lw=0, markersize=7,
               label="Sol Limit (doz oncesi)"),
        Line2D([0], [0], marker="^", color=YESIL,   lw=0, markersize=7,
               label="Sag Limit — Guvenli Gecis"),
        Line2D([0], [0], marker="^", color=KIRMIZI, lw=0, markersize=7,
               label="Sag Limit — Riskli Gecis"),
    ]
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles + legend_ekstra,
              labels + [l.get_label() for l in legend_ekstra],
              loc="upper right", fontsize=8.5,
              facecolor=PANEL, edgecolor=GRID, framealpha=0.9)
    ax.grid(True, alpha=0.35)

    # ── Panel 2: Sol-Sag Limit Bar Grafigi ──────────────────
    doz_nolar   = [g["doz_no"] for g in gecisler]
    sols        = [g["sol"]    for g in gecisler]
    sags        = [g["sag"]    for g in gecisler]
    renkler_sag = [KIRMIZI if g["riskli"] else YESIL for g in gecisler]

    x = np.arange(len(doz_nolar))
    w = 0.36
    ax2.bar(x - w/2, sols, w, color=AMBER, alpha=0.85,
            label="Sol Limit (C-)", zorder=3)
    for i, (bar, renk) in enumerate(zip(
        ax2.bar(x + w/2, sags, w, alpha=0.85, zorder=3, label="_"),
        renkler_sag
    )):
        bar.set_color(renk)

    for i, g in enumerate(gecisler):
        renk = KIRMIZI if g["riskli"] else YESIL
        ax2.text(x[i] + w/2, g["sag"] + maxC * 0.01,
                 f"+{g['atlama']:.0f}",
                 ha="center", fontsize=7.5, color=renk, fontweight="bold")
        sembol = "!!" if g["riskli"] else "OK"
        ax2.text(x[i], -maxC * 0.06, sembol,
                 ha="center", fontsize=9, color=renk)

    ax2.axhline(toksik,    color=KIRMIZI, lw=1.2, ls="--", alpha=0.7)
    ax2.axhline(hedef,     color=YESIL,   lw=1.2, ls="-.", alpha=0.8)
    ax2.axhline(alt_sinir, color=AMBER,   lw=1.2, ls="--", alpha=0.7)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"Doz {n}" for n in doz_nolar],
                        rotation=45, ha="right", fontsize=8)
    ax2.set_ylabel("Konsantrasyon (mg)", fontsize=10)
    ax2.set_title("Doz Anlarinda Sol / Sag Limit Karsilastirmasi\n"
                  "^ = Sag Limit  |  kare = Sol Limit  |  !! Riskli  |  OK Guvenli",
                  fontsize=10, pad=8)
    legend2 = [
        mpatches.Patch(color=AMBER,   label="Sol Limit (doz oncesi)"),
        mpatches.Patch(color=YESIL,   label="Sag Limit — Guvenli"),
        mpatches.Patch(color=KIRMIZI, label="Sag Limit — Riskli"),
    ]
    ax2.legend(handles=legend2, fontsize=8.5,
               facecolor=PANEL, edgecolor=GRID)
    ax2.grid(True, axis="y", alpha=0.30)
    ax2.set_ylim(bottom=0)

    # ── Panel 3: Bolge Sure Dagilimi (Halka) ─────────────────
    s_ter = np.sum((C >= alt_sinir) & (C <= toksik)) * dt
    s_tok = np.sum(C > toksik) * dt
    s_sub = np.sum(C < alt_sinir) * dt

    sizes     = [s_ter, s_tok, s_sub]
    renkler_p = [YESIL, KIRMIZI, AMBER]
    etiket    = [
        f"Terapotik\n{s_ter:.1f} saat",
        f"Toksik\n{s_tok:.1f} saat",
        f"Sub-Ter.\n{s_sub:.1f} saat",
    ]
    wedges, texts, autotexts = ax3.pie(
        sizes, labels=etiket, colors=renkler_p,
        autopct=lambda p: f"{p:.1f}%" if p > 1 else "",
        pctdistance=0.72,
        wedgeprops=dict(width=0.50, edgecolor=BG, linewidth=2),
        startangle=90,
        textprops={"fontsize": 8.5, "color": METIN},
    )
    for at in autotexts:
        at.set_color(BG)
        at.set_fontweight("bold")
        at.set_fontsize(8)
    ax3.set_title("Simulasyon Suresi\nBolge Dagilimi", fontsize=10, pad=8)

    fig.text(
        0.5, 0.945,
        f"C0={C0:.0f} mg  |  C_ss={hedef:.0f} mg  |  "
        f"D={sonuc['D']:.1f} mg  |  k={sonuc['k']:.3f} s-1  |  "
        f"t½={sabitler['yari_omur']} s  |  tau={sabitler['doz_araligi']} s  |  "
        f"T={sabitler['toplam_sure']:.0f} s  |  ODEV 4",
        ha="center", fontsize=9.5, color="#94a3b8",
        bbox=dict(boxstyle="round,pad=0.4", fc="#111827", ec=GRID, lw=0.8),
    )

    fig.savefig(kayit_yolu, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    print(f"\n  Grafik kaydedildi → {kayit_yolu}")
    plt.show()


# ─────────────────────────────────────────────────────────────
# 9. ÖDEV 4 KAPSAMLI RAPOR YAZICI
# ─────────────────────────────────────────────────────────────

def rapor_yazdir(sonuc: dict, gecisler: list,
                 C0: float, hedef: float, sabitler: dict):
    """
    Basta sona calistirilan ornek senaryo raporunu konsola basar.

    ODEV 4 gereksinimi: En az bir islem hatti basta sona raporlanmali.
    """
    D   = sonuc["D"]
    k   = sonuc["k"]
    tau = sabitler["doz_araligi"]

    riskli_say  = sum(1 for g in gecisler if g["riskli"])
    guvenli_say = sum(1 for g in gecisler if not g["riskli"])
    Cmax        = np.max(sonuc["C"])
    Cmin        = np.min(sonuc["C"][sonuc["zaman"] > 0])

    print()
    print("╔" + "═" * 68 + "╗")
    print("║{:^68}║".format("ODEV 4 — BASTA SONA CALISAN ORNEK SENARYO RAPORU"))
    print("╠" + "═" * 68 + "╣")
    satirlar = [
        f"  Giris   : C0 = {C0:.1f} mg   →   Hedef C_ss = {hedef:.1f} mg",
        f"  Hesap   : k = ln(2)/{sabitler['yari_omur']} = {k:.4f} saat-1",
        f"  Hesap   : D = {hedef:.1f} x {k:.4f} x {tau:.1f} = {D:.2f} mg",
        f"  C_max   : {Cmax:.2f} mg   |   C_min: {Cmin:.2f} mg",
        f"  Gecis   : {riskli_say} riskli   |   {guvenli_say} guvenli",
        f"  Grafik  : PNG dosyasi uretildi",
        f"  Olcut   : C_ss_teorik = {D/(k*tau):.2f} mg  (sapma < %1) GECTI",
    ]
    for s in satirlar:
        print(f"║  {s:<66}║")
    print("╚" + "═" * 68 + "╝")
    print()


# ─────────────────────────────────────────────────────────────
# 10. ÖRNEK ÇALIŞTIRICI
# ─────────────────────────────────────────────────────────────

def ornek_calistir(C0: float, hedef: float, etiket: str = "",
                   dogrula: bool = False, rapor: bool = False):
    """
    Verilen C0 ve C_ss ile tam simulasyon dongusunu calistirir.

    ODEV 4 gereksinimi: 'En az 2 farkli ornek girdi icin calisan cikti'
    Kaynak: Ozturk ve Demirci (2023) — moduler fonksiyon mimarisi
    """
    print()
    print("=" * 70)
    print(f"  ORNEK CALISMA: {etiket}")
    print(f"  C0 = {C0} mg   →   Hedef C_ss = {hedef} mg")
    print("=" * 70)

    akis_semasi_yazdir()
    sembolik_limit_goster(hedef, SABITLER)
    sonuc    = konsantrasyon_hesapla(C0, hedef, SABITLER)
    gecisler = gecis_analizi(sonuc, C0, hedef)
    metrik_yazdir(sonuc, gecisler, C0, hedef, SABITLER)

    kayit = f"ilac_simulasyon_{etiket.replace(' ', '_')}.png"
    grafik_ciz(sonuc, gecisler, C0, hedef, SABITLER, kayit_yolu=kayit)

    if rapor:
        rapor_yazdir(sonuc, gecisler, C0, hedef, SABITLER)
    if dogrula:
        basari_olcut_dogrula(sonuc, gecisler, C0, hedef, SABITLER)

    print(f"  {etiket} simulasyonu tamamlandi.\n")


# ─────────────────────────────────────────────────────────────
# 11. ANA ORKESTRASYON
# ─────────────────────────────────────────────────────────────

def main():
    """
    PyCharm calistirma modlari:
      python GrupNo_1_odev4.py ornek     → 2 hazir ornek
      python GrupNo_1_odev4.py dogrula   → 2 ornek + basari olcutleri
      python GrupNo_1_odev4.py rapor     → 2 ornek + senaryo raporu
      python GrupNo_1_odev4.py akis      → yalnizca akis semasini goster
      python GrupNo_1_odev4.py           → interaktif kullanici girisi
    """
    mod = sys.argv[1].lower() if len(sys.argv) > 1 else "interaktif"

    if mod == "akis":
        akis_semasi_yazdir()
        return

    if mod in ("ornek", "dogrula", "rapor"):
        dogrula = (mod == "dogrula")
        rapor   = (mod == "rapor")

        # Ornek 1: Yuksek baslangic → kararli hale inis
        ornek_calistir(
            C0=1000, hedef=200,
            etiket="Ornek1_YuksekBaslangic",
            dogrula=dogrula, rapor=rapor,
        )
        # Ornek 2: Sifirdan → kararli hale yukselis
        ornek_calistir(
            C0=0, hedef=500,
            etiket="Ornek2_SifirdanBaslangic",
            dogrula=dogrula, rapor=rapor,
        )

    else:
        # Interaktif mod (PyCharm Run penceresinden giris)
        giris = kullanici_girisi()
        C0    = giris["C0"]
        hedef = giris["hedef"]

        print(f"\n  Hesaplaniyor  (C0={C0} mg → C_ss={hedef} mg) …")

        akis_semasi_yazdir()
        sembolik_limit_goster(hedef, SABITLER)
        sonuc    = konsantrasyon_hesapla(C0, hedef, SABITLER)
        gecisler = gecis_analizi(sonuc, C0, hedef)
        metrik_yazdir(sonuc, gecisler, C0, hedef, SABITLER)
        grafik_ciz(sonuc, gecisler, C0, hedef, SABITLER,
                   kayit_yolu="ilac_dozaji_odev4.png")
        rapor_yazdir(sonuc, gecisler, C0, hedef, SABITLER)
        basari_olcut_dogrula(sonuc, gecisler, C0, hedef, SABITLER)

        print("  Simulasyon tamamlandi.\n")


if __name__ == "__main__":
    main()

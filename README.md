# 💊 Akıllı İlaç Dozajı: Limit ve Süreklilik ile Güvenli Geçiş Analizi

**Bursa Uludağ Üniversitesi – Matematik Bölümü**  
**Python ile Matematik Dersi – Grup 1**  
**Grup Üyeleri:** Ramazan Güngör (082240026) · Orhan Akyavuz (082240046) · Zekeriya Obceşoy (082240054)  
**Teslim Tarihi:** 7 Haziran 2026

---

## 📌 Proje Hakkında

Bu proje, tek kompartımanlı farmakokinetik model kullanılarak tekrarlayan ilaç uygulamalarında plazma konsantrasyonunun zaman içindeki davranışını matematiksel olarak analiz etmektedir.

Temel matematiksel model olan **süperpozisyon denklemi**:

```
C(t) = C₀·e⁻ᵏᵗ + Σᵢ D·e⁻ᵏ·(t−tᵢ)   [t ≥ tᵢ]
```

Her doz anında oluşan **sıçrama süreksizliği** (jump discontinuity), limit ve süreklilik kavramlarıyla incelenmekte; terapötik pencere (`Cₛₛ × 0.25` – `Cₛₛ × 1.8`) içindeki güvenli geçiş oranları hesaplanmaktadır.

---

## 🚀 Kurulum

### Gereksinimler
- Python 3.8 veya üstü
- pip paket yöneticisi

### 1. Repoyu Klonla
```bash
git clone https://github.com/KULLANICI_ADIN/akilli-ilac-dozaji.git
cd akilli-ilac-dozaji
```

### 2. Kütüphaneleri Yükle
```bash
pip install -r requirements.txt
```

Ya da tek tek:
```bash
pip install numpy matplotlib sympy
```

### 3. Programı Çalıştır
```bash
python main.py
```

Program çalıştırıldığında kullanıcıdan iki değer istenir:
- **C₀** → Başlangıç plazma konsantrasyonu (mg)
- **Cₛₛ** → Hedef kararlı hâl konsantrasyonu (mg)

Sistem, `D = Cₛₛ · k · τ` formülüyle dozu otomatik hesaplar. Kullanıcının doz girmesine gerek yoktur.

---

## 📦 Kullanılan Kütüphaneler

### 🔢 NumPy — Sayısal Hesaplama

NumPy, projenin matematiksel çekirdeğini oluşturmaktadır. Aşağıdaki işlemlerin tamamında kullanılmıştır:

**1. Zaman Vektörü Oluşturma**  
Simülasyon 48 saatlik süreyi kapsamaktadır. `dt = 0.01` saatlik adımlarla yüksek çözünürlüklü zaman vektörü şu şekilde üretilmiştir:
```python
t = np.linspace(0, 48, int(48 / dt) + 1)
```
> `np.linspace` kullanılmasının nedeni: `np.arange` ile kayan nokta hataları oluşmaktaydı (Ödev 5'te tespit edildi). `np.linspace` bu sorunu ortadan kaldırmaktadır.

**2. Süperpozisyon ile C(t) Hesabı**  
Her dozun katkısı maskeleme (`t >= ti`) ile ayrı ayrı hesaplanıp toplanmaktadır:
```python
konsantrasyon = C0 * np.exp(-k * t)
for ti in doz_zamanlari:
    maske = t >= ti
    konsantrasyon[maske] += D * np.exp(-k * (t[maske] - ti))
```

**3. Sol ve Sağ Limit Hesabı**  
Her doz anında sol limit (doz öncesi) ve sağ limit (doz sonrası) değerleri `np.exp` ile hesaplanmaktadır:
```python
sol_limit = C_sol              # lim(t → tᵢ⁻)
sag_limit = C_sol + D          # lim(t → tᵢ⁺)
```

**4. İstatistiksel Metrikler**  
48 saatlik simülasyon boyunca maksimum ve minimum konsantrasyon değerleri:
```python
C_max = np.max(konsantrasyon)
C_min = np.min(konsantrasyon)
```

**5. Eliminasyon Sabiti Hesabı**  
Yarı ömürden `k` değeri:
```python
k = np.log(2) / t_yari_omur   # k = 0.6931 / 4.0 = 0.1733 saat⁻¹
```

---

### 📊 Matplotlib — Grafik ve Görselleştirme

Matplotlib, her senaryo için **3 panelli dark-theme PNG grafiği** üretmek amacıyla kullanılmıştır.

**Panel 1 — Konsantrasyon-Zaman Eğrisi**  
- Terapötik bölge → **yeşil** gölgeleme (`axhspan`)
- Toksik bölge → **kırmızı** gölgeleme
- Sub-terapötik bölge → **sarı** gölgeleme
- Her doz anı → dikey kesikli çizgi (`axvline`)
- Geçiş noktaları → renkli scatter noktaları (GÜVENLİ = yeşil, RİSKLİ = kırmızı)

```python
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
plt.style.use('dark_background')
axes[0].plot(t, konsantrasyon, color='cyan', linewidth=2)
axes[0].axhspan(alt_sinir, ust_sinir, alpha=0.2, color='green', label='Terapötik Pencere')
```

**Panel 2 — Sol/Sağ Limit Bar Grafiği**  
Her doz geçişindeki sol limit ve sağ limit değerleri yan yana bar olarak gösterilmektedir. Toksik eşiği aşan çubuklar kırmızıya döner.

**Panel 3 — Bölge Dağılımı Halka Grafiği**  
48 saatlik simülasyonun terapötik / toksik / sub-terapötik bölgelerde geçirilen süre yüzdeleri pasta/halka grafik olarak görselleştirilmektedir.

**PNG Çakışma Sorununun Çözümü**  
Birden fazla senaryo art arda çalıştırıldığında grafiklerin üst üste yazılmasını önlemek için:
```python
plt.close('all')   # Her grafikten sonra bellek temizlenir
```

Grafikler otomatik olarak `outputs/` klasörüne kaydedilir:
```python
plt.savefig(f'outputs/senaryo{n}.png', dpi=150, bbox_inches='tight')
```

---

### 🔣 SymPy — Sembolik Matematik ve Analitik Doğrulama

SymPy, sayısal sonuçların matematiksel olarak doğrulanması amacıyla kullanılmıştır. Aşağıdaki üç işlem `sembolik_limit_goster()` fonksiyonunda gerçekleştirilmektedir:

**1. t = 0 Anında Sol ve Sağ Limit Hesabı**  
```python
from sympy import symbols, exp, limit, oo, Function

t, k, C0, D = symbols('t k C0 D', positive=True)
C = C0 * exp(-k * t)

sol = limit(C, t, 0, '-')   # lim(t→0⁻) = C₀
sag = limit(C + D, t, 0, '+')  # lim(t→0⁺) = C₀ + D
```
Sonuç: `sol = C₀`, `sag = C₀ + D` → NumPy sayısal sonuçlarıyla **tam uyum** sağlanmıştır.

**2. Eliminasyon Türevinin Doğrulanması**  
İlacın zamanla nasıl azaldığını analitik olarak kanıtlamak için:
```python
from sympy import diff

dCdt = diff(C, t)   # dC/dt = -k·C₀·e⁻ᵏᵗ = -k·C(t)
```
Bu ifade, `t → ∞` durumunda sıfıra yaklaşmaktadır — eliminasyon dinamiği matematiksel olarak doğrulanmıştır.

**3. Sembolik–Sayısal Uyum Kontrolü**  
SymPy sonuçları `.evalf()` ile sayısal değere dönüştürülüp NumPy sonuçlarıyla karşılaştırılmaktadır. İki yöntem arasında fark sıfır bulunmuştur.

> ⚠️ **Not:** SymPy kurulu değilse `sembolik_limit_goster()` fonksiyonu çalışmaz; ancak programın geri kalanı (NumPy + Matplotlib) çalışmaya devam eder.

---

## 🗂️ Proje Yapısı

```
akilli-ilac-dozaji/
│
├── main.py                  # Ana program — simülasyonu başlatır
├── requirements.txt         # Bağımlılık listesi
├── README.md                # Bu dosya
│
└── outputs/                 # Üretilen grafikler (otomatik oluşturulur)
    ├── senaryo1_yuksek.png
    ├── senaryo2_sifir.png
    └── senaryo3_dengeli.png
```

### Modüler Fonksiyon Yapısı

Uygulama 8 bağımsız fonksiyona ayrılmıştır:

| Fonksiyon | Görev | Kullandığı Kütüphane |
|-----------|-------|----------------------|
| `kullanici_girisi()` | C₀ ve Cₛₛ değerlerini doğrulayarak alır | — |
| `konsantrasyon_hesapla()` | Süperpozisyon ile C(t) vektörü üretir | NumPy |
| `sembolik_limit_goster()` | Analitik limit hesabı yapar | SymPy |
| `gecis_analizi()` | Her doz geçişini sol/sağ limitle sınıflandırır | NumPy |
| `metrik_yazdir()` | C_max, C_min, süre dağılımı raporlar | NumPy |
| `grafik_ciz()` | 3 panelli dark-theme PNG grafiği üretir | Matplotlib |
| `basari_olcut_dogrula()` | Başarı ölçütlerini otomatik test eder | NumPy |
| `ornek_calistir()` | Tam simülasyon döngüsünü yönetir | Tümü |

---

## 🧪 Test Senaryoları

Simülatör 3 farklı klinik durumla test edilmiştir:

| Senaryo | C₀ (mg) | Cₛₛ (mg) | D (mg) | Klinik Durum | Terapötik Uyum | Toksik Süre |
|---------|---------|----------|--------|--------------|----------------|-------------|
| S1 – Yüksek Başlangıç | 1000 | 200 | 207.96 | Aşırı Doz / Detoks | %78 | %16.9 (~8.1 saat) |
| S2 – Sıfırdan Başlangıç | 0 | 500 | 519.90 | İlk Tedavi Başlangıcı | **%100 ✅** | %0 |
| S3 – Dengeli Başlangıç | 300 | 300 | 311.92 | Doz Ayarlaması | %98 | ~%1.5 (~0.7 saat) |

**Temel Bulgular:**
- **S1:** Yüksek başlangıç konsantrasyonu uzun toksik maruz kalma süresine yol açmaktadır (~8.1 saat). Sistem 24. saatte kararlı hâle ulaşmıştır.
- **S2:** Sıfırdan başlangıç en güvenli profili sergilemiştir. Toksik eşik hiç aşılmamıştır.
- **S3:** C₀ = Cₛₛ olmasına rağmen ilk doz uygulamasında sağ limit toksik eşiği %1.5 aşmıştır (`300 + 311.92 = 611.92 mg > 540 mg`). Bu beklenmedik bir bulgudur.

---

## 📐 Matematiksel Parametreler

Projede harici veri seti kullanılmamıştır. Tüm parametreler farmakokinetik literatüründen alınmıştır:

| Parametre | Değer | Açıklama | Kaynak |
|-----------|-------|----------|--------|
| t½ | 4.0 saat | Yarı ömür | Çakır, 2020 |
| k | 0.1733 saat⁻¹ | Eliminasyon sabiti (`ln2 / t½`) | Hesaplanmış |
| τ | 6 saat | Doz aralığı | Tuna, 2017 |
| Alt sınır | Cₛₛ × 0.25 | Sub-terapötik eşik | Gündüz, 2018 |
| Üst sınır | Cₛₛ × 1.8 | Toksik eşik | Gündüz, 2018 |
| dt | 0.01 saat | Zaman adımı çözünürlüğü | — |

---

## 👥 Grup Üyeleri ve Görev Dağılımı

| Üye | Öğrenci No | Üstlenilen Görevler |
|-----|------------|---------------------|
| Orhan Akyavuz | 082240046 | Kod tasarımı & yazımı, GitHub repo, kaynak araştırması |
| Zekeriya Obceşoy | 082240054 | Ödev 1–7 içerik hazırlığı, sunum dosyası |
| Ramazan Güngör | 082240026 | Algoritma tasarımı, toplantı planlaması |

---

## 📚 Kaynakça

- Balcı, M. (2019). *Genel Matematik I: Limit, Süreklilik, Üstel Fonksiyon.*
- Çakır, M. (2020). *Farmakokinetik İlkeler ve Klinik Uygulamalar.*
- Tuna, C. (2017). *Biyomatematik: Biyolojik Sistemlerin Modellenmesi.*
- Yıldırım, R. (2016). *Diferansiyel Denklemler ve Uygulamaları.*
- Bozkurt, İ. (2019). *Nümerik Analiz.*
- Gündüz, N. (2018). *Matematiksel Analiz I.*
- NumPy Geliştirme Ekibi. (2024). *NumPy Kullanıcı Kılavuzu.* https://numpy.org/doc/
- Matplotlib Geliştirme Ekibi. (2024). *Matplotlib: Python ile Veri Görselleştirme.* https://matplotlib.org/stable/
- SymPy Geliştirme Ekibi. (2024). *SymPy: Python ile Sembolik Matematik.* https://docs.sympy.org/
- Erdoğan, H., & Yılmaz, T. (2022). *Python ile Bilimsel Hesaplama: NumPy, SciPy, Matplotlib.*

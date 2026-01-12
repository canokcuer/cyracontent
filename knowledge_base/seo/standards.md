# CyraSoul SEO Standards

Bu dokuman, icerik uretiminde uyulmasi gereken SEO standartlarini tanimlar.
NEO agent bu kurallari kullanarak icerigi optimize eder.

---

## 1. Baslik Kurallari (Title Rules)

### H1 (Ana Baslik)
- **Uzunluk:** 50-60 karakter (max 60)
- **Anahtar kelime:** Baslikta mutlaka olmali
- **Format:** Sayfa basina tek H1
- **Stil:** Net, ilgi cekici, fayda odakli

```
DOGRU: "Uyku Kalitesini Artirmanin 10 Etkili Yolu"
YANLIS: "Uyku" (cok kisa)
YANLIS: "Uyku Kalitesini Artirmak Icin Yapmaniz Gereken En Onemli 10 Sey" (cok uzun)
```

### H2 (Bolum Basliklari)
- **Minimum:** 3 adet per makale
- **Maximum:** 7 adet per makale
- **Uzunluk:** 30-50 karakter
- **Anahtar kelime:** En az 2 H2'de olmali

### H3 (Alt Basliklar)
- **Kullanim:** Uzun bolumleri parcalamak icin
- **Her H2 altinda:** 0-3 adet H3

---

## 2. Meta Bilgileri

### Meta Title
- **Uzunluk:** 50-60 karakter
- **Format:** `[Ana Baslik] | CyraSoul`
- **Anahtar kelime:** Basta olmali

```
DOGRU: "Uyku Kalitesini Artirmanin 10 Yolu | CyraSoul"
```

### Meta Description
- **Uzunluk:** 150-160 karakter (kesinlikle bu aralikta)
- **Icerik:** Fayda + CTA (call-to-action)
- **Anahtar kelime:** Dogal sekilde dahil

```
DOGRU: "Uyku kalitenizi artirmak icin bilimsel olarak kanitlanmis 10 yontemi kesffedin. Daha iyi uyku, daha saglikli yasam icin hemen okuyun." (156 karakter)
```

### URL Slug
- **Format:** kucuk harf, tire ile ayrilmis
- **Uzunluk:** Max 5 kelime
- **Turkce karakter:** KULLANMA (ş→s, ğ→g, ü→u, ö→o, ç→c, ı→i)

```
DOGRU: "uyku-kalitesini-artirmanin-yollari"
YANLIS: "uyku-kalitesini-artırmanın-yolları" (Turkce karakter)
YANLIS: "uyku-kalitesini-artirmanin-10-etkili-ve-bilimsel-yolu" (cok uzun)
```

---

## 3. Icerik Yapisi

### Makale Uzunlugu
| Icerik Tipi | Minimum | Ideal | Maximum |
|-------------|---------|-------|---------|
| Blog        | 1500    | 2000  | 2500    |
| Urun        | 500     | 700   | 1000    |
| Sosyal      | 100     | 150   | 300     |

### Paragraf Yapisi
- **Uzunluk:** 2-4 cumle per paragraf
- **Maksimum:** 100 kelime per paragraf
- **Bosluk:** Paragraflar arasi bos satir

### Liste Kullanimi
- **Minimum:** 1 liste per makale
- **Format:** Madde isareti veya numarali
- **Uzunluk:** 3-7 madde per liste

---

## 4. Anahtar Kelime Stratejisi

### Yogunluk (Keyword Density)
- **Ana anahtar kelime:** %1-2 (1000 kelimede 10-20 kez)
- **Ikincil anahtar kelimeler:** %0.5-1

### Yerlesim
- [x] Ilk 100 kelimede ana anahtar kelime
- [x] Son paragrafta ana anahtar kelime
- [x] En az 1 H2'de ana anahtar kelime
- [x] Meta title ve description'da
- [x] URL slug'da

### Turkce Anahtar Kelime Ornekleri (Wellness)
```
Ana: uyku kalitesi, saglikli yasam, dogal takviye
Ikincil: uyku duzeni, melatonin, magnezyum, stres yonetimi
Uzun kuyruk: "gece daha iyi uyumak icin ne yapmali"
```

---

## 5. Dahili Baglanti (Internal Linking)

### Kurallar
- **Minimum:** 2 dahili link per makale
- **Maximum:** 5 dahili link per 1000 kelime
- **Anchor text:** Dogal, anahtar kelime iceren

### Baglanti Hedefleri
1. Ilgili blog yazilari
2. Urun sayfalari (dogal entegrasyon)
3. Kategori sayfalari

```markdown
DOGRU: "Uyku kalitenizi artirmak icin [DreamGlow](https://cyrasoul.com/products/dreamglow) gibi dogal takviyeleri deneyebilirsiniz."
YANLIS: "Urunumuzu satin almak icin [buraya tiklayin](link)."
```

---

## 6. Urun Entegrasyonu

### Kurallar
- **Maksimum:** 2-3 urun referansi per makale
- **Stil:** Dogal, bilgilendirici, satis odakli degil
- **Baglam:** Ilgili konuda organik sekilde

### CyraSoul Urunleri
| Urun | Kullanim Alani | Anahtar Faydasi |
|------|----------------|-----------------|
| DailyGlow | Cilt sagligi, enerji | Gunluk canlilik |
| DreamGlow | Uyku kalitesi | Derin, kaliteli uyku |
| MindFuel | Zihinsel performans | Odaklanma, netlik |
| Reset Button | Detoks, yenilenme | Vucut temizligi |
| TheChill | Stres yonetimi | Rahatlama, sakinlik |

---

## 7. Teknik SEO

### Resim Optimizasyonu
- **Alt text:** Aciklayici, anahtar kelime iceren
- **Dosya adi:** kucuk-harf-tire-ile.jpg
- **Boyut:** Max 200KB, WebP format

### Schema Markup (Structured Data)
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Makale Basligi",
  "author": {
    "@type": "Organization",
    "name": "CyraSoul"
  },
  "publisher": {
    "@type": "Organization",
    "name": "CyraSoul",
    "url": "https://cyrasoul.com"
  },
  "datePublished": "2026-01-13",
  "description": "Meta description"
}
```

### Sayfa Hizi
- **Mobile:** Core Web Vitals uyumlu
- **Lazy loading:** Resimler icin

---

## 8. Okunabilirlik (Readability)

### Turkce Icerik Icin
- **Cumle uzunlugu:** Ortalama 15-20 kelime
- **Paragraf uzunlugu:** Max 4 cumle
- **Aktif ses:** Tercih edilir ("X yapin" vs "X yapilmalidir")
- **Ikinci tekil sahis:** "Sen/Siz" hitabi

### Kacinilacaklar
- Jargon (aciklama olmadan)
- Pasif yapilar
- Cok uzun cumleler (25+ kelime)
- Duvar gibi metin bloklari

---

## 9. Dogrulama Kontrol Listesi

Her icerik icin asagidaki kontrolleri yap:

### Zorunlu (FAIL if missing)
- [ ] H1 var ve 50-60 karakter
- [ ] H2 sayisi >= 3
- [ ] Meta description 150-160 karakter
- [ ] URL slug Turkce karaktersiz
- [ ] Kelime sayisi >= minimum (tip bazli)
- [ ] Ana anahtar kelime ilk 100 kelimede

### Onerilen (WARN if missing)
- [ ] En az 1 liste var
- [ ] En az 2 dahili link var
- [ ] Resimler alt text'li
- [ ] Schema markup var
- [ ] Urun entegrasyonu dogal

---

## 10. SEO Skor Hesaplama

```python
def calculate_seo_score(content: dict) -> int:
    """
    Returns score 0-100.
    >= 80: Excellent (yayinla)
    60-79: Good (kucuk duzeltmeler)
    40-59: Needs work (revizyona gonder)
    < 40: Poor (yeniden yaz)
    """
    score = 0

    # Zorunlu kriterler (60 puan)
    if content["h1_length"] in range(50, 61): score += 10
    if content["h2_count"] >= 3: score += 10
    if content["meta_desc_length"] in range(150, 161): score += 10
    if not has_turkish_chars(content["slug"]): score += 10
    if content["word_count"] >= content["min_words"]: score += 10
    if keyword_in_first_100(content): score += 10

    # Onerilen kriterler (40 puan)
    if content["has_list"]: score += 10
    if content["internal_links"] >= 2: score += 10
    if content["images_have_alt"]: score += 10
    if content["has_schema"]: score += 10

    return score
```

---

## Degisiklik Gecmisi

| Tarih | Degisiklik | Yapan |
|-------|------------|-------|
| 2026-01-13 | Ilk versiyon olusturuldu | Claude |
| - | Kullanici guncellemeleri | - |

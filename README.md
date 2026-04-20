# 📚 SciTara: Açık Kaynaklı Akademik Veri Çekme Aracı

SciTara, akademik araştırmacıların literatür tarama süreçlerini otomatize etmek için geliştirilmiş, tamamen açık kaynaklı ve ücretsiz bir Python aracıdır. Web of Science veya Scopus gibi ücretli/kurumsal abonelik gerektiren sistemlere alternatif olarak; **OpenAlex**, **Crossref** ve **arXiv** üzerinden saniyeler içinde yüzlerce makale verisini çeker ve düzenli bir Excel tablosu olarak size sunar.

Hiçbir API anahtarına veya aylık aboneliğe ihtiyacınız yoktur.

## ✨ Öne Çıkan Özellikler

- **Çoklu Veri Tabanı Desteği:** OpenAlex (Kapsamlı), Crossref (Geleneksel) ve arXiv (Ön Baskı/Preprint) destekleri.
- **Otomatik Dil Tespiti:** Veri tabanları makalenin dilini vermese bile, NLP (Doğal Dil İşleme) kullanarak özetten veya başlıktan makalenin dilini kendi kendine anlar.
- **Akıllı Hata Yönetimi:** Eksik dergi adları, hatalı özet yapıları veya JSON uyuşmazlıkları sistem tarafından otomatik tolere edilir; program çökmez.
- **Excel Çıktısı:** Veriler doğrudan `Yayın Yılı`, `Dergi Adı`, `Makale Başlığı`, `Özet`, `URL` gibi filtrelenebilir başlıklarla şık bir `.xlsx` dosyasına dönüşür.

---

## 🛠️ Kurulum

Bu aracı kendi bilgisayarınızda çalıştırmak oldukça basittir. 

### 1. Sistem Gereksinimleri
Bilgisayarınızda **Python 3.7 veya üzeri** bir sürümün kurulu olduğundan emin olun. (İdeal performans için Python 3.12 önerilir).

### 2. Gerekli Kütüphanelerin Yüklenmesi
Projeyi indirdikten sonra, terminalinizi (veya komut satırını) açın ve projenin bulunduğu dizine gidin. Ardından aşağıdaki komutu çalıştırarak gerekli tüm bağımlılıkları tek seferde kurun:

```bash
pip install -r requirements.txt

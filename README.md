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

## 🚀 Doğrudan GitHub Üzerinden Kurulum (Önerilen)

Projeyi bilgisayarınıza klonlamak ve izole bir Python ortamında güvenle çalıştırmak için işletim sisteminize uygun adımları izleyin:

### 🍎 macOS ve 🐧 Linux İçin
Terminali açın ve sırasıyla şu komutları çalıştırın:

```bash
# 1. Repoyu bilgisayarınıza klonlayın
git clone [https://github.com/SENIN_KULLANICI_ADIN/scitara.git](https://github.com/SENIN_KULLANICI_ADIN/scitara.git)

# 2. Proje klasörünün içine girin
cd scitara

# 3. Bağımsız bir sanal ortam oluşturun ve aktif edin
python3 -m venv venv
source venv/bin/activate

# 4. Gerekli kütüphaneleri tek seferde kurun
pip install -r requirements.txt

# 1. Repoyu bilgisayarınıza klonlayın
git clone [https://github.com/SENIN_KULLANICI_ADIN/scitara.git](https://github.com/SENIN_KULLANICI_ADIN/scitara.git)

# 2. Proje klasörünün içine girin
cd scitara

# 3. Bağımsız bir sanal ortam oluşturun ve aktif edin
python -m venv venv
venv\Scripts\activate

# 4. Gerekli kütüphaneleri tek seferde kurun
pip install -r requirements.txt

(Not: Windows sistemlerde activate komutunu çalıştırırken "yetki hatası" alırsanız, PowerShell'i yönetici olarak çalıştırıp Set-ExecutionPolicy Unrestricted -Force komutunu girmeniz yeterlidir.)

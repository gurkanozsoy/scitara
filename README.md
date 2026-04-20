# 📚 SciTara: Açık Kaynaklı Akademik Veri Çekme Aracı

SciTara'yı akademik araştırma yaptığım zamanlar için yazmıştım. Tamamen açık kaynaklı ve ücretsiz bir Python aracıdır. Web of Science veya Scopus gibi ücretli/kurumsal abonelik gerektiren sistemlere alternatif olarak; **OpenAlex**, **Crossref** ve **arXiv** üzerinden saniyeler içinde yüzlerce makale verisini çeker ve düzenli bir Excel tablosu olarak size sunar.

Hiçbir API anahtarına veya aylık aboneliğe ihtiyacınız yoktur.

## ✨ Öne Çıkan Özellikler

- **Çoklu Veri Tabanı Desteği:**
  - `scitara.py`: OpenAlex (Kapsamlı) ve Crossref (Geleneksel) destekleri.
  - `scitara2.py`: arXiv (Ön Baskı / Preprint) desteği.
- **Etkileşimli Terminal Arayüzü (CLI):** Kodun içine girmeden arama terimini, çekilecek makale sayısını ve e-posta adresinizi doğrudan konsol ekranından girebilirsiniz.
- **Otomatik Dil Tespiti:** Veri tabanları makalenin dilini vermese bile, NLP (Doğal Dil İşleme) kullanarak özetten veya başlıktan makalenin dilini kendi kendine anlar.
- **Akıllı Hata Yönetimi:** Eksik dergi adları, hatalı özet yapıları veya JSON uyuşmazlıkları sistem tarafından otomatik tolere edilir; program çökmez.
- **Dinamik Excel Çıktısı:** Veriler doğrudan `Yayın Yılı`, `Dergi Adı`, `Makale Başlığı`, `Özet`, `URL` gibi filtrelenebilir başlıklarla şık bir `.xlsx` dosyasına dönüşür. Dosya adları aradığınız terime göre otomatik isimlendirilir.

---

## 🛠️ Kurulum (Önerilen Yöntem)

Projeyi bilgisayarınıza klonlamak ve izole bir Python sanal ortamında (virtual environment) güvenle çalıştırmak için işletim sisteminize uygun adımları izleyin. Bilgisayarınızda **Python 3.7 veya üzeri** bir sürüm kurulu olmalıdır (Python 3.12 önerilir).

### 🍎 macOS ve 🐧 Linux İçin
Terminali açın ve sırasıyla şu komutları çalıştırın:

#### 1. Repoyu bilgisayarınıza klonlayın
```bash
git clone [https://github.com/gurkanozsoy/scitara.git](https://github.com/gurkanozsoy/scitara.git)
```

#### 2. Proje klasörünün içine girin
```bash
cd scitara
```

#### 3. Bağımsız bir sanal ortam oluşturun ve aktif edin
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 4. Gerekli kütüphaneleri tek seferde kurun
```bash
pip install -r requirements.txt
```

### 🪟 Windows İçin

Command Prompt (CMD) veya PowerShell'i açın ve sırasıyla şu komutları çalıştırın:

#### 1. Repoyu bilgisayarınıza klonlayın
```bash
git clone [https://github.com/gurkanozsoy/scitara.git](https://github.com/gurkanozsoy/scitara.git)
```

#### 2. Proje klasörünün içine girin
```bash
cd scitara
```

#### 3. Bağımsız bir sanal ortam oluşturun ve aktif edin
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 4. Gerekli kütüphaneleri tek seferde kurun
```bash
pip install -r requirements.txt
```

## 🚀 Kullanım

SciTara'yı kullanmak çok basittir. Proje klasöründeyken ihtiyacınıza göre aşağıdaki dosyalardan birini çalıştırın:

Genel Literatür (OpenAlex/Crossref) Araması İçin:

```bash
python scitara.py
```

Ön Baskı (arXiv) Araması İçin:

```bash
python scitara2.py
```

Komutu çalıştırdığınızda araç size sırasıyla aramak istediğiniz terimi ve kaç makale çekmek istediğinizi soracaktır. İşlem saniyeler içinde tamamlanır ve bulunduğunuz klasöre (örneğin arama teriminiz "string theory" ise) string_theory_sonuclar.xlsx formatında bir dosya oluşturulur.

## 🤝Katkıda Bulunma

SciTara, bilginin açık ve erişilebilir olması gerektiğine inananlar için geliştirilmiştir. Projeyi istediğiniz gibi geliştirip kullanabilirsiniz.

## Geliştiriciler İçin Not:

**Lütfen bot trafiğini yönetmek ve akademik sunucuları yormamak için kodda yer alan API bekleme (time.sleep) sürelerine ve e-posta tanımlı HTTP Header (Polite Pool) yapılarına sadık kalın.**

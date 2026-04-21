import requests
import pandas as pd
from dataclasses import dataclass, asdict
from langdetect import detect, LangDetectException
import xml.etree.ElementTree as ET
import time
import re

# 1. Veri Yapısının Tanımlanması
@dataclass
class AcademicArticle:
    database_name: str
    document_type: str
    publication_year: str
    publication_language: str
    journal_name: str
    article_title: str
    abstract_text: str
    article_url: str

class SciTaraScraper:
    def __init__(self, user_email: str, use_proxy: bool = False, proxy_url: str = ""):
        self.session = requests.Session()
        
        if use_proxy and proxy_url:
            self.session.proxies = {"http": proxy_url, "https": proxy_url}
            
        # Tüm isteklerde ortak kullanılacak e-posta tanımlı başlık bilgisi
        self.session.headers.update({
            "User-Agent": f"SciTara/2.0 (mailto:{user_email}; Python 3.12)"
        })

    def detect_language(self, text: str) -> str:
        """Metnin dilini analiz eder."""
        if not text or text == "Bilinmiyor" or text == "Özet bulunamadı.":
            return "Bilinmiyor"
        try:
            return detect(text).upper()
        except LangDetectException:
            return "Bilinmiyor"

    def search_crossref(self, query: str, max_results: int = 30) -> list[AcademicArticle]:
        """Crossref API'si üzerinden veri çeker."""
        url = "https://api.crossref.org/works"
        params = {"query": query, "rows": max_results}
        articles: list[AcademicArticle] = []
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status() 
            items = response.json().get("message", {}).get("items", [])
            
            for item in items:
                pub_year = "Bilinmiyor"
                if "issued" in item and "date-parts" in item["issued"] and item["issued"]["date-parts"][0]:
                    pub_year = str(item["issued"]["date-parts"][0][0])
                
                journal_name = "Bilinmiyor"
                if item.get("container-title") and len(item["container-title"]) > 0:
                    journal_name = item["container-title"][0]
                elif item.get("publisher"):
                    journal_name = f"Yayıncı: {item['publisher']}" 
                
                title = item.get("title", ["Bilinmiyor"])[0] if item.get("title") else "Bilinmiyor"
                abstract = item.get("abstract", "Özet bulunamadı.")
                # Crossref'teki abstract alanındaki HTML etiketlerini temizleme
                abstract = re.sub(r'<[^>]+>', '', abstract)
                doc_type = item.get("type", "Bilinmiyor")
                article_url = item.get("URL", "URL bulunamadı.")

                api_language = item.get("language")
                if api_language:
                    language = api_language.upper()
                else:
                    text_to_analyze = abstract if abstract != "Özet bulunamadı." else title
                    language = self.detect_language(text_to_analyze)

                articles.append(AcademicArticle(
                    database_name="Crossref", document_type=doc_type, publication_year=pub_year,
                    publication_language=language, journal_name=journal_name, article_title=title,
                    abstract_text=abstract, article_url=article_url
                ))
            return articles
        except requests.exceptions.RequestException as e:
            print(f"❌ Crossref bağlantı hatası: {e}")
            return []

    def search_openalex(self, query: str, max_results: int = 30) -> list[AcademicArticle]:
        """OpenAlex API'si üzerinden veri çeker."""
        url = "https://api.openalex.org/works"
        params = {"search": query, "per-page": max_results}
        articles: list[AcademicArticle] = []
        
        try:
            response = self.session.get(url, params=params, timeout=20)
            response.raise_for_status()
            items = response.json().get("results", [])
            
            for item in items:
                pub_year = str(item.get("publication_year", "Bilinmiyor"))
                title = item.get("display_name", "Bilinmiyor")
                
                journal_name = "Bilinmiyor"
                primary_loc = item.get("primary_location")
                if primary_loc and primary_loc.get("source"):
                    journal_name = primary_loc["source"].get("display_name", "Bilinmiyor")
                
                doc_type = item.get("type", "Bilinmiyor")
                article_url = item.get("doi", "URL bulunamadı.")
                if not article_url and primary_loc:
                     article_url = primary_loc.get("landing_page_url", "URL bulunamadı.")

                abstract_idx = item.get("abstract_inverted_index")
                abstract = "Özet bulunamadı."
                if abstract_idx:
                    max_idx = max([idx for positions in abstract_idx.values() for idx in positions])
                    words = [""] * (max_idx + 1)
                    for word, positions in abstract_idx.items():
                        for pos in positions:
                            words[pos] = word
                    # Boş stringleri temizleyip cümleyi oluşturma
                    abstract = " ".join([w for w in words if w])

                api_language = item.get("language")
                language = api_language.upper() if api_language else "BILINMIYOR"
                
                if language == "BILINMIYOR" or not language:
                    language = self.detect_language(abstract if abstract != "Özet bulunamadı." else title)

                articles.append(AcademicArticle(
                    database_name="OpenAlex", document_type=doc_type, publication_year=pub_year,
                    publication_language=language, journal_name=journal_name, article_title=title,
                    abstract_text=abstract, article_url=article_url
                ))
            return articles
        except requests.exceptions.RequestException as e:
            print(f"❌ OpenAlex bağlantı hatası: {e}")
            return []

    def search_arxiv(self, query: str, max_results: int = 30) -> list[AcademicArticle]:
        """arXiv API'si üzerinden veri çeker."""
        url = "http://export.arxiv.org/api/query"
        params = {"search_query": f"all:{query}", "start": 0, "max_results": max_results}
        articles: list[AcademicArticle] = []
        
        try:
            response = self.session.get(url, params=params, timeout=20)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                title_elem = entry.find('atom:title', ns)
                title = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else "Bilinmiyor"
                
                summary_elem = entry.find('atom:summary', ns)
                abstract = summary_elem.text.strip().replace('\n', ' ') if summary_elem is not None else "Özet bulunamadı."
                
                published_elem = entry.find('atom:published', ns)
                pub_year = published_elem.text[:4] if published_elem is not None else "Bilinmiyor"
                
                journal_name = "arXiv Preprint"
                doc_type = "Preprint / Ön Baskı"
                
                id_elem = entry.find('atom:id', ns)
                article_url = id_elem.text if id_elem is not None else "URL bulunamadı."
                
                text_to_analyze = abstract if abstract != "Özet bulunamadı." else title
                language = self.detect_language(text_to_analyze)

                articles.append(AcademicArticle(
                    database_name="arXiv", document_type=doc_type, publication_year=pub_year,
                    publication_language=language, journal_name=journal_name, article_title=title,
                    abstract_text=abstract, article_url=article_url
                ))
            
            time.sleep(3) # arXiv nezaket kuralı, aşırı yüklenmemek için.
            return articles
            
        except requests.exceptions.RequestException as e:
            print(f"❌ arXiv ağına bağlanırken bir hata oluştu: {e}")
            return []
        except ET.ParseError as e:
            print(f"❌ arXiv sunucusundan gelen XML verisi ayrıştırılamadı: {e}")
            return []

    def search_europepmc(self, query: str, max_results: int = 30) -> list[AcademicArticle]:
        """Europe PMC REST API'si üzerinden veri çeker (Tıp ve Yaşam Bilimleri)."""
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        params = {"query": query, "format": "json", "resultType": "core", "pageSize": max_results}
        articles: list[AcademicArticle] = []
        
        try:
            response = self.session.get(url, params=params, timeout=20)
            response.raise_for_status()
            items = response.json().get("resultList", {}).get("result", [])
            
            for item in items:
                pub_year = str(item.get("pubYear", "Bilinmiyor"))
                title = item.get("title", "Bilinmiyor")
                journal_name = item.get("journalTitle", "Bilinmiyor")
                doc_type = "Journal Article"
                
                abstract = item.get("abstractText", "Özet bulunamadı.")
                abstract = re.sub(r'<[^>]+>', '', abstract) # HTML etiketlerini temizleme
                
                doi = item.get("doi")
                article_url = f"https://doi.org/{doi}" if doi else "URL bulunamadı."
                
                api_language = item.get("language")
                language = api_language.upper() if api_language else "BILINMIYOR"
                
                if language == "BILINMIYOR" or not language:
                    language = self.detect_language(abstract if abstract != "Özet bulunamadı." else title)

                articles.append(AcademicArticle(
                    database_name="Europe PMC", document_type=doc_type, publication_year=pub_year,
                    publication_language=language, journal_name=journal_name, article_title=title,
                    abstract_text=abstract, article_url=article_url
                ))
            return articles
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Europe PMC ağına bağlanırken bir hata oluştu: {e}")
            return []

    def export_to_excel(self, data: list[AcademicArticle], filename: str) -> None:
        """Toplanan verileri standart formatta Excel'e dönüştürür."""
        if not data:
            print("Dışa aktarılacak veri bulunamadı.")
            return

        df = pd.DataFrame([asdict(item) for item in data])
        df.rename(columns={
            "database_name": "Veri Tabanı Adı", "document_type": "Doküman Türü",
            "publication_year": "Yayın Yılı", "publication_language": "Yayın Dili",
            "journal_name": "Dergi / Yayıncı Adı", "article_title": "Makale Başlığı",
            "abstract_text": "Özet Bilgisi", "article_url": "Makale URL"
        }, inplace=True)
        
        try:
            df.to_excel(filename, index=False, engine='openpyxl')
            print(f"\n✅ İşlem başarılı! Veriler '{filename}' dosyasına kaydedildi. Toplam kayıt: {len(df)}\n")
        except Exception as e:
            print(f"\n❌ Excel dosyası oluşturulurken hata meydana geldi: {e}\n")


# Kodu Çalıştırma Bloğu (Terminal Arayüzü)
if __name__ == "__main__":
    print("\n" + "="*55)
    print(" 🚀 SciTara: Gelişmiş Akademik Literatür Tarama Aracı")
    print("="*55 + "\n")
    
    # 1. Bilgilerin alınması
    kullanici_eposta = input("Lütfen e-posta adresinizi girin (API limitleri için): ").strip()
    if not kullanici_eposta:
        kullanici_eposta = "bilinmeyen@scitara.com"
        
    arama_terimi = input("Aramak istediğiniz terimi girin (Örn: machine learning): ").strip()
    if not arama_terimi:
        print("❌ Arama terimi boş bırakılamaz. Çıkış yapılıyor...")
        exit()
        
    try:
        istenen_sonuc = input("Kaç makale çekmek istersiniz? (Varsayılan 30, enter ile geçebilirsiniz): ").strip()
        istenen_sonuc_sayisi = int(istenen_sonuc) if istenen_sonuc else 30
    except ValueError:
        print("⚠️ Geçersiz sayı girdiniz. Varsayılan olarak 30 makale çekilecek.")
        istenen_sonuc_sayisi = 30

    # 2. Tarama platformunun seçilmesi
    print("\n" + "-"*40)
    print(" 📚 Hangi veri tabanında tarama yapılsın?")
    print("-" * 40)
    print("1 - Crossref (Genel Akademik)")
    print("2 - OpenAlex (Geniş Kapsamlı)")
    print("3 - arXiv (Ön Baskı: Fizik, Mat, Bilgisayar Bil.)")
    print("4 - Europe PMC (Tıp, Biyoloji ve Yaşam Bilimleri)")
    print("5 - Hepsinde Tara (Belirtilen sayı kadar her birinden çeker)")
    
    secim = input("\nSeçiminiz (1/2/3/4/5): ").strip()
    
    scraper = SciTaraScraper(user_email=kullanici_eposta)
    sonuclar = []

    print(f"\n⏳ '{arama_terimi}' terimi için sorgu başlatılıyor. Lütfen bekleyin...\n")

    # 3. Seçime göre işlemlerin yürütülmesi
    if secim == "1":
        print("🔎 Crossref taranıyor...")
        sonuclar.extend(scraper.search_crossref(arama_terimi, istenen_sonuc_sayisi))
    elif secim == "2":
        print("🔎 OpenAlex taranıyor...")
        sonuclar.extend(scraper.search_openalex(arama_terimi, istenen_sonuc_sayisi))
    elif secim == "3":
        print("🔎 arXiv taranıyor...")
        sonuclar.extend(scraper.search_arxiv(arama_terimi, istenen_sonuc_sayisi))
    elif secim == "4":
        print("🔎 Europe PMC taranıyor...")
        sonuclar.extend(scraper.search_europepmc(arama_terimi, istenen_sonuc_sayisi))
    elif secim == "5":
        print("🔎 Crossref taranıyor...")
        sonuclar.extend(scraper.search_crossref(arama_terimi, istenen_sonuc_sayisi))
        print("🔎 OpenAlex taranıyor...")
        sonuclar.extend(scraper.search_openalex(arama_terimi, istenen_sonuc_sayisi))
        print("🔎 arXiv taranıyor...")
        sonuclar.extend(scraper.search_arxiv(arama_terimi, istenen_sonuc_sayisi))
        print("🔎 Europe PMC taranıyor...")
        sonuclar.extend(scraper.search_europepmc(arama_terimi, istenen_sonuc_sayisi))
    else:
        print("⚠️ Hatalı seçim yaptınız. Varsayılan olarak 'OpenAlex' taranıyor...")
        sonuclar.extend(scraper.search_openalex(arama_terimi, istenen_sonuc_sayisi))

    # 4. Verilerin dışa aktarımı
    # Dosya adındaki geçersiz karakterleri temizleme
    guvenli_dosya_adi = "".join([c if c.isalnum() else "_" for c in arama_terimi]).strip("_").lower()
    dosya_adi = f"scitara_{guvenli_dosya_adi}_sonuclar.xlsx"
    
    scraper.export_to_excel(data=sonuclar, filename=dosya_adi)

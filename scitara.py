import requests
import pandas as pd
from dataclasses import dataclass, asdict
from langdetect import detect, LangDetectException

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

class AcademicDatabaseScraper:
    # E-posta parametresi zorunlu hale getirildi
    def __init__(self, user_email: str, use_proxy: bool = False, proxy_url: str = ""):
        self.session = requests.Session()
        
        if use_proxy and proxy_url:
            self.session.proxies = {"http": proxy_url, "https": proxy_url}
            
        # Kullanıcının girdiği e-posta HTTP başlığına dinamik olarak ekleniyor
        self.session.headers.update({
            "User-Agent": f"SciTara/1.0 (mailto:{user_email}; Python 3.12)"
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
            print(f"Crossref bağlantı hatası: {e}")
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
                    abstract = " ".join(words)

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
            print(f"OpenAlex bağlantı hatası: {e}")
            return []

    def export_to_excel(self, data: list[AcademicArticle], filename: str) -> None:
        """Toplanan verileri Excel'e dönüştürür."""
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
    print("\n" + "="*50)
    print(" 🚀 SciTara: Akademik Literatür Tarama Aracı")
    print("="*50 + "\n")
    
    # Kullanıcıdan bilgileri dinamik olarak alıyoruz
    kullanici_eposta = input("Lütfen e-posta adresinizi girin (Sunucu limitleri için gereklidir): ").strip()
    if not kullanici_eposta:
        kullanici_eposta = "bilinmeyen@scitara.com" # Boş bırakılırsa varsayılan
        
    arama_terimi = input("Aramak istediğiniz terimi girin (Örn: quantum computing): ").strip()
    if not arama_terimi:
        print("❌ Arama terimi boş bırakılamaz. Çıkış yapılıyor...")
        exit()
        
    try:
        istenen_sonuc = input("Kaç makale çekmek istersiniz? (Varsayılan 30, enter'a basıp geçebilirsiniz): ").strip()
        istenen_sonuc_sayisi = int(istenen_sonuc) if istenen_sonuc else 30
    except ValueError:
        print("⚠️ Geçersiz sayı girdiniz. Varsayılan olarak 30 makale çekilecek.")
        istenen_sonuc_sayisi = 30

    # Sınıfı kullanıcının girdiği e-posta ile başlat
    scraper = AcademicDatabaseScraper(user_email=kullanici_eposta)
    
    print(f"\n⏳ '{arama_terimi}' terimi için veri tabanında sorgu başlatılıyor. Lütfen bekleyin...")
    
    # Varsayılan olarak daha kapsamlı olan OpenAlex üzerinden arar. 
    # Dileyenler alttaki kodu scraper.search_crossref olarak değiştirebilir.
    sonuclar = scraper.search_openalex(query=arama_terimi, max_results=istenen_sonuc_sayisi)
    
    dosya_adi = arama_terimi.replace(" ", "_").lower() + "_sonuclar.xlsx"
    scraper.export_to_excel(data=sonuclar, filename=dosya_adi)
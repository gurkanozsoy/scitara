import requests
import pandas as pd
from dataclasses import dataclass, asdict
from langdetect import detect, LangDetectException
import xml.etree.ElementTree as ET
import time

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

class ArxivDatabaseScraper:
    def __init__(self, use_proxy: bool = False, proxy_url: str = ""):
        self.session = requests.Session()
        if use_proxy and proxy_url:
            self.session.proxies = {"http": proxy_url, "https": proxy_url}
            
        self.session.headers.update({
            "User-Agent": "SciTara_Arxiv/1.0 (Python 3.12)"
        })

    def detect_language(self, text: str) -> str:
        if not text or text == "Bilinmiyor" or text == "Özet bulunamadı.":
            return "Bilinmiyor"
        try:
            return detect(text).upper()
        except LangDetectException:
            return "Bilinmiyor"

    def search_arxiv(self, query: str, max_results: int = 30) -> list[AcademicArticle]:
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

                article = AcademicArticle(
                    database_name="arXiv", document_type=doc_type, publication_year=pub_year,
                    publication_language=language, journal_name=journal_name, article_title=title,
                    abstract_text=abstract, article_url=article_url
                )
                articles.append(article)
            
            time.sleep(3) # arXiv nezaket kuralı
            return articles
            
        except requests.exceptions.RequestException as e:
            print(f"arXiv ağına bağlanırken bir hata oluştu: {e}")
            return []
        except ET.ParseError as e:
            print(f"arXiv sunucusundan gelen XML verisi ayrıştırılamadı: {e}")
            return []

    def export_to_excel(self, data: list[AcademicArticle], filename: str) -> None:
        if not data:
            print("Dışa aktarılacak veri bulunamadı.")
            return

        df = pd.DataFrame([asdict(item) for item in data])
        df.rename(columns={
            "database_name": "Veri Tabanı Adı", "document_type": "Doküman Türü",
            "publication_year": "Yayın Yılı", "publication_language": "Yayın Dili",
            "journal_name": "Dergi Adı", "article_title": "Makale Başlığı",
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
    print(" 🚀 SciTara: arXiv (Açık Erişim) Tarama Aracı")
    print("="*50 + "\n")
    
    arama_terimi = input("Aramak istediğiniz terimi girin (Örn: string theory): ").strip()
    if not arama_terimi:
        print("❌ Arama terimi boş bırakılamaz. Çıkış yapılıyor...")
        exit()
        
    try:
        istenen_sonuc = input("Kaç makale çekmek istersiniz? (Varsayılan 30, enter'a basıp geçebilirsiniz): ").strip()
        istenen_sonuc_sayisi = int(istenen_sonuc) if istenen_sonuc else 30
    except ValueError:
        print("⚠️ Geçersiz sayı girdiniz. Varsayılan olarak 30 makale çekilecek.")
        istenen_sonuc_sayisi = 30

    scraper = ArxivDatabaseScraper()
    
    print(f"\n⏳ '{arama_terimi}' terimi için arXiv platformunda sorgu başlatılıyor...")
    
    sonuclar = scraper.search_arxiv(query=arama_terimi, max_results=istenen_sonuc_sayisi)
    
    # Oluşturulacak Excel dosyasının adını aranan terime göre dinamik yapıyoruz
    dosya_adi = "arxiv_" + arama_terimi.replace(" ", "_").lower() + "_sonuclar.xlsx"
    scraper.export_to_excel(data=sonuclar, filename=dosya_adi)
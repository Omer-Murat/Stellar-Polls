# 🌌 Stellar Polls - Dinamik Anket ve Oylama Sistemi

> Gelişmiş web standartlarına uygun olarak tasarlanmış, kozmik temalı, kullanıcı etkileşimli ve ölçeklenebilir bir Django anket uygulaması. 

Bu proje, temel oylama ve anket yönetimi ihtiyaçlarını karşılamak üzere **Ömer Murat / GitHub Omer-Murat** tarafından sıfırdan mimarilendirilmiş ve geliştirilmiştir. Güçlü bir altyapıya sahip olan bu sistem, hem bağımsız bir uygulama olarak çalışabilmekte hem de açık kaynak topluluğunun katkılarıyla büyümeye uygun, esnek bir temele dayanmaktadır.

## 🚀 Öne Çıkan Özellikler

* **Rol Bazlı Erişim:** Admin paneli üzerinden tam yetkili anket ve seçenek yönetimi.
* **Gerçek Zamanlı Sonuç Hesaplama:** Kullanıcı oylarının anında veritabanına işlenerek sonuç yüzdelerinin hesaplanması.
* **Güvenlik Mimarisi:** Django'nun yerleşik CSRF koruması, SQL Injection önlemleri ve oy manipülasyonuna karşı temel güvenlik bariyerleri.
* **Temiz Kod Yapısı (Clean Code):** MTV (Model-Template-View) mimarisine tam uyum ve modüler yapı.
* **Modern Teknolojik Arayüz:** Modern "Cosmic" UI, cam efekti (glassmorphism) ve TailwindCSS V3 mimarisi üzerine kurulu akıcı animasyonlar.

## 💻 Kullanılan Teknolojiler

* **Backend:** Python 3.x, Django 5.x
* **Frontend:** HTML5, CSS3, Tailwind CSS v3, DaisyUI
* **Veritabanı:** SQLite (Geliştirme ortamı)
* **Versiyon Kontrolü:** Git & GitHub

## 🗺️ Yol Haritası ve Geliştirme Süreci (Roadmap)

Bu proje, sürekli gelişime açık bir vizyonla tasarlanmıştır. Gelecek sürümlerde entegre edilmesi planlanan özellikler şunlardır:

- [x] **Kullanıcı Kimlik Doğrulama:** Kayıtlı kullanıcıların anket oluşturabilmesi ve oylarının profilleriyle eşleşmesi.
- [x] **Zaman Sınırlı Anketler:** Başlangıç ve bitiş tarihi belirlenebilen süreli anket özellikleri.
- [ ] **RESTful API Entegrasyonu:** Django REST Framework (DRF) ile uygulamanın dış servislere ve mobil uygulamalara açılması.
- [ ] **IP veya Çerez Bazlı Oy Sınırlaması:** Aynı kullanıcının mükerrer oy kullanmasını engelleyen gelişmiş algoritmalar.
- [ ] **Dockerizasyon:** Projenin Docker konteynerleri ile her ortamda tek tıkla ayağa kaldırılabilir hale getirilmesi.
- [ ] **Gelişmiş Veri Görselleştirme:** Chart.js veya D3.js ile anket sonuçlarının grafiksel sunumu.

## ⚙️ Kurulum Rehberi

Projeyi yerel ortamınızda test etmek veya geliştirmeye katkı sağlamak için aşağıdaki adımları izleyebilirsiniz:

```bash
# 1. Depoyu yerel makinenize klonlayın
git clone https://github.com/Omer-Murat/Stellar-Polls.git

# 2. Proje dizinine geçiş yapın
cd proje-adiniz

# 3. Sanal ortam (Virtual Environment) oluşturun ve aktif edin
python -m venv venv
source venv/bin/activate  # Windows için: venv\Scripts\activate

# 4. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 5. Veritabanı tablolarını oluşturun
python manage.py migrate

# 6. Yönetim paneli için süper kullanıcı oluşturun
python manage.py createsuperuser

# 7. Geliştirme sunucusunu başlatın
python manage.py runserver

# 🛡️ Pi-hole: İleri Düzey Tersine Mühendislik ve Sistem Analizi Raporu
**Öğrenci:** Ahmet Arda Sezer 
**Bölüm:** Bilişim Güvenliği Teknolojisi
**Seçilen Senaryo:** Senaryo 7 - DNS Müfettişi / Paket Analizi & Tersine Mühendislik

## 🔍 Proje Kapsamı ve Analiz Metodolojisi
Bu çalışma, dünya çapında yaygın olarak kullanılan Pi-hole DNS sinkhole yazılımının kurulum aşamalarını, ağ paketi işleme (sniffing) motorunu ve sistem bütünlüğünü tersine mühendislik disiplinleriyle analiz etmektedir. Projede **Statik Analiz (Static Reconnaissance)**, **Ağ Trafiği Analizi (Packet Sniffing)** ve **Adli Bilişim (Forensics)** metodolojileri bir arada kullanılmış; bulgular YARA kuralları ve JSON formatında yapılandırılmış çıktılarla desteklenmiştir.

---

## 🛠️ Bölüm 1: Statik Analiz ve String Çıkarımı
Hedef yazılımın kurulumunu üstlenen `basic-install.sh` betiği (Artifact) üzerinde statik kod analizi gerçekleştirilmiştir.

* **Bütünlük Kontrolü (Integrity Check Heuristics):** Kurulum dosyasının sadece bir indirici (downloader) olmadığı, dışarıdan çekilen bağımlılıkları `sha1sum` algoritması ile doğrulayarak MITM saldırılarına karşı bütünlük kontrolü yaptığı tespit edilmiştir.
* **Yapılandırılmış Çıktı Üretimi (JSON):** Statik analiz sonucunda elde edilen kritik dizinler ve fonksiyonlar yapılandırılmış **JSON** formatında raporlanmıştır. *(Bkz: `extracted_iocs.json`)*
* **YARA İmza Üretimi:** Pi-hole'un kurulum davranışlarını profileyen özgün bir **YARA kuralı** geliştirilmiştir. *(Bkz: `pihole_installer.yar`)*


![vizeee](https://github.com/user-attachments/assets/65834e40-aa10-44aa-8b1c-a81ae7eafc76)

## 🔬 Bölüm 2: Sandbox İzolasyonu ve Adli Bilişim (Forensics)
Kurulum işlemleri host makine yerine izole edilmiş bir **Kali Linux Sanal Makinesi (Sandbox)** üzerinde gerçekleştirilmiştir.

Sistemin "İz Silme" (Artifact Removal) yeteneği test edilmiştir. `sudo pihole uninstall` komutu sonrasında:
1. `ls -la /etc/pihole` ile dosya sisteminde konfigürasyon kalıntısı kalmadığı,
2. `cat /etc/passwd | grep pihole` ile arka plan servis kullanıcısının tamamen silindiği,
3. `ss -tulpn | grep 53` komutuyla hiçbir "Zombi Port" kalmadığı kanıtlanmıştır.


![sudo](https://github.com/user-attachments/assets/bc9caad3-7f90-4d06-9d03-da4b42bc08b3)

## ⚙️ Bölüm 3: Otomasyon Tersine Mühendisliği ve İzolasyon Mimarisi
* **CI/CD Pipeline Analizi:** `.github/workflows/test.yml` dosyası analiz edilmiştir. Sistemin "Webhook" mekanizmasıyla entegre çalıştığı ve her "Pull Request" eyleminin insan müdahalesi olmadan otomatik entegrasyon testlerini tetiklediği doğrulanmıştır.
* **Docker Katmanı İncelemesi:** Uygulamanın `debian:bookworm-slim` gibi minimum saldırı yüzeyine (Minimal Attack Surface) sahip bir katman kullandığı görülmüştür. Bu mimarinin, VM'lerin aksine host Kernel'ini paylaşması tersine mühendislik süreçlerinde bellek analizini farklılaştıran bir unsur olarak belgelenmiştir.

## 🎯 Bölüm 4: Tehdit Modellemesi: pihole-FTL Motoru ve DoH Bypass Saldırısı
Projenin odak noktası olan **pihole-FTL** DNS motorunun davranışları incelenmiştir.

* **Sniffing Mekanizması:** FTL motoru, standart UDP/TCP 53 portu üzerinden geçen şifresiz DNS paketlerini yakalar (Sniffing) ve bunları "Gravity" veri yapısıyla karşılaştırır.
* **Zafiyet Analizi (DoH Bypass):** Ağdaki bir kullanıcı veya zararlı yazılım, sorgularını Port 53 yerine **Port 443 (HTTPS) üzerinden şifreli tünellerle (DoH)** gönderirse, FTL motorunun paket analiz yeteneği tamamen devre dışı kalmaktadır.
* **Kavram Kanıtı (Proof of Concept):** Bu sniffing körlüğü, özel bir Python scripti ile simüle edilmiş ve kanıtlanmıştır. *(Bkz: `dns_sniffer_poc.py`)*

### 📊 Veri Akış Şeması: pihole-FTL ve DoH Bypass Modeli
```mermaid
graph TD
    A["İstemci / Zararlı Yazılım"] -->|"1. Şifresiz DNS İsteği"| B("Port 53 - UDP/TCP")
    A -->|"2. Şifreli DoH İsteği"| C("Port 443 - HTTPS")
    
    B --> D{"pihole-FTL (Sniffer)"}
    D -->|"Paket Okunabilir"| E["Gravity Listesi Heuristikleri"]
    E -->|"Eşleşme Var"| F(("Sorguyu Engelle / Sinkhole"))
    
    C -.->|"Paket Okunamaz"| G["Şifreli Tünel / Dış DNS"]
    G -.-> H(("Pi-hole FTL BYPASS Edildi!"))
    
    style D fill:#f9f,stroke:#333,stroke-width:2px
    style H fill:#ff4c4c,stroke:#333,stroke-width:2px,color:#fff

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



### Adım 5: Kaynak Kod ve Akış Analizi (Threat Modeling)

**1. Entrypoint (Başlangıç Noktası) ve Auth Mekanizması Tespiti:**
Yapay zeka tabanlı "Reasoning" (Akıl Yürütme) teknikleri kullanılarak uygulamanın kaynak kod dizini taranmıştır. Web arayüzünün giriş noktası (Entrypoint) olarak `login.lp` (Lua Pages) dosyası tespit edilmiştir. 

* **Auth Mekanizması Keşfi:** Kod analizi sırasında sistemin JWT veya OAuth gibi modern token mimarileri yerine, `<button type="submit" ...>Log in (uses cookie)</button>` satırından da teyit edildiği üzere geleneksel **Stateful Session Cookie (Çerez Tabanlı Oturum)** kullandığı tespit edilmiştir.

**2. THREAT MODELING SİMÜLASYONU 🕵️‍♂️**

* **Kritik Soru 1: Bir hacker bu reponun kodunu incelerken ne tür bir veriyi çalabileceğini nasıl bilir?**
  * *Reasoning (Akıl Yürütme) Analizi:* Bir hacker açık kaynak kodlu bir repoyu incelerken "Information Gathering" (Bilgi Toplama) yapar. `login.lp` kodunu inceleyen saldırgan, sistemin çerezlerle çalıştığını gördüğü an hedefini belirler: **"Admin Çerezi (Session Hijacking)"**. Hacker bilir ki bu çerezi ele geçirirse veya bu çerez üzerinden işlem yaptırırsa, ağdaki tüm cihazların DNS geçmişini (hangi sitelere girildiğini) çalabilir ve sahte banka sitelerine yönlendirme (DNS Spoofing) yapabilir.

* **Kritik Soru 2: Bulunan auth mekanizmasına dışarıdan nasıl saldırılabilir?**
  * *Saldırı Vektörü Keşfi:* Kodun içindeki `<form id="loginform">` bloğu derinlemesine incelendiğinde, modern web güvenliği standartlarında olması gereken `Anti-CSRF Token` (istek doğrulama bileti) yapısının bulunmadığı saptanmıştır.
  * *Sömürü (Exploit) Senaryosu:* Sistem dışarıdan Brute-Force (Kaba Kuvvet) saldırılarına kapalı olsa da, çerez yapısındaki CSRF açığı dışarıdan saldırıya imkan tanır. Saldırgan, halihazırda Pi-hole paneline giriş yapmış (çerezi aktif) kurbana zararsız görünen bir link gönderir (Bkz: Repodaki `csrf_exploit_poc.html`). Kurban linke tıkladığında, arka planda çalışan gizli form kurbanın yetkileriyle Pi-hole API'sine istek atar ve hacker'ın istediği zararlı domaini beyaz listeye ekler.

---

## 🧠 Teorik Altyapı ve Mimari İnceleme

### Sistem İzolasyonu ve Kalıntı (Artifact) Analizi
Siber güvenlik standartlarında sistem temizliğinin ispatı adli bilişim (forensics) adımlarıyla gerçekleştirilir. Sanal makine (VM) üzerinde yapılan analizlerde, `sudo pihole uninstall` işlemi sonrasında dosya sistemi (`/etc/pihole`), yetkili kullanıcılar (`/etc/passwd` üzerinden) ve ağ portları (`ss -tulpn` üzerinden) detaylıca taranmıştır. İnceleme sonucunda hiçbir konfigürasyon, arka plan servisi veya açık DNS portu kalmadığı somut olarak doğrulanmıştır.

### DevSecOps: Webhook ve Otomasyon Tetikleyicileri
CI/CD pipeline süreçlerinde "Webhook", sistemlerin birbirleriyle gerçek zamanlı iletişim kurmasını sağlayan HTTP tabanlı bir geri çağırma (callback) mekanizmasıdır. Bu projede, GitHub deposuna yapılan her yeni kod talebi (Pull Request) webhook'ları anında tetikleyerek insan müdahalesiz güvenlik ve linter testlerini başlatır. Bu otomasyon, Güvenli Yazılım Geliştirme Yaşam Döngüsü (Secure SDLC) standartlarının korunmasında kritik bir rol oynar.

### Konteyner Mimarisi, VM ve Kubernetes (K8s) Karşılaştırması
Projenin ağ ortamına dağıtımı, `debian:bookworm-slim` gibi minimal bir imaj üzerine inşa edilen Docker mimarisiyle sağlanmaktadır. 
* Geleneksel Sanal Makineler (VM), hipervizör (Hypervisor) aracılığıyla donanımı sanallaştırıp kendi ağır işletim sistemi çekirdeklerini çalıştırırken; Docker, host sistemin çekirdeğini (kernel) paylaşarak çok daha hafif ve izole bir yapı sunar. 
* Binlerce konteyneri yönetmek için tasarlanan Kubernetes (K8s) orkestrasyon sistemlerinden farklı olarak, Pi-hole gibi tekil çözümler Docker ile izole edilir. Güvenliği maksimize etmek için konteynerin host sisteme erişimi `cap_drop` (capabilities drop) parametreleriyle kısıtlanmalıdır.

### Saldırgan Perspektifi ve Tehdit İstihbaratı
Kaynak kod analizinde bir saldırganın (Threat Actor) birincil hedefleri API uç noktaları, kimlik doğrulama (Authentication) mekanizmaları ve veritabanı şemalarıdır. Pi-hole sistemini ele geçiren bir saldırgan, ağdaki tüm DNS sorgu geçmişini izleyerek ciddi bir mahremiyet ihlali yaratabilir. Analizimizde tespit edilen Cookie tabanlı yapıdaki "Anti-CSRF Token" eksikliği, saldırganların sosyal mühendislik yoluyla yetkisiz sistem değişiklikleri yapmasına doğrudan zemin hazırlayan en kritik saldırı vektörü olarak modellenmiştir.

---

### 📊 Veri Akış Şeması (CSRF Saldırı Modeli)
Aşağıdaki diyagram, Anti-CSRF token eksikliği durumunda dışarıdan bir saldırganın web paneline nasıl müdahale edebileceğini göstermektedir:

```mermaid
graph TD
    A["Saldırgan (Hacker)"] -->|"1. Zararlı Linki Gönderir"| B("Kurban (Admin)")
    B -->|"2. Oturumu Açıkken Linke Tıklar"| C{"Zararlı Web Sayfası (POC)"}
    C -->|"3. Gizli Form Tetiklenir (CSRF)"| D["Pi-hole Web API"]
    D -->|"4. İşlem Onaylanır (Çerez Geçerli)"| E(("Zararlı Domain Eklendi!"))
    
    style C fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#ff4c4c,stroke:#333,stroke-width:2px,color:#fff






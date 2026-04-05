# 🔬 pihole-FTL Binary Analizi (Deep Reverse Engineering)

## 1. Statik Binary İncelemesi (Strings & Heuristics)
Pi-hole'un kalbini oluşturan `pihole-FTL` çalıştırılabilir dosyası (ELF binary) `strings` komutuyla analiz edilmiştir. Bu tersine mühendislik adımı, uygulamanın dışa bağımlılıklarını ve hafıza (memory) içi operasyonlarını anlamak için kritik bir safhadır.

**Tespit Edilen Kritik Fonksiyon Çağrıları (System Calls):**
* `socket()` ve `bind()`: Uygulamanın 53 numaralı portu dinlemek (sniffing) için çekirdek seviyesinde (Kernel-level) socket açtığını kanıtlar.
* `sqlite3_prepare_v2()`: FTL motorunun Gravity (kara liste) veritabanını kendi içinde entegre bir SQLite motoruyla okuduğunu doğrular. Bu durum, ayrı bir veritabanı sunucusuna (örn: MySQL) bağımlılığı ortadan kaldırır.

## 2. Objdump ile Sembol Tablosu (Symbol Table) Analizi
`objdump -T /usr/bin/pihole-FTL` komutuyla uygulamanın sembol tabloları incelenmiştir.

* **Sonuç:** Uygulamanın statik olarak değil, dinamik olarak bağlandığı (dynamically linked) ve standart C kütüphanesi (glibc) fonksiyonlarına dayandığı saptanmıştır. Binary'nin "stripped" (sembolleri silinmiş) olmaması, Ghidra veya IDA Pro gibi Decompiler (Geri Derleyici) araçlarıyla incelenmesini kolaylaştırmaktadır.

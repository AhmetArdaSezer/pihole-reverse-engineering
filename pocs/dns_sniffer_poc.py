#!/usr/bin/env python3
# ==============================================================================
# Proje: Pi-hole Tersine Mühendislik ve Paket Analizi
# Yazar: Ahmet Arda Sezer
# Amaç: Şifresiz DNS (Port 53) ve Şifreli DoH (Port 443) Trafiği Simülasyonu
# ==============================================================================

from scapy.all import sniff, DNSQR
# TODO: Gelecek sürümde IPv6 (DoH) trafiğini analiz edebilmek için TShark entegrasyonu eklenecek.
def process_packet(packet):
    """
    Yakalanan ağ paketlerini analiz eden ana fonksiyon.
    Eğer paket DNSQR (DNS Query Record) katmanı içeriyorsa, şifresizdir.
    İçermiyorsa HTTPS (DoH) şifrelemesine takılmış demektir.
    """
    # 1. Aşama: Paketin şifresiz standart DNS (Port 53) olup olmadığını kontrol et
    if packet.haslayer(DNSQR):
        # QNAME (Queried Name) değerini decode ederek insanın okuyabileceği hale getir
        queried_domain = packet[DNSQR].qname.decode('utf-8')
        print(f"[!] Şifresiz DNS İsteği Yakalandı (Port 53): {queried_domain}")
        print("    -> Durum: Pi-hole FTL motoru bu paketi okuyabilir ve engelleyebilir.")
    
    # 2. Aşama: Paket şifreli tünelden (DoH - Port 443) geçiyorsa
    else:
        print("[x] Şifreli Paket (DoH/HTTPS) Yakalandı.")
        print("    -> Durum: İçerik okunamıyor. Pi-hole FTL Bypass edildi!")

if __name__ == "__main__":
    print("Pi-hole FTL Sniffer Simülasyonu Başlatıldı...")
    print("Ağ üzerindeki Port 53 (DNS) ve Port 443 (DoH) trafiği dinleniyor...\n")
    
    # Scapy sniffer fonksiyonu: Sadece hedef portları filtrele ve 10 paket yakala
    # store=0 parametresi, RAM şişmesini önlemek için paketleri hafızada tutmaz
    sniff(filter="port 53 or port 443", prn=process_packet, store=0, count=10)

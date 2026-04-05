#!/usr/bin/env python3
from scapy.all import sniff, DNSQR

def process_packet(packet):
    if packet.haslayer(DNSQR):
        queried_domain = packet[DNSQR].qname.decode('utf-8')
        print(f"[!] Şifresiz DNS İsteği Yakalandı (Port 53): {queried_domain}")
    else:
        print("[x] Şifreli Paket (DoH/HTTPS) Yakalandı.")
        print("    -> İçerik okunamıyor. Pi-hole FTL Bypass edildi!")

print("Pi-hole FTL Sniffer Simülasyonu Başlatıldı...")
sniff(filter="port 53 or port 443", prn=process_packet, store=0, count=10)

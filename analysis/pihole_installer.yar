rule Pihole_Installer_Detection {
    meta:
        author = "Ahmet Arda Sezer"
        description = "Pi-hole kurulum scripti statik analiz imza tespiti"
    strings:
        $url = "https://install.pi-hole.net"
        $bash_exec = "curl -sSL"
        $root_check = "if [[ $EUID -eq 0 ]]"
        $critical_dir = "/etc/pihole"
    condition:
        all of them
}

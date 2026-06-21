# Sicherheit

PicShelf ist für lokale Netze und private Docker-Umgebungen gedacht.

## Melden

Sicherheitsprobleme bitte nicht öffentlich als Beispiel ausnutzen. Für ein eigenes GitHub-Repo kann hier später eine Kontaktadresse ergänzt werden.

## Grenzen

- Kein eingebautes Login
- Keine Rollen oder Rechteverwaltung
- Keine Prüfung hochgeladener Dateien, da PicShelf keinen Upload anbietet

Für Zugriff aus dem Internet sollte ein Reverse Proxy mit Authentifizierung, TLS und IP-Beschränkung genutzt werden.

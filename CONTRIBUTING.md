# Beitrag

PicShelf soll klein und wartbar bleiben. Änderungen sollten deshalb den Kern einfach halten und keine schweren Abhängigkeiten einführen.

## Lokale Prüfung

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
docker compose config
```

## Leitlinien

- Keine Datenbank, solange Dateien und Ordner reichen
- Keine Cloud-Pflicht
- Keine externen Frontend-Abhängigkeiten ohne klaren Nutzen
- Docker-Betrieb als Standardpfad testen
- README bei geänderter Bedienung aktualisieren

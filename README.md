# PicShelf

PicShelf ist ein lokaler Bildhoster für Heimnetzwerke und selbst gehostete Dienste.
Die Anwendung arbeitet dateibasiert, kommt ohne Datenbank aus und stellt Bilder per HTTP mit direkt kopierbaren URLs bereit.

Der Fokus liegt auf wenig Aufwand im Betrieb, sauberer Ordnerstruktur und einer einfachen Weboberfläche für Verwaltung und Zugriff.

## Highlights

- Lokale Bilder per HTTP ausliefern
- Kategorien direkt aus Ordnernamen ableiten
- Direkt kopierbare Bild-URLs
- Vorschau mit Adresse im Overlay
- Suche nach Dateiname und Kategorie
- Upload, Umbenennen, Verschieben und Löschen
- Mehrfachauswahl für Löschen, Download und Teilen
- Kategorien in der UI anlegen, umbenennen und löschen
- Favoriten markieren und filtern
- Grid- und Listenansicht
- Dark Mode automatisch nach Systemeinstellung
- Speicherplatzanzeige für das Bilderlaufwerk
- Keine externen Python-Abhängigkeiten
- Docker-tauglich und als nicht privilegierter Container nutzbar

## Warum PicShelf

PicShelf ist für den typischen Homelab-Einsatz gebaut:

- Bilder bleiben normale Dateien im Dateisystem
- andere Dienste können die URLs direkt verwenden
- es gibt kein Cloud-Konto und kein separates Backend-System
- der Betrieb bleibt transparent und leicht wartbar

## Schnellstart mit Docker Compose

```bash
docker compose up -d --build
```

Danach ist die Galerie unter folgender URL erreichbar:

```text
http://localhost:8099
```

Im Heimnetz kann statt `localhost` die IP des Hosts verwendet werden, zum Beispiel:

```text
http://<host-ip>:8099
```

## Screenshot

<img width="967" height="576" alt="image" src="https://github.com/user-attachments/assets/8f34ec20-5b44-4775-90d4-8199817d5d13" />


## Bilder ablegen

Kategorien entstehen durch Unterordner im Bilderverzeichnis:

```text
images/
├── Natur/
│   ├── wald.jpg
│   └── see.webp
├── Referenzen/
│   └── layout.png
└── logo.png
```

Bilder direkt im Ordner `images/` erscheinen in der Kategorie `Allgemein`.

Unterstützte Dateitypen:

`avif`, `bmp`, `gif`, `jpeg`, `jpg`, `png`, `svg`, `webp`

## Betrieb als Dienst

Für einen bestehenden Docker-Host kann diese Compose-Datei als Vorlage dienen:

```yaml
services:
  picshelf:
    image: ghcr.io/tingeltangelbob/picshelf:latest
    container_name: picshelf
    restart: unless-stopped
    ports:
      - "8099:8080"
    environment:
      TZ: Europe/Berlin
      PICSHELF_TITLE: PicShelf
      PICSHELF_IMAGES_DIR: /data/images
      PICSHELF_CACHE_SECONDS: "3600"
      PICSHELF_MAX_UPLOAD_MB: "50"
      PICSHELF_ACCESS_LOG: "0"
    volumes:
      - /pfad/zu/bildern:/data/images
    read_only: true
    tmpfs:
      - /tmp
    security_opt:
      - no-new-privileges:true
```

Wenn die kopierte Bildadresse immer eine feste Heimnetz-Adresse enthalten soll, kann zusätzlich gesetzt werden:

```yaml
environment:
  PICSHELF_BASE_URL: http://<host-ip>:8099
```

Ohne `PICSHELF_BASE_URL` erzeugt die Oberfläche die Adresse aus der aktuell geöffneten Browser-URL.

## Portainer

Wenn du PicShelf in Portainer per Copy-and-Paste deployen willst, nutze die Datei `docker-compose.portainer.yml`.
Sie zieht ein fertiges Image aus GHCR und braucht deshalb keinen Build-Kontext und keinen lokalen `Dockerfile`-Pfad.

```yaml
services:
  picshelf:
    image: ghcr.io/tingeltangelbob/picshelf:latest
    container_name: picshelf
    restart: unless-stopped
    ports:
      - "8099:8080"
    environment:
      TZ: Europe/Berlin
      PICSHELF_TITLE: PicShelf
      PICSHELF_IMAGES_DIR: /data/images
      PICSHELF_CACHE_SECONDS: "3600"
      PICSHELF_MAX_UPLOAD_MB: "50"
      PICSHELF_ACCESS_LOG: "0"
    volumes:
      - picshelf-images:/data/images
    read_only: true
    tmpfs:
      - /tmp
    security_opt:
      - no-new-privileges:true

volumes:
  picshelf-images:
```

## Varianten

- `docker compose up -d --build` für lokale Entwicklung mit den Bildern im Repo-Ordner `images/`
- `docker-compose.portainer.yml` für Portainer ohne Build-Schritt und ohne Anpassungen; dort liegt das Bildmaterial in einem benannten Volume statt in einem Host-Pfad, damit der Stack wirklich copy-paste-fähig bleibt
- GitHub Actions veröffentlicht bei jedem Push auf `main` ein aktuelles Container-Image nach GHCR
- Wer die Bilder lieber direkt im ausgecheckten Repo ablegen will, kann den lokalen `images/`-Ordner weiter nutzen

Hinweis: Nach dem ersten Push muss der GitHub-Action-Run einmal durchlaufen, bevor Portainer das Image `ghcr.io/tingeltangelbob/picshelf:latest` ziehen kann.

## Konfiguration

| Variable | Standard | Bedeutung |
| --- | --- | --- |
| `PORT` | `8080` | Interner HTTP-Port |
| `HOST` | `0.0.0.0` | Bind-Adresse im Container |
| `PICSHELF_IMAGES_DIR` | `./images` | Bilderverzeichnis |
| `PICSHELF_TITLE` | `PicShelf` | Titel in der Weboberfläche |
| `PICSHELF_BASE_URL` | leer | Optionale feste Basis-URL für Bildadressen |
| `PICSHELF_CACHE_SECONDS` | `3600` | Browser-Cache für Bilddateien |
| `PICSHELF_MAX_UPLOAD_MB` | `50` | Maximale Größe einer Upload-Anfrage in MB |
| `PICSHELF_ACCESS_LOG` | `0` | HTTP-Zugriffslog aktivieren mit `1` |
| `PICSHELF_BUILD_LABEL` | `local` | Anzeige für den aktuellen Build in der Oberfläche |

## Entwicklung

Lokaler Start ohne Docker:

```bash
cd picshelf
PYTHONPATH=src PICSHELF_IMAGES_DIR=./images python3 -m picshelf.server
```

Tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## API

```text
GET /api/images
GET /api/meta
POST /api/upload
POST /api/categories
POST /api/categories/delete
POST /api/categories/rename
POST /api/images/rename
POST /api/images/move
POST /api/images/delete
POST /api/images/delete-bulk
POST /api/images/download
POST /api/images/favorite
```

## Sicherheit

PicShelf ist für ein vertrauenswürdiges Heimnetz gedacht und enthält bewusst kein Login-System.
Für öffentlichen Zugriff sollte ein Reverse Proxy mit Authentifizierung, TLS und Zugriffsbeschränkung vorgeschaltet werden.

Der Container läuft ohne Root-Rechte und kann mit read-only Root-Dateisystem betrieben werden.
Der Bilderordner wird schreibbar gemountet, weil Upload, Umbenennen, Verschieben und Löschen direkt auf Dateien arbeiten.

## Lizenz

MIT

## Autor und Support

Wenn dir PicShelf hilft, freue ich mich über Stern, Feedback oder einen Pull Request.

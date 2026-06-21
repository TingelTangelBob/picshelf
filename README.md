# PicShelf

PicShelf ist ein kleiner lokaler Bildserver mit Galerie-UI. Bilder liegen einfach als Dateien in Ordnern. Jeder Ordner wird als Kategorie angezeigt, jedes Bild bekommt eine direkt kopierbare HTTP-Adresse.

Der Fokus liegt auf Heimnetz, Docker Compose, wenig Ressourcen und einfacher Wartung. Es gibt keine Datenbank, kein Cloud-Konto und kein komplexes Rechtesystem.

## Funktionen

- Lokale Bilder per HTTP ausliefern
- Galerie mit Kategorien aus Ordnernamen
- Kopierbare Adresse pro Bild
- Bildvorschau mit Adresse im Overlay
- Suche nach Dateiname und Kategorie
- Bilder hochladen, umbenennen, verschieben und löschen
- Mehrere Bilder auswählen und gemeinsam löschen, herunterladen oder teilen
- Kategorien über die UI anlegen
- Kategorien umbenennen und löschen
- Favoriten markieren und filtern
- Umschaltbare Grid- und Listenansicht
- Dark Mode automatisch nach Systemeinstellung
- Speicherplatzanzeige für das Laufwerk des Bilderordners
- Keine externen Python-Abhängigkeiten
- Docker-tauglich und als nicht privilegierter Container nutzbar
- Read-only Container mit schreibbarem Bilderordner-Volume

## Ordnerstruktur

```text
picshelf/
├── src/picshelf/server.py     # HTTP-Server, API und Dateiverwaltung
├── src/picshelf/static/       # Weboberfläche
├── tests/                     # Stdlib-Tests
├── images/                    # Lokaler Bilderordner für Docker Compose
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── pyproject.toml
└── README.md
```

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

Unterstützte Dateiendungen: `avif`, `bmp`, `gif`, `jpeg`, `jpg`, `png`, `svg`, `webp`.

## Bilder verwalten

Die Weboberfläche enthält einfache Verwaltungsfunktionen:

- Upload per Icon, Dialog und Drag-and-drop
- Globales Drag-and-drop mit Importvorschlag
- Kategorie anlegen
- Kategorie umbenennen und löschen
- Bild umbenennen
- Bild in eine andere Kategorie verschieben
- Bild löschen
- Mehrere Bilder als ZIP herunterladen
- Mehrere Bildadressen teilen oder kopieren
- Favorit setzen oder entfernen
- Zwischen Grid und Liste wechseln

Kategorien sind Ordner im Bilderverzeichnis. Das Verschieben eines Bildes entspricht also einem Verschieben der Datei in einen anderen Ordner.
Leere Kategorien werden in der Seitenleiste angezeigt, sobald der Ordner angelegt wurde.

Favoriten werden lokal im Bilderverzeichnis in `.picshelf-favorites.json` gespeichert. Die Datei ist versteckt und wird nicht als Bild angezeigt.

## Lokal mit Docker Compose starten

```bash
docker compose up -d --build
```

Danach ist die Galerie erreichbar unter:

```text
http://localhost:8099
```

Im Heimnetz kann später die IP des Hosts genutzt werden, zum Beispiel:

```text
http://192.168.178.191:8099
```

## Betrieb als Dienst

Für einen bestehenden Docker-Ordner kann die Compose-Datei übernommen und der Bilderordner angepasst werden:

```yaml
services:
  picshelf:
    image: ghcr.io/dein-name/picshelf:latest
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

Wenn die kopierte Adresse immer eine feste Heimnetz-Adresse enthalten soll, kann zusätzlich gesetzt werden:

```yaml
environment:
  PICSHELF_BASE_URL: http://192.168.178.191:8099
```

Ohne `PICSHELF_BASE_URL` erzeugt die UI die Adresse aus der aktuell geöffneten Browser-Adresse.

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

Antwort:

```json
{
  "categories": [
    {
      "name": "Natur",
      "items": [
        {
          "name": "wald",
          "fileName": "wald.jpg",
          "category": "Natur",
          "path": "Natur/wald.jpg",
          "url": "/media/Natur/wald.jpg",
          "size": 12345,
          "favorite": false
        }
      ]
    }
  ],
  "total": 1,
  "favorites": 0,
  "disk": {
    "total": 1000000000,
    "used": 400000000,
    "free": 600000000,
    "percentUsed": 40.0
  }
}
```

## Sicherheit

PicShelf ist für ein vertrauenswürdiges Heimnetz gedacht. Es enthält bewusst kein Login-System. Für öffentlichen Zugriff sollte ein Reverse Proxy mit Authentifizierung, TLS und Zugriffsbeschränkung davor genutzt werden.

Der Container läuft ohne Root-Rechte und kann mit read-only Root-Dateisystem betrieben werden. Der Bilderordner wird schreibbar gemountet, weil Upload, Umbenennen, Verschieben und Löschen direkt auf Dateien arbeiten.

## Lizenz

MIT

## Autor und Support

- GitHub: [TingelTangelBob](https://github.com/TingelTangelBob)
- Support: [GitHub Sponsors](https://github.com/sponsors/TingelTangelBob)

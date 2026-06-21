from __future__ import annotations

import html
import io
import json
import mimetypes
import os
import re
import shutil
import zipfile
from email import policy
from email.parser import BytesParser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote, unquote, urlparse

from . import __version__


IMAGE_EXTENSIONS = {
    ".avif",
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".svg",
    ".webp",
}

DEFAULT_CATEGORY = "Allgemein"
CATEGORY_PATTERN = re.compile(r"^[^/\\]+$")
FAVORITES_FILE = ".picshelf-favorites.json"


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def is_image_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def is_hidden_path(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)


def is_inside(base_dir: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(base_dir)
        return True
    except ValueError:
        return False


def clean_category_name(name: str | None) -> str:
    if not name:
        return DEFAULT_CATEGORY
    cleaned = " ".join(name.strip().split())
    if not cleaned:
        return DEFAULT_CATEGORY
    if cleaned.startswith(".") or cleaned in {".", ".."} or not CATEGORY_PATTERN.match(cleaned):
        raise ValueError("Ungueltiger Kategoriename.")
    return cleaned


def clean_file_name(name: str | None, fallback_extension: str | None = None) -> str:
    if not name:
        raise ValueError("Dateiname fehlt.")
    cleaned = PurePosixPath(name.replace("\\", "/")).name.strip()
    if cleaned.startswith(".") or cleaned in {"", ".", ".."}:
        raise ValueError("Ungueltiger Dateiname.")

    path = Path(cleaned)
    if not path.suffix and fallback_extension:
        cleaned = f"{cleaned}{fallback_extension}"
        path = Path(cleaned)

    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError("Dateityp wird nicht unterstuetzt.")
    return cleaned


def category_dir(images_dir: Path, category: str | None, create: bool = False) -> Path:
    cleaned = clean_category_name(category)
    directory = images_dir if cleaned == DEFAULT_CATEGORY else images_dir / cleaned
    resolved = directory.resolve()
    if not is_inside(images_dir, resolved) and resolved != images_dir:
        raise ValueError("Ungueltige Kategorie.")
    if create:
        resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def resolve_image_path(images_dir: Path, raw_path: str) -> Path:
    media_path = safe_media_path(raw_path)
    if media_path is None:
        raise FileNotFoundError("Bild wurde nicht gefunden.")

    file_path = (images_dir / Path(*media_path.parts)).resolve()
    if not is_inside(images_dir, file_path) or not is_image_file(file_path):
        raise FileNotFoundError("Bild wurde nicht gefunden.")
    return file_path


def relative_media_path(images_dir: Path, file_path: Path) -> str:
    return str(file_path.relative_to(images_dir)).replace(os.sep, "/")


def unique_file_path(directory: Path, file_name: str) -> Path:
    target = directory / file_name
    if not target.exists():
        return target

    stem = target.stem
    suffix = target.suffix
    for index in range(1, 1000):
        candidate = directory / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
    raise FileExistsError("Es gibt bereits zu viele Dateien mit diesem Namen.")


def remove_empty_parent_dirs(images_dir: Path, start: Path) -> None:
    current = start.resolve()
    while current != images_dir and is_inside(images_dir, current):
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def favorites_path(images_dir: Path) -> Path:
    return images_dir / FAVORITES_FILE


def load_favorites(images_dir: Path) -> set[str]:
    path = favorites_path(images_dir)
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    if not isinstance(data, list):
        return set()
    return {item for item in data if isinstance(item, str) and safe_media_path(item) is not None}


def save_favorites(images_dir: Path, favorites: set[str]) -> None:
    path = favorites_path(images_dir)
    path.write_text(json.dumps(sorted(favorites), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def replace_favorite_path(images_dir: Path, old_path: str, new_path: str) -> None:
    favorites = load_favorites(images_dir)
    if old_path not in favorites:
        return
    favorites.remove(old_path)
    favorites.add(new_path)
    save_favorites(images_dir, favorites)


def remove_favorite_path(images_dir: Path, old_path: str) -> None:
    favorites = load_favorites(images_dir)
    if old_path not in favorites:
        return
    favorites.remove(old_path)
    save_favorites(images_dir, favorites)


def remove_favorite_paths(images_dir: Path, old_paths: set[str]) -> None:
    favorites = load_favorites(images_dir)
    next_favorites = favorites - old_paths
    if next_favorites != favorites:
        save_favorites(images_dir, next_favorites)


def remove_favorites_by_prefix(images_dir: Path, prefix: str) -> None:
    favorites = load_favorites(images_dir)
    normalized = prefix.rstrip("/") + "/"
    next_favorites = {item for item in favorites if not item.startswith(normalized)}
    if next_favorites != favorites:
        save_favorites(images_dir, next_favorites)


def rename_favorites_by_prefix(images_dir: Path, old_prefix: str, new_prefix: str) -> None:
    favorites = load_favorites(images_dir)
    old_normalized = old_prefix.rstrip("/") + "/"
    new_normalized = new_prefix.rstrip("/") + "/"
    next_favorites = {
        f"{new_normalized}{item.removeprefix(old_normalized)}" if item.startswith(old_normalized) else item
        for item in favorites
    }
    if next_favorites != favorites:
        save_favorites(images_dir, next_favorites)


def image_paths_from_payload(images_dir: Path, data: dict[str, Any]) -> list[Path]:
    raw_paths = data.get("paths")
    if not isinstance(raw_paths, list) or not raw_paths:
        raise ValueError("Keine Bilder ausgewählt.")

    resolved: list[Path] = []
    seen: set[str] = set()
    for raw_path in raw_paths:
        if not isinstance(raw_path, str):
            raise ValueError("Ungueltige Bildauswahl.")
        file_path = resolve_image_path(images_dir, raw_path)
        relative_path = relative_media_path(images_dir, file_path)
        if relative_path not in seen:
            seen.add(relative_path)
            resolved.append(file_path)
    return resolved


def safe_media_path(url_path: str) -> PurePosixPath | None:
    decoded = unquote(url_path)
    candidate = PurePosixPath(decoded)
    if candidate.is_absolute():
        return None
    if not candidate.parts:
        return None
    if any(part in {"", ".", ".."} for part in candidate.parts):
        return None
    return candidate


def media_url_for(relative_path: Path, base_url: str = "") -> str:
    encoded = "/".join(quote(part) for part in relative_path.parts)
    relative_url = f"/media/{encoded}"
    if not base_url:
        return relative_url
    return f"{base_url.rstrip('/')}{relative_url}"


def build_library(images_dir: Path, base_url: str = "") -> dict[str, Any]:
    root = images_dir.resolve()
    categories: dict[str, list[dict[str, Any]]] = {}
    favorites = load_favorites(root)

    if not root.exists():
        return {"categories": [], "total": 0, "favorites": 0, "disk": None}

    for directory in sorted((path for path in root.iterdir() if path.is_dir()), key=lambda p: p.name.lower()):
        relative_path = directory.relative_to(root)
        if is_hidden_path(relative_path):
            continue
        resolved = directory.resolve()
        if is_inside(root, resolved):
            categories.setdefault(directory.name, [])

    for file_path in sorted(root.rglob("*"), key=lambda p: str(p).lower()):
        if is_hidden_path(file_path.relative_to(root)) or not is_image_file(file_path):
            continue

        resolved = file_path.resolve()
        if not is_inside(root, resolved):
            continue

        relative_path = file_path.relative_to(root)
        relative_key = str(relative_path).replace(os.sep, "/")
        category = relative_path.parts[0] if len(relative_path.parts) > 1 else DEFAULT_CATEGORY
        categories.setdefault(category, []).append(
            {
                "name": file_path.stem,
                "fileName": file_path.name,
                "category": category,
                "path": relative_key,
                "url": media_url_for(relative_path, base_url),
                "size": file_path.stat().st_size,
                "favorite": relative_key in favorites,
            }
        )

    category_list = [
        {"name": name, "items": items}
        for name, items in sorted(categories.items(), key=lambda entry: entry[0].lower())
    ]
    try:
        usage = shutil.disk_usage(root)
        disk = {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percentUsed": round((usage.used / usage.total) * 100, 1) if usage.total else 0,
        }
    except OSError:
        disk = None

    return {
        "categories": category_list,
        "total": sum(len(category["items"]) for category in category_list),
        "favorites": sum(1 for category in category_list for item in category["items"] if item["favorite"]),
        "disk": disk,
    }


def static_dir() -> Path:
    return Path(__file__).resolve().parent / "static"


def render_app_index(title: str) -> bytes:
    template = (static_dir() / "index.html").read_text(encoding="utf-8")
    return template.replace("__TITLE__", html.escape(title)).encode("utf-8")


class PicShelfHandler(BaseHTTPRequestHandler):
    server_version = f"PicShelf/{__version__}"

    @property
    def config(self) -> dict[str, Any]:
        return self.server.config  # type: ignore[attr-defined]

    def do_GET(self) -> None:
        self.route(include_body=True)

    def do_HEAD(self) -> None:
        self.route(include_body=False)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/upload":
                self.handle_upload()
                return
            if parsed.path == "/api/categories":
                self.handle_create_category()
                return
            if parsed.path == "/api/categories/delete":
                self.handle_delete_category()
                return
            if parsed.path == "/api/categories/rename":
                self.handle_rename_category()
                return
            if parsed.path == "/api/images/rename":
                self.handle_rename_image()
                return
            if parsed.path == "/api/images/move":
                self.handle_move_image()
                return
            if parsed.path == "/api/images/delete":
                self.handle_delete_image()
                return
            if parsed.path == "/api/images/delete-bulk":
                self.handle_delete_images()
                return
            if parsed.path == "/api/images/download":
                self.handle_download_images()
                return
            if parsed.path == "/api/images/favorite":
                self.handle_favorite_image()
                return
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Endpunkt wurde nicht gefunden."})
        except ValueError as error:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
        except FileNotFoundError as error:
            self.send_json(HTTPStatus.NOT_FOUND, {"error": str(error)})
        except FileExistsError as error:
            self.send_json(HTTPStatus.CONFLICT, {"error": str(error)})
        except OSError as error:
            self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": f"Dateioperation fehlgeschlagen: {error}"})

    def read_body(self) -> bytes:
        length = self.headers.get("Content-Length")
        if not length:
            return b""
        size = int(length)
        max_size = self.config["max_upload_bytes"]
        if size > max_size:
            raise ValueError(f"Anfrage ist zu gross. Maximum: {max_size // 1024 // 1024} MB.")
        return self.rfile.read(size)

    def read_json(self) -> dict[str, Any]:
        body = self.read_body()
        if not body:
            return {}
        try:
            data = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError("Ungueltiges JSON.") from error
        if not isinstance(data, dict):
            raise ValueError("JSON muss ein Objekt sein.")
        return data

    def send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_bytes(
            status,
            body,
            "application/json; charset=utf-8",
            include_body=True,
            cache_control="no-store",
        )

    def parse_multipart(self) -> tuple[dict[str, str], list[dict[str, Any]]]:
        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            raise ValueError("Upload muss multipart/form-data verwenden.")

        body = self.read_body()
        message = BytesParser(policy=policy.default).parsebytes(
            f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8") + body
        )
        fields: dict[str, str] = {}
        files: list[dict[str, Any]] = []

        for part in message.iter_parts():
            if part.get_content_disposition() != "form-data":
                continue
            name = part.get_param("name", header="content-disposition")
            filename = part.get_filename()
            payload = part.get_payload(decode=True) or b""
            if filename:
                files.append({"field": name, "filename": filename, "content": payload})
            elif name:
                fields[name] = payload.decode(part.get_content_charset() or "utf-8", errors="replace")

        return fields, files

    def handle_upload(self) -> None:
        fields, files = self.parse_multipart()
        if not files:
            raise ValueError("Keine Datei im Upload gefunden.")

        images_dir = self.config["images_dir"]
        directory = category_dir(images_dir, fields.get("category"), create=True)
        uploaded: list[dict[str, str]] = []

        for item in files:
            file_name = clean_file_name(item["filename"])
            content = item["content"]
            if not content:
                raise ValueError(f"{file_name} ist leer.")
            target = unique_file_path(directory, file_name)
            target.write_bytes(content)
            uploaded.append({"path": relative_media_path(images_dir, target), "fileName": target.name})

        self.send_json(HTTPStatus.CREATED, {"uploaded": uploaded})

    def handle_create_category(self) -> None:
        data = self.read_json()
        if not data.get("name"):
            raise ValueError("Kategoriename fehlt.")
        category = clean_category_name(data.get("name"))
        category_dir(self.config["images_dir"], category, create=True)
        self.send_json(HTTPStatus.CREATED, {"category": category})

    def handle_delete_category(self) -> None:
        data = self.read_json()
        if not data.get("name"):
            raise ValueError("Kategoriename fehlt.")
        category = clean_category_name(data.get("name"))
        if category == DEFAULT_CATEGORY:
            raise ValueError("Allgemein kann nicht gelöscht werden.")

        images_dir = self.config["images_dir"]
        directory = category_dir(images_dir, category, create=False)
        if not directory.exists() or not directory.is_dir():
            raise FileNotFoundError("Kategorie wurde nicht gefunden.")

        shutil.rmtree(directory)
        remove_favorites_by_prefix(images_dir, category)
        self.send_json(HTTPStatus.OK, {"deleted": category})

    def handle_rename_category(self) -> None:
        data = self.read_json()
        if not data.get("name") or not data.get("newName"):
            raise ValueError("Kategoriename fehlt.")

        old_category = clean_category_name(data.get("name"))
        new_category = clean_category_name(data.get("newName"))
        if old_category == DEFAULT_CATEGORY:
            raise ValueError("Allgemein kann nicht umbenannt werden.")
        if new_category == DEFAULT_CATEGORY:
            raise ValueError("Bitte einen anderen Namen als Allgemein wählen.")
        if old_category == new_category:
            self.send_json(HTTPStatus.OK, {"category": new_category})
            return

        images_dir = self.config["images_dir"]
        source = category_dir(images_dir, old_category, create=False)
        target = category_dir(images_dir, new_category, create=False)
        if not source.exists() or not source.is_dir():
            raise FileNotFoundError("Kategorie wurde nicht gefunden.")
        if target.exists():
            raise FileExistsError("Eine Kategorie mit diesem Namen existiert bereits.")

        source.rename(target)
        rename_favorites_by_prefix(images_dir, old_category, new_category)
        self.send_json(HTTPStatus.OK, {"category": new_category})

    def handle_rename_image(self) -> None:
        data = self.read_json()
        source = resolve_image_path(self.config["images_dir"], str(data.get("path", "")))
        old_path = relative_media_path(self.config["images_dir"], source)
        new_name = clean_file_name(data.get("newName"), source.suffix)
        target = source.with_name(new_name).resolve()
        if not is_inside(self.config["images_dir"], target):
            raise ValueError("Ungueltiger Zielpfad.")
        if target.exists() and target != source:
            raise FileExistsError("Eine Datei mit diesem Namen existiert bereits.")
        source.rename(target)
        new_path = relative_media_path(self.config["images_dir"], target)
        replace_favorite_path(self.config["images_dir"], old_path, new_path)
        self.send_json(HTTPStatus.OK, {"path": new_path})

    def handle_move_image(self) -> None:
        data = self.read_json()
        source = resolve_image_path(self.config["images_dir"], str(data.get("path", "")))
        old_path = relative_media_path(self.config["images_dir"], source)
        directory = category_dir(self.config["images_dir"], data.get("category"), create=True)
        target = (directory / source.name).resolve()
        if target.exists() and target != source:
            raise FileExistsError("In der Zielkategorie existiert bereits eine Datei mit diesem Namen.")
        if target == source:
            self.send_json(HTTPStatus.OK, {"path": relative_media_path(self.config["images_dir"], source)})
            return
        source_parent = source.parent
        shutil.move(str(source), str(target))
        remove_empty_parent_dirs(self.config["images_dir"], source_parent)
        new_path = relative_media_path(self.config["images_dir"], target)
        replace_favorite_path(self.config["images_dir"], old_path, new_path)
        self.send_json(HTTPStatus.OK, {"path": new_path})

    def handle_delete_image(self) -> None:
        data = self.read_json()
        source = resolve_image_path(self.config["images_dir"], str(data.get("path", "")))
        source_parent = source.parent
        old_path = relative_media_path(self.config["images_dir"], source)
        source.unlink()
        remove_favorite_path(self.config["images_dir"], old_path)
        remove_empty_parent_dirs(self.config["images_dir"], source_parent)
        self.send_json(HTTPStatus.OK, {"deleted": str(data.get("path", ""))})

    def handle_delete_images(self) -> None:
        data = self.read_json()
        images_dir = self.config["images_dir"]
        sources = image_paths_from_payload(images_dir, data)
        deleted: list[str] = []

        for source in sources:
            relative_path = relative_media_path(images_dir, source)
            source_parent = source.parent
            source.unlink()
            remove_empty_parent_dirs(images_dir, source_parent)
            deleted.append(relative_path)

        remove_favorite_paths(images_dir, set(deleted))
        self.send_json(HTTPStatus.OK, {"deleted": deleted})

    def handle_download_images(self) -> None:
        data = self.read_json()
        images_dir = self.config["images_dir"]
        sources = image_paths_from_payload(images_dir, data)
        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for source in sources:
                archive.write(source, arcname=relative_media_path(images_dir, source))

        body = buffer.getvalue()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Disposition", 'attachment; filename="picshelf-images.zip"')
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def handle_favorite_image(self) -> None:
        data = self.read_json()
        source = resolve_image_path(self.config["images_dir"], str(data.get("path", "")))
        image_path = relative_media_path(self.config["images_dir"], source)
        favorite = bool(data.get("favorite"))
        favorites = load_favorites(self.config["images_dir"])
        if favorite:
            favorites.add(image_path)
        else:
            favorites.discard(image_path)
        save_favorites(self.config["images_dir"], favorites)
        self.send_json(HTTPStatus.OK, {"path": image_path, "favorite": favorite})

    def route(self, include_body: bool) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path in {"/", "/index.html"}:
            self.send_bytes(
                HTTPStatus.OK,
                render_app_index(self.config["title"]),
                "text/html; charset=utf-8",
                include_body,
                cache_control="no-store",
            )
            return
        if path.startswith("/assets/"):
            self.send_asset(path.removeprefix("/assets/"), include_body)
            return
        if path == "/api/images":
            payload = json.dumps(
                build_library(self.config["images_dir"], self.config["base_url"]),
                ensure_ascii=False,
            ).encode("utf-8")
            self.send_bytes(
                HTTPStatus.OK,
                payload,
                "application/json; charset=utf-8",
                include_body,
                cache_control="no-store",
            )
            return
        if path == "/api/meta":
            self.send_json(
                HTTPStatus.OK,
                {
                    "version": __version__,
                    "build": self.config["build_label"],
                    "releaseUrl": f"https://github.com/TingelTangelBob/picshelf/releases/tag/v{__version__}",
                },
            )
            return
        if path == "/health":
            self.send_bytes(
                HTTPStatus.OK,
                b"ok\n",
                "text/plain; charset=utf-8",
                include_body,
                cache_control="no-store",
            )
            return
        if path.startswith("/media/"):
            self.send_media(path.removeprefix("/media/"), include_body)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def send_bytes(
        self,
        status: HTTPStatus,
        body: bytes,
        content_type: str,
        include_body: bool,
        cache_control: str,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", cache_control)
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def send_media(self, raw_path: str, include_body: bool) -> None:
        media_path = safe_media_path(raw_path)
        if media_path is None:
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        images_dir = self.config["images_dir"]
        file_path = (images_dir / Path(*media_path.parts)).resolve()
        if not is_inside(images_dir, file_path) or not is_image_file(file_path):
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(file_path.stat().st_size))
        self.send_header("Cache-Control", f"public, max-age={self.config['cache_seconds']}")
        self.end_headers()
        if include_body:
            with file_path.open("rb") as image_file:
                self.wfile.write(image_file.read())

    def send_asset(self, raw_path: str, include_body: bool) -> None:
        asset_path = safe_media_path(raw_path)
        if asset_path is None or len(asset_path.parts) != 1:
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        file_path = (static_dir() / asset_path.name).resolve()
        if not is_inside(static_dir(), file_path) or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        body = file_path.read_bytes()
        self.send_bytes(
            HTTPStatus.OK,
            body,
            content_type,
            include_body,
            cache_control="no-store",
        )

    def log_message(self, format: str, *args: Any) -> None:
        if self.config["access_log"]:
            super().log_message(format, *args)


class PicShelfServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, server_address: tuple[str, int], handler_class: type[BaseHTTPRequestHandler], config: dict[str, Any]):
        super().__init__(server_address, handler_class)
        self.config = config


def make_config() -> dict[str, Any]:
    images_dir = Path(os.environ.get("PICSHELF_IMAGES_DIR", "./images")).resolve()
    max_upload_mb = env_int("PICSHELF_MAX_UPLOAD_MB", 50)
    return {
        "images_dir": images_dir,
        "title": os.environ.get("PICSHELF_TITLE", "PicShelf"),
        "base_url": os.environ.get("PICSHELF_BASE_URL", "").rstrip("/"),
        "cache_seconds": env_int("PICSHELF_CACHE_SECONDS", 3600),
        "max_upload_bytes": max_upload_mb * 1024 * 1024,
        "access_log": env_bool("PICSHELF_ACCESS_LOG", False),
        "build_label": os.environ.get("PICSHELF_BUILD_LABEL", "local"),
    }


def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port = env_int("PORT", 8080)
    config = make_config()
    config["images_dir"].mkdir(parents=True, exist_ok=True)
    server = PicShelfServer((host, port), PicShelfHandler, config)
    print(f"PicShelf serving {config['images_dir']} on http://{host}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()

import tempfile
import unittest
from pathlib import Path

from picshelf.server import (
    DEFAULT_CATEGORY,
    category_dir,
    clean_category_name,
    clean_file_name,
    load_favorites,
    remove_favorite_paths,
    remove_favorites_by_prefix,
    remove_favorite_path,
    replace_favorite_path,
    save_favorites,
    unique_file_path,
    build_library,
    media_url_for,
    safe_media_path,
)


class LibraryTests(unittest.TestCase):
    def test_build_library_groups_images_by_first_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Natur").mkdir()
            (root / "Referenzen").mkdir()
            (root / "Natur" / "wald.jpg").write_bytes(b"jpg")
            (root / "Referenzen" / "diagramm.png").write_bytes(b"png")
            (root / "notiz.txt").write_text("kein bild", encoding="utf-8")

            library = build_library(root)

            self.assertEqual(library["total"], 2)
            self.assertEqual([category["name"] for category in library["categories"]], ["Natur", "Referenzen"])
            self.assertEqual(library["categories"][0]["items"][0]["url"], "/media/Natur/wald.jpg")

    def test_build_library_uses_default_category_for_root_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "logo.webp").write_bytes(b"webp")

            library = build_library(root)

            self.assertEqual(library["categories"][0]["name"], "Allgemein")
            self.assertEqual(library["categories"][0]["items"][0]["path"], "logo.webp")

    def test_build_library_includes_empty_category_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Leer").mkdir()

            library = build_library(root)

            self.assertEqual(library["categories"], [{"name": "Leer", "items": []}])
            self.assertEqual(library["total"], 0)

    def test_build_library_marks_favorites(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Natur").mkdir()
            (root / "Natur" / "wald.jpg").write_bytes(b"jpg")
            save_favorites(root, {"Natur/wald.jpg"})

            library = build_library(root)

            self.assertEqual(library["favorites"], 1)
            self.assertTrue(library["categories"][0]["items"][0]["favorite"])

    def test_media_url_escapes_path_parts(self):
        self.assertEqual(
            media_url_for(Path("Neue Bilder") / "bild 1.jpg", "http://server.local:8099"),
            "http://server.local:8099/media/Neue%20Bilder/bild%201.jpg",
        )


class PathSafetyTests(unittest.TestCase):
    def test_rejects_traversal(self):
        self.assertIsNone(safe_media_path("../secret.jpg"))
        self.assertIsNone(safe_media_path("Natur/../secret.jpg"))

    def test_accepts_nested_media_path(self):
        self.assertEqual(str(safe_media_path("Natur/Wald/bild.jpg")), "Natur/Wald/bild.jpg")

    def test_rejects_bad_category_names(self):
        with self.assertRaises(ValueError):
            clean_category_name("../secret")
        with self.assertRaises(ValueError):
            clean_category_name(".hidden")

    def test_empty_category_is_default_category(self):
        self.assertEqual(clean_category_name(""), DEFAULT_CATEGORY)

    def test_file_name_keeps_only_basename_and_requires_image_extension(self):
        self.assertEqual(clean_file_name(r"C:\upload\bild.png"), "bild.png")
        with self.assertRaises(ValueError):
            clean_file_name("notiz.txt")

    def test_file_name_can_preserve_previous_extension(self):
        self.assertEqual(clean_file_name("neuer-name", ".jpg"), "neuer-name.jpg")

    def test_category_dir_stays_inside_image_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(category_dir(root, "Natur"), root / "Natur")
            self.assertEqual(category_dir(root, "Allgemein"), root)

    def test_unique_file_path_adds_suffix_on_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "bild.jpg").write_bytes(b"jpg")

            self.assertEqual(unique_file_path(root, "bild.jpg").name, "bild-1.jpg")

    def test_favorite_path_can_be_replaced_and_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            save_favorites(root, {"Alt/bild.jpg"})

            replace_favorite_path(root, "Alt/bild.jpg", "Neu/bild.jpg")
            self.assertEqual(load_favorites(root), {"Neu/bild.jpg"})

            remove_favorite_path(root, "Neu/bild.jpg")
            self.assertEqual(load_favorites(root), set())

    def test_multiple_favorites_can_be_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            save_favorites(root, {"A/1.jpg", "A/2.jpg", "B/3.jpg"})

            remove_favorite_paths(root, {"A/1.jpg", "B/3.jpg"})

            self.assertEqual(load_favorites(root), {"A/2.jpg"})

    def test_favorites_can_be_removed_by_category_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            save_favorites(root, {"Archiv/1.jpg", "Archiv/Sub/2.jpg", "Andere/3.jpg"})

            remove_favorites_by_prefix(root, "Archiv")

            self.assertEqual(load_favorites(root), {"Andere/3.jpg"})


if __name__ == "__main__":
    unittest.main()

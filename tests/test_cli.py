import subprocess
import sys
from pathlib import Path


def test_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "backuper", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
    assert "-s" in result.stdout
    assert "-t" in result.stdout
    assert "-e" in result.stdout
    assert "-c" in result.stdout
    assert "-v" in result.stdout


def test_backup_category_filters_and_preserves_tree(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    nested = source_dir / "album" / "2024"
    nested.mkdir(parents=True)
    (source_dir / "album" / "photo.jpg").write_text("jpg", encoding="utf-8")
    (nested / "raw_image.dng").write_text("dng", encoding="utf-8")
    (nested / "notes.txt").write_text("ignore", encoding="utf-8")

    target_dir = tmp_path / "target"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "backuper",
            "-v",
            "INFO",
            "-s",
            str(source_dir),
            "-t",
            str(target_dir),
            "-c",
            "raw-images",
            "-c",
            "export-images",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (target_dir / "album" / "photo.jpg").read_text(encoding="utf-8") == "jpg"
    assert (target_dir / "album" / "2024" / "raw_image.dng").read_text(encoding="utf-8") == "dng"
    assert not (target_dir / "album" / "2024" / "notes.txt").exists()


def test_backup_ext_list_filters_to_requested_files(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "photo.jpeg").write_text("jpeg", encoding="utf-8")
    (source_dir / "scan.nef").write_text("nef", encoding="utf-8")
    (source_dir / "cover.png").write_text("png", encoding="utf-8")

    target_dir = tmp_path / "target"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "backuper",
            "-s",
            str(source_dir),
            "-t",
            str(target_dir),
            "-e",
            "jpeg",
            "-e",
            "png",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (target_dir / "photo.jpeg").read_text(encoding="utf-8") == "jpeg"
    assert (target_dir / "cover.png").read_text(encoding="utf-8") == "png"
    assert not (target_dir / "scan.nef").exists()


def test_backup_skips_empty_branches(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    (source_dir / "keep" / "sub").mkdir(parents=True)
    (source_dir / "skip" / "empty").mkdir(parents=True)
    (source_dir / "keep" / "photo.jpg").write_text("keep", encoding="utf-8")
    (source_dir / "skip" / "notes.txt").write_text("ignore", encoding="utf-8")

    target_dir = tmp_path / "target"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "backuper",
            "-s",
            str(source_dir),
            "-t",
            str(target_dir),
            "-e",
            "jpg",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (target_dir / "keep" / "photo.jpg").read_text(encoding="utf-8") == "keep"
    assert not (target_dir / "skip").exists()

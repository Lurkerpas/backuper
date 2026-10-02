import argparse
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Iterable, Sequence

CATEGORY_EXTENSIONS = {
    "raw-images": {".dng", ".nef", ".orf", ".arw", ".cr2", ".raw"},
    "export-images": {".jpg", ".jpeg", ".png"},
}


def normalize_extension(value: str) -> str:
    return value.lower().strip() if value.lower().strip().startswith(".") else f".{value.lower().strip()}"


def resolve_selected_extensions(values: Iterable[str], categories: Iterable[str]) -> set[str]:
    selected: set[str] = set()

    for value in values:
        candidate = value.strip()
        if not candidate:
            continue
        if candidate.lower() in CATEGORY_EXTENSIONS:
            selected.update(CATEGORY_EXTENSIONS[candidate.lower()])
        else:
            selected.add(normalize_extension(candidate))

    for category in categories:
        key = category.strip().lower()
        if key not in CATEGORY_EXTENSIONS:
            raise ValueError(f"Unsupported category: {category}")
        selected.update(CATEGORY_EXTENSIONS[key])

    if not selected:
        raise ValueError("At least one extension or category must be provided.")

    return selected


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="backuper",
        description="Copy selected image files from a source tree into a mirrored target tree.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbosity",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging verbosity level (defaults to INFO).",
    )
    parser.add_argument("-s", "--source", type=Path, required=True, help="Source directory to scan.")
    parser.add_argument("-t", "--target", type=Path, required=True, help="Target directory where matching files will be copied.")
    parser.add_argument(
        "-e",
        "--extension",
        dest="extensions",
        action="append",
        default=[],
        help="Extension to include; repeat for multiple values, e.g. -e jpg -e png.",
    )
    parser.add_argument(
        "-c",
        "--category",
        dest="categories",
        action="append",
        default=[],
        help="Category filter to include. Supported values: raw-images, export-images.",
    )
    return parser


def is_selected_file(path: Path, extensions: set[str]) -> bool:
    return path.suffix.lower() in extensions


def copy_matching_files(source: Path, target: Path, extensions: set[str]) -> int:
    if not source.exists():
        raise FileNotFoundError(f"Source does not exist: {source}")
    if not source.is_dir():
        raise NotADirectoryError(f"Source is not a directory: {source}")

    source_root = source.resolve()
    target_root = target.resolve()
    if target_root == source_root or target_root.is_relative_to(source_root):
        raise ValueError("Target directory must not be inside the source directory.")

    target.mkdir(parents=True, exist_ok=True)
    copied = 0

    for root, _, files in os.walk(source_root):
        root_path = Path(root)
        for filename in sorted(files):
            file_path = root_path / filename
            if not is_selected_file(file_path, extensions):
                continue
            relative_path = file_path.relative_to(source_root)
            destination = target_root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, destination)
            logging.info("Copied %s -> %s", file_path, destination)
            copied += 1

    logging.info("Finished: copied %d file(s) to %s", copied, target_root)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.verbosity.upper()),
        format="%(levelname)s: %(message)s",
        stream=sys.stdout,
    )

    try:
        selected_extensions = resolve_selected_extensions(args.extensions, args.categories)
        return copy_matching_files(args.source, args.target, selected_extensions)
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        logging.error(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

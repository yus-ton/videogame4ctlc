from __future__ import annotations

from pathlib import Path


EXCLUDE_DIRS = {"__pycache__", ".venv", "venv", ".git", "build", "dist"}
IGNORE_HIDDEN = True  # metti False se vuoi includere .qualcosa


def should_skip(path: Path) -> bool:
    parts = path.parts

    # ignora file/dir nascosti (quelli che iniziano con ".")
    if IGNORE_HIDDEN and any(part.startswith(".") for part in parts):
        return True

    # ignora directory note
    if any(part in EXCLUDE_DIRS for part in parts):
        return True

    return False


def main():
    root = Path.cwd()

    rel_paths: list[str] = []
    for p in root.rglob("*.py"):
        if not p.is_file():
            continue
        if should_skip(p):
            continue
        rel_paths.append(p.relative_to(root).as_posix())

    rel_paths.sort(key=str.lower)

    # stampa
    for rp in rel_paths:
        print(rp)

    # salva anche su file (commenta se non ti serve)
    (root / "paths.txt").write_text("\n".join(rel_paths) + "\n", encoding="utf-8")
    print(f"\nSalvati {len(rel_paths)} path in: {root / 'paths.txt'}")


if __name__ == "__main__":
    main()

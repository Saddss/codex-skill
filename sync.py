# Incremental sync of this repository into a Codex home.
#
# Run: python3 sync.py [--codex-home DIR] [--dry-run] [--prune] [--backup] [-v]
#
# Only AGENTS.md and skills/ are ever touched; credentials, sessions and other
# runtime files in the destination are left alone.

import argparse
import filecmp
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKIP_DIRS = {".git", "__pycache__", ".local-backups", ".venv"}
SKIP_NAMES = {".DS_Store"}


def tracked_files() -> list[Path]:
    """Relative paths of the files this repository owns, in stable order."""
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z", "--", "AGENTS.md", "skills"],
            check=True,
            capture_output=True,
        ).stdout
        names = [Path(name) for name in out.decode().split("\0") if name]
        if names:
            return sorted(names)
    except (OSError, subprocess.CalledProcessError):
        pass
    names = [Path("AGENTS.md")]
    for path in (ROOT / "skills").rglob("*"):
        parts = path.relative_to(ROOT).parts
        if path.is_file() and not SKIP_DIRS.intersection(parts):
            if path.name not in SKIP_NAMES and path.suffix != ".pyc":
                names.append(path.relative_to(ROOT))
    return sorted(names)


def destination(arg: str | None) -> Path:
    if arg:
        return Path(arg).expanduser().resolve()
    from_env = os.environ.get("CODEX_HOME")
    if from_env:
        return Path(from_env).expanduser().resolve()
    return (Path.home() / ".codex").resolve()


def backup_of(dest: Path, rel: Path, backup_root: Path) -> None:
    target = backup_root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dest, target)


def prune_empty_dirs(root: Path) -> None:
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync AGENTS.md and skills/ into a Codex home.")
    parser.add_argument("--codex-home", metavar="DIR", help="destination, default $CODEX_HOME or ~/.codex")
    parser.add_argument("--dry-run", action="store_true", help="report changes without writing")
    parser.add_argument("--prune", action="store_true", help="delete files under skills/ that this repository does not have")
    parser.add_argument("--backup", action="store_true", help="keep replaced and deleted files under .local-backups/")
    parser.add_argument("-v", "--verbose", action="store_true", help="also list unchanged files")
    args = parser.parse_args()

    if not (ROOT / "AGENTS.md").is_file() or not (ROOT / "skills").is_dir():
        print(f"error: {ROOT} does not look like the codex-skill repository", file=sys.stderr)
        return 1

    dest = destination(args.codex_home)
    if dest.exists() and not dest.is_dir():
        print(f"error: {dest} is not a directory", file=sys.stderr)
        return 1

    owned = tracked_files()
    backup_root = ROOT / ".local-backups" / time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    backed_up = 0
    added = updated = unchanged = 0

    for rel in owned:
        src = ROOT / rel
        if not src.is_file():
            print(f"error: listed but missing: {rel}", file=sys.stderr)
            return 1
        target = dest / rel
        if target.is_file() and filecmp.cmp(src, target, shallow=False):
            unchanged += 1
            if args.verbose:
                print(f"same      {rel}")
            continue
        exists = target.is_file()
        if exists and args.backup and not args.dry_run:
            backup_of(target, rel, backup_root)
            backed_up += 1
        print(f"{'update' if exists else 'add':<9} {rel}{'  (dry run)' if args.dry_run else ''}")
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
        if exists:
            updated += 1
        else:
            added += 1

    removed = 0
    only_local: list[Path] = []
    skills_dir = dest / "skills"
    if skills_dir.is_dir():
        for path in sorted(skills_dir.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(dest)
            if rel in owned:
                continue
            if not args.prune:
                only_local.append(rel)
                continue
            if args.backup and not args.dry_run:
                backup_of(path, rel, backup_root)
                backed_up += 1
            print(f"remove    {rel}{'  (dry run)' if args.dry_run else ''}")
            if not args.dry_run:
                path.unlink()
            removed += 1
        if args.prune and not args.dry_run:
            prune_empty_dirs(skills_dir)

    print(
        f"\n{dest}: added {added}, updated {updated}, removed {removed}, "
        f"unchanged {unchanged}, only in destination {len(only_local)}"
    )
    if only_local and args.verbose:
        for rel in only_local:
            print(f"only local {rel}")
    if args.backup and backed_up:
        print(f"backed up {backed_up} file(s) under {backup_root}")
    if args.dry_run:
        print("dry run: nothing was written")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env bash
# Link AGENTS.md and every skill in this repository into a Codex home.
#
# Usage: bash scripts/install.sh [--codex-home DIR] [--dry-run]
#
# Only AGENTS.md and the skills this repository has are touched. Links are
# created once; after that `git pull` is the synchronization. System-managed
# skills such as $CODEX_HOME/skills/.system are never touched.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --codex-home)
      CODEX_HOME="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h | --help)
      echo "usage: bash scripts/install.sh [--codex-home DIR] [--dry-run]"
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [ ! -f "$REPO_ROOT/AGENTS.md" ] || [ ! -d "$REPO_ROOT/skills" ]; then
  echo "ERROR: $REPO_ROOT does not look like the codex-skill repository" >&2
  exit 1
fi

timestamp="$(date +%s)"
linked=0
kept=0
relinked=0
replaced=0
backed_up=0
pruned=0

run() {
  if [ "$DRY_RUN" = 1 ]; then
    return 0
  fi
  "$@"
}

link_entry() {
  src="$1"
  dest="$2"
  label="$3"

  if [ -L "$dest" ]; then
    current="$(readlink "$dest")"
    if [ "$current" = "$src" ]; then
      echo "keep      ${label}"
      kept=$((kept + 1))
      return 0
    fi
    echo "relink    ${label} -> ${src}"
    run ln -sfn "$src" "$dest"
    relinked=$((relinked + 1))
    return 0
  fi

  if [ -e "$dest" ]; then
    if diff -rq "$src" "$dest" >/dev/null 2>&1; then
      echo "replace   ${label} (identical copy)"
      run rm -rf "$dest"
      replaced=$((replaced + 1))
    else
      echo "backup    ${label} -> ${dest}.bak.${timestamp}"
      run mv "$dest" "${dest}.bak.${timestamp}"
      backed_up=$((backed_up + 1))
    fi
  else
    echo "link      ${label} -> ${src}"
    linked=$((linked + 1))
  fi

  run ln -sfn "$src" "$dest"
}

run mkdir -p "$CODEX_HOME/skills"
link_entry "$REPO_ROOT/AGENTS.md" "$CODEX_HOME/AGENTS.md" "AGENTS.md"

for dir in "$REPO_ROOT"/skills/*/; do
  name="$(basename "$dir")"
  link_entry "$REPO_ROOT/skills/$name" "$CODEX_HOME/skills/$name" "skills/$name"
done

# Drop links that point into this repository but no longer resolve, which is
# what a skill removed from the repository leaves behind.
for dest in "$CODEX_HOME"/skills/*; do
  if [ ! -L "$dest" ]; then
    continue
  fi
  if [ -e "$dest" ]; then
    continue
  fi
  case "$(readlink "$dest")" in
    "$REPO_ROOT"/*)
      echo "prune     skills/$(basename "$dest") (dangling)"
      run rm -f "$dest"
      pruned=$((pruned + 1))
      ;;
  esac
done

echo ""
echo "${CODEX_HOME}: linked ${linked}, kept ${kept}, relinked ${relinked}, replaced ${replaced}, backed up ${backed_up}, pruned ${pruned}"
echo "git pull in ${REPO_ROOT} is the synchronization from now on."
if [ "$DRY_RUN" = 1 ]; then
  echo "dry run: nothing was written"
fi

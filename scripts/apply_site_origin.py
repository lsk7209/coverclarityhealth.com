import argparse
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = "{SITE_ORIGIN}"
PUBLIC_PATTERNS = [
    "*.html",
    "aca/*.html",
    "guides/*.html",
    "*.xml",
    "*.txt",
    "content/*.json",
]


def normalize_origin(value: str) -> str:
    origin = (value or "").strip().rstrip("/")
    if not origin.startswith("https://"):
        raise SystemExit("SITE_ORIGIN must be an https:// origin, for example https://example.com")
    if PLACEHOLDER in origin or "localhost" in origin or "127.0.0.1" in origin:
        raise SystemExit("SITE_ORIGIN must be the production origin, not a placeholder or local URL")
    return origin


def iter_public_files():
    seen = set()
    for pattern in PUBLIC_PATTERNS:
        for path in ROOT.glob(pattern):
            if path.is_file() and path not in seen:
                seen.add(path)
                yield path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin", default=os.getenv("SITE_ORIGIN", ""))
    args = parser.parse_args()
    origin = normalize_origin(args.origin)

    changed = []
    for path in iter_public_files():
        text = path.read_text(encoding="utf-8")
        if PLACEHOLDER not in text:
            continue
        path.write_text(text.replace(PLACEHOLDER, origin), encoding="utf-8")
        changed.append(str(path.relative_to(ROOT)))

    print(f"Applied SITE_ORIGIN={origin} to {len(changed)} files.")
    for name in changed:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

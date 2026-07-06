"""CLI entrypoint: reads ig/<date>/cards.json, generates the card PNGs
into the same folder.

Usage (run from the fa-daily-brief repo root):
    python -m scripts.ig_cards.generate 2026-07-06
"""

import argparse
import json
from pathlib import Path

from . import card_builder, renderer


def load_cards_data(cards_file: Path) -> dict:
    return json.loads(cards_file.read_text(encoding="utf-8"))


def run(cards_file: Path, output_dir: Path) -> list[Path]:
    data = load_cards_data(cards_file)
    cards = card_builder.build_cards(data)

    written = []
    for card in cards:
        output_path = output_dir / card["filename"]
        renderer.render_to_png(card["html"], str(output_path))
        written.append(output_path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate IG carousel card PNGs from ig/<date>/cards.json"
    )
    parser.add_argument("date", help="Date folder under ig/, format YYYY-MM-DD")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    cards_dir = repo_root / "ig" / args.date
    cards_file = cards_dir / "cards.json"

    written = run(cards_file, cards_dir)
    for path in written:
        print(f"Saved {path}")


if __name__ == "__main__":
    main()

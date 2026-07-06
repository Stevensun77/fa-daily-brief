import json

from scripts.ig_cards import generate

SAMPLE_DATA = {
    "category": "insurance",
    "handle": "@sghongfire",
    "cover": {"headline": "測試標題"},
    "quotes": [{"quote": "測試金句", "body": "測試內文"}],
    "cta": {"text": "測試 CTA", "line": "測試導流句"},
}


def test_load_cards_data_reads_json(tmp_path):
    cards_file = tmp_path / "cards.json"
    cards_file.write_text(json.dumps(SAMPLE_DATA, ensure_ascii=False), encoding="utf-8")

    data = generate.load_cards_data(cards_file)

    assert data == SAMPLE_DATA


def test_run_writes_expected_png_files(tmp_path):
    cards_file = tmp_path / "cards.json"
    cards_file.write_text(json.dumps(SAMPLE_DATA, ensure_ascii=False), encoding="utf-8")
    output_dir = tmp_path

    written = generate.run(cards_file, output_dir)

    written_names = sorted(p.name for p in written)
    assert written_names == ["01-cover.png", "02-quote.png", "03-cta.png"]
    for path in written:
        assert path.exists()
        assert path.stat().st_size > 0

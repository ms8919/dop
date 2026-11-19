from dop_gallery import render


def render_sample(tmp_path):
    entries = [
        {
            "address": "Domkloster 4, 50667 Köln",
            "img": "images/50667-koeln-domkloster-4.jpg",
            "x": 356481.784,
            "y": 5645284.496,
            "lon": 6.9581,
            "lat": 50.9413,
            "flight_date": "11.05.2025",
            "tile": "32_356_5645",
        }
    ]
    unresolved = [("Nirgendwo 1, 99999 Nichtstadt", "keine passende Adresse gefunden")]
    out = tmp_path / "gallery"
    index = render.render_gallery(entries, unresolved, str(out))
    return open(index, encoding="utf-8").read()


def test_german_ui_strings(tmp_path):
    page = render_sample(tmp_path)
    assert "<title>DOP-Galerie</title>" in page
    assert "DOP-Galerie" in page
    assert "Nicht aufgel" in page
    assert "Aufnahmedatum: 11.05.2025" in page
    assert "DOP-Kachel: 32_356_5645" in page
    assert "Luftbild-Ausschnitte" in page
    assert "keine passende Adresse gefunden" in page


def test_card_style_markers(tmp_path):
    page = render_sample(tmp_path)
    assert 'class="card"' in page
    assert "border-radius: 8px" in page
    assert "box-shadow" in page
    assert "--green:" in page
    assert "--blue:" in page
    assert "&rsaquo;" in page
    assert 'class="topbar"' in page


def test_card_content_and_image_link(tmp_path):
    page = render_sample(tmp_path)
    assert '<img src="images/50667-koeln-domkloster-4.jpg"' in page
    assert "Domkloster 4, 50667 Köln" in page
    assert 'href="images/50667-koeln-domkloster-4.jpg"' in page


def test_no_third_party_branding(tmp_path):
    page = render_sample(tmp_path)
    assert "Stadtwerke" not in page

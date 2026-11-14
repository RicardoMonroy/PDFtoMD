from pathlib import Path

from pdftomd.app import convert, output_path


def test_output_path_never_overwrites(tmp_path):
    src = tmp_path / "doc.pdf"
    assert output_path(src) == tmp_path / "doc.md"
    (tmp_path / "doc.md").write_text("mine")
    assert output_path(src) == tmp_path / "doc (1).md"


def test_convert_docx(tmp_path):
    import docx  # python-docx, test-only

    src = tmp_path / "hola.docx"
    d = docx.Document()
    d.add_heading("Título", 1)
    d.add_paragraph("Hola mundo")
    d.save(src)

    out = convert(src)
    assert out == tmp_path / "hola.md"
    text = out.read_text(encoding="utf-8")
    assert "# Título" in text and "Hola mundo" in text

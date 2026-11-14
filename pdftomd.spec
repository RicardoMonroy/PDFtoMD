# PyInstaller build: `pyinstaller pdftomd.spec` (needs pillow for the icon)
# Windows/Linux: single-file executable. macOS: PDFtoMD.app bundle.
import sys

from PyInstaller.utils.hooks import collect_all

datas = [("src/pdftomd/icon.png", "pdftomd")]
binaries, hiddenimports = [], []
for pkg in ("markitdown", "magika", "pdfminer"):  # model/data files loaded at runtime
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    ["src/pdftomd/__main__.py"],
    pathex=["src"],
    datas=datas,
    binaries=binaries,
    hiddenimports=hiddenimports,
    excludes=["tkinter"],
)
pyz = PYZ(a.pure)
icon = "src/pdftomd/icon.png"

if sys.platform == "darwin":
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="pdftomd", console=False, icon=icon)
    coll = COLLECT(exe, a.binaries, a.datas, name="pdftomd")
    app = BUNDLE(
        coll,
        name="PDFtoMD.app",
        icon=icon,
        bundle_identifier="io.github.ricardomonroy.pdftomd",
        info_plist={"NSHighResolutionCapable": True},
    )
else:
    exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="pdftomd", console=False, icon=icon, upx=False)

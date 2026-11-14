<p align="center"><img src="src/pdftomd/icon.png" width="128" alt="PDFtoMD"></p>

# PDFtoMD

Aplicación de escritorio sencilla, con estética de terminal: **arrastra uno o varios archivos PDF o Word (.docx)** a la ventana y se convierten a **Markdown** en la misma carpeta donde están.

Usa [MarkItDown](https://github.com/microsoft/markitdown) de Microsoft para la conversión y [Qt (PySide6)](https://doc.qt.io/qtforpython/) para la interfaz. Funciona en Linux, Windows y macOS.

- `informe.pdf` → `informe.md` (en la misma carpeta)
- Si `informe.md` ya existe, **no se sobrescribe**: se crea `informe (1).md`
- También puedes usar el botón `[ o elige archivos… ]`, o abrir archivos con `pdftomd archivo.pdf`

## Descarga (sin instalar Python)

En [Releases](https://github.com/RicardoMonroy/PDFtoMD/releases/latest) hay ejecutables listos:

| Sistema | Archivo | Cómo abrirlo |
|---|---|---|
| Windows | `pdftomd-windows-x64.exe` | Doble clic. Si aparece "Windows protegió su PC": *Más información* → *Ejecutar de todas formas* |
| macOS (Apple Silicon) | `pdftomd-macos-arm64.zip` | Descomprime y mueve `PDFtoMD.app` a Aplicaciones. La primera vez: clic derecho → *Abrir* |
| Linux x86_64 | `pdftomd-linux-x86_64.tar.gz` | Ver abajo |

Los ejecutables no están firmados digitalmente, por eso Windows y macOS muestran una advertencia la primera vez.

Linux:

```bash
tar xzf pdftomd-linux-x86_64.tar.gz
install -Dm755 pdftomd ~/.local/bin/pdftomd
install -Dm644 pdftomd.png ~/.local/share/icons/hicolor/512x512/apps/pdftomd.png
install -Dm644 pdftomd.desktop ~/.local/share/applications/pdftomd.desktop
```

## Instalación con pipx (requiere Python 3.10+)

Más ligera que el ejecutable y fácil de actualizar (`pipx upgrade pdftomd`).

### Linux (Arch / Omarchy)

```bash
sudo pacman -S python-pipx
pipx install git+https://github.com/RicardoMonroy/PDFtoMD.git
```

Para que aparezca en el lanzador de aplicaciones con su icono:

```bash
curl -fLo ~/.local/share/applications/pdftomd.desktop --create-dirs https://raw.githubusercontent.com/RicardoMonroy/PDFtoMD/main/pdftomd.desktop
curl -fLo ~/.local/share/icons/hicolor/512x512/apps/pdftomd.png --create-dirs https://raw.githubusercontent.com/RicardoMonroy/PDFtoMD/main/src/pdftomd/icon.png
```

### Windows

1. Instala Python desde [python.org](https://www.python.org/downloads/) (marca "Add python.exe to PATH").
2. En PowerShell:

```powershell
py -m pip install --user pipx
py -m pipx ensurepath
pipx install git+https://github.com/RicardoMonroy/PDFtoMD.git
```

3. Ejecuta `pdftomd` (o crea un acceso directo a `%USERPROFILE%\.local\bin\pdftomd.exe`).

### macOS

```bash
brew install pipx
pipx ensurepath
pipx install git+https://github.com/RicardoMonroy/PDFtoMD.git
```

Ejecuta `pdftomd` desde la terminal.

## Uso

Arrastra los archivos a la ventana. El registro muestra el estado de cada uno:

```
[ ] en espera   [~] convirtiendo   [✓] listo   [✗] error   [-] formato no soportado
```

## Desarrollo

```bash
git clone https://github.com/RicardoMonroy/PDFtoMD.git
cd PDFtoMD
python -m venv .venv && source .venv/bin/activate
pip install -e . pytest python-docx
pytest
python -m pdftomd
```

Generar el ejecutable localmente:

```bash
pip install pyinstaller pillow
pyinstaller pdftomd.spec   # resultado en dist/
```

Publicar una versión: crea un tag `vX.Y.Z` y súbelo (`git tag v0.2.0 && git push --tags`). GitHub Actions compila para los tres sistemas y crea el Release.

## Limitaciones

- Formatos: `.pdf` y `.docx`. El formato antiguo `.doc` no está soportado (guárdalo como `.docx`).
- PDFs escaneados (solo imagen) no tienen texto extraíble: el Markdown saldrá vacío.
- MarkItDown extrae texto y estructura básica; tablas complejas o diseños con columnas pueden perder formato.
- macOS: solo hay ejecutable para Apple Silicon (M1 o posterior). En Mac Intel usa pipx.

## Licencia

MIT

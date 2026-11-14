# PDFtoMD

Aplicación de escritorio sencilla: **arrastra uno o varios archivos PDF o Word (.docx)** a la ventana y se convierten a **Markdown** en la misma carpeta donde están.

Usa [MarkItDown](https://github.com/microsoft/markitdown) de Microsoft para la conversión y [Qt (PySide6)](https://doc.qt.io/qtforpython/) para la interfaz. Funciona en Linux, Windows y macOS.

- `informe.pdf` → `informe.md` (en la misma carpeta)
- Si `informe.md` ya existe, **no se sobrescribe**: se crea `informe (1).md`
- También puedes usar el botón "O elige archivos…"

## Instalación

Requiere **Python 3.10+**. La forma recomendada es [pipx](https://pipx.pypa.io/), que instala la app en su propio entorno aislado.

### Linux (Arch / Omarchy)

```bash
sudo pacman -S python-pipx
pipx install git+https://github.com/RicardoMonroy/PDFtoMD.git
```

Para que aparezca en el lanzador de aplicaciones:

```bash
curl -o ~/.local/share/applications/pdftomd.desktop https://raw.githubusercontent.com/RicardoMonroy/PDFtoMD/main/pdftomd.desktop
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

```bash
pdftomd
```

Arrastra los archivos a la ventana. El registro muestra cada archivo convertido (✔) o con error (✘).

## Desarrollo

```bash
git clone https://github.com/RicardoMonroy/PDFtoMD.git
cd PDFtoMD
python -m venv .venv && source .venv/bin/activate
pip install -e . pytest python-docx
pytest
python -m pdftomd
```

## Limitaciones

- Formatos: `.pdf` y `.docx`. El formato antiguo `.doc` no está soportado (guárdalo como `.docx`).
- PDFs escaneados (solo imagen) no tienen texto extraíble: el Markdown saldrá vacío.
- MarkItDown extrae texto y estructura básica; tablas complejas o diseños con columnas pueden perder formato.

## Licencia

MIT

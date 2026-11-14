"""PDFtoMD: drag & drop PDF/Word files to convert them to Markdown with MarkItDown."""

import sys
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

SUPPORTED = {".pdf", ".docx"}


def output_path(src: Path) -> Path:
    """Same folder, same name, .md. Never overwrite: add ' (n)' if taken."""
    out = src.with_suffix(".md")
    n = 1
    while out.exists():
        out = src.with_name(f"{src.stem} ({n}).md")
        n += 1
    return out


def convert(src: Path, md=None) -> Path:
    if md is None:
        from markitdown import MarkItDown

        md = MarkItDown()
    text = md.convert(str(src)).text_content
    out = output_path(src)
    out.write_text(text, encoding="utf-8")
    return out


class Worker(QObject):
    progress = Signal(str)
    finished = Signal()

    def __init__(self, files):
        super().__init__()
        self.files = files

    def run(self):
        from markitdown import MarkItDown  # slow import, keep off the UI thread

        md = MarkItDown()
        for f in self.files:
            try:
                out = convert(f, md)
                self.progress.emit(f"✔ {f.name}  →  {out.name}")
            except Exception as e:  # one bad file must not stop the batch
                self.progress.emit(f"✘ {f.name}: {e}")
        self.finished.emit()


class DropWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDFtoMD")
        self.resize(560, 420)
        self.setAcceptDrops(True)
        self.thread = None

        self.label = QLabel("Arrastra aquí archivos PDF o Word (.docx)\n\nEl Markdown se guarda en la misma carpeta")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumHeight(150)
        self.label.setStyleSheet("border: 2px dashed palette(mid); border-radius: 12px; font-size: 15px;")

        pick = QPushButton("O elige archivos…")
        pick.clicked.connect(self.pick_files)
        self.log = QListWidget()

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(pick)
        layout.addWidget(self.log)

    def pick_files(self):
        names, _ = QFileDialog.getOpenFileNames(self, "Elegir archivos", "", "Documentos (*.pdf *.docx)")
        self.start([Path(n) for n in names])

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.start([Path(u.toLocalFile()) for u in event.mimeData().urls() if u.isLocalFile()])

    def start(self, paths):
        if self.thread and self.thread.isRunning():
            self.log.addItem("⏳ Espera a que termine la conversión actual")
            return
        files = [p for p in paths if p.suffix.lower() in SUPPORTED and p.is_file()]
        for p in paths:
            if p not in files:
                self.log.addItem(f"– Ignorado (formato no soportado): {p.name}")
        if not files:
            return
        self.label.setText(f"Convirtiendo {len(files)} archivo(s)…")

        self.thread = QThread()
        self.worker = Worker(files)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(lambda: self.label.setText("Listo. Arrastra más archivos"))
        self.thread.start()

    def on_progress(self, msg):
        self.log.addItem(msg)
        self.log.scrollToBottom()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PDFtoMD")
    app.setDesktopFileName("pdftomd")
    w = DropWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

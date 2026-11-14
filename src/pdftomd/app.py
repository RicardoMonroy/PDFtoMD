"""PDFtoMD: drag & drop PDF/Word files to convert them to Markdown with MarkItDown."""

import sys
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QColor, QFontDatabase, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

SUPPORTED = {".pdf", ".docx"}

# Terminal palette (GitHub dark)
BG, PANEL, BORDER = "#0d1117", "#161b22", "#30363d"
FG, DIM, BLUE = "#c9d1d9", "#8b949e", "#58a6ff"
OK, WARN, ERR = "#7ee787", "#d29922", "#f85149"

STYLE = f"""
QWidget {{ background: {BG}; color: {FG}; }}
#prompt {{ color: {DIM}; }}
#drop {{ border: 1px dashed {BORDER}; border-radius: 6px; color: {BLUE}; font-size: 15px; }}
#drop[hover="true"] {{ border-color: {BLUE}; background: {PANEL}; }}
QPushButton {{ background: transparent; color: {DIM}; border: none; padding: 4px; }}
QPushButton:hover {{ color: {BLUE}; }}
QListWidget {{ background: {BG}; border: none; border-top: 1px solid {BORDER}; padding-top: 6px; }}
QListWidget::item {{ padding: 2px 0; }}
QListWidget::item:selected {{ background: {PANEL}; color: inherit; }}
"""


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
    started = Signal(int)            # index of file being converted
    done = Signal(int, bool, str)    # index, ok, message
    finished = Signal()

    def __init__(self, files):
        super().__init__()
        self.files = files

    def run(self):
        from markitdown import MarkItDown  # slow import, keep off the UI thread

        md = MarkItDown()
        for i, f in enumerate(self.files):
            self.started.emit(i)
            try:
                out = convert(f, md)
                self.done.emit(i, True, out.name)
            except Exception as e:  # one bad file must not stop the batch
                self.done.emit(i, False, str(e).splitlines()[0] if str(e) else type(e).__name__)
        self.finished.emit()


class DropWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pdftomd")
        self.resize(600, 440)
        self.setAcceptDrops(True)
        self.setStyleSheet(STYLE)
        self.thread = None
        self.items = []
        self.status = "suelta archivos .pdf o .docx aquí"

        prompt = QLabel("$ pdftomd --drop")
        prompt.setObjectName("prompt")

        self.drop = QLabel()
        self.drop.setObjectName("drop")
        self.drop.setAlignment(Qt.AlignCenter)
        self.drop.setTextFormat(Qt.RichText)
        self.drop.setMinimumHeight(140)

        pick = QPushButton("[ o elige archivos… ]")
        pick.setCursor(Qt.PointingHandCursor)
        pick.clicked.connect(self.pick_files)

        self.log = QListWidget()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.addWidget(prompt)
        layout.addWidget(self.drop)
        layout.addWidget(pick, alignment=Qt.AlignLeft)
        layout.addWidget(self.log)

        self.cursor_on = True
        self.blink = QTimer(self, interval=530, timeout=self.toggle_cursor)
        self.blink.start()
        self.render_drop()

    # --- drop zone -------------------------------------------------------
    def toggle_cursor(self):
        self.cursor_on = not self.cursor_on
        self.render_drop()

    def render_drop(self):
        # invisible block when off, so the text doesn't shift
        cursor = f'<span style="color:{OK if self.cursor_on else BG}">█</span>'
        self.drop.setText(f"[ {self.status} ]{cursor}")

    def set_hover(self, on):
        self.drop.setProperty("hover", on)
        self.drop.style().polish(self.drop)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.set_hover(True)

    def dragLeaveEvent(self, event):
        self.set_hover(False)

    def dropEvent(self, event):
        self.set_hover(False)
        self.start([Path(u.toLocalFile()) for u in event.mimeData().urls() if u.isLocalFile()])

    def pick_files(self):
        names, _ = QFileDialog.getOpenFileNames(self, "Elegir archivos", "", "Documentos (*.pdf *.docx)")
        self.start([Path(n) for n in names])

    # --- log -------------------------------------------------------------
    def add_line(self, text, color):
        item = QListWidgetItem(text)
        item.setForeground(QColor(color))
        self.log.addItem(item)
        self.log.scrollToBottom()
        return item

    def start(self, paths):
        if self.thread and self.thread.isRunning():
            self.add_line("[!] espera a que termine la conversión actual", WARN)
            return
        files = [p for p in paths if p.suffix.lower() in SUPPORTED and p.is_file()]
        for p in paths:
            if p not in files:
                self.add_line(f"[-] {p.name}: formato no soportado", DIM)
        if not files:
            return

        self.files = files
        self.items = [self.add_line(f"[ ] {f.name}", DIM) for f in files]
        self.status = f"convirtiendo 0/{len(files)}…"
        self.render_drop()

        self.thread = QThread()
        self.worker = Worker(files)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.started.connect(self.on_started)
        self.worker.done.connect(self.on_done)
        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def on_started(self, i):
        self.items[i].setText(f"[~] {self.files[i].name}  convirtiendo…")
        self.items[i].setForeground(QColor(WARN))

    def on_done(self, i, ok, msg):
        name = self.files[i].name
        if ok:
            self.items[i].setText(f"[✓] {name} → {msg}")
            self.items[i].setForeground(QColor(OK))
        else:
            self.items[i].setText(f"[✗] {name}: {msg}")
            self.items[i].setForeground(QColor(ERR))
        self.status = f"convirtiendo {i + 1}/{len(self.files)}…"
        self.render_drop()

    def on_finished(self):
        self.status = "listo · suelta más archivos"
        self.render_drop()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("pdftomd")
    app.setDesktopFileName("pdftomd")
    app.setWindowIcon(QIcon(str(Path(__file__).with_name("icon.png"))))
    font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
    font.setPointSize(11)
    app.setFont(font)
    w = DropWindow()
    w.show()
    if len(sys.argv) > 1:  # `pdftomd a.pdf b.docx` / "Open with" from the file manager
        w.start([Path(a) for a in sys.argv[1:]])
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

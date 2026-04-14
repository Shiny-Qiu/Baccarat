import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from ui_main_window import StartDialog, BaccaratMainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setFont(QFont('Microsoft YaHei', 10))

    dlg = StartDialog()
    if dlg.exec() != dlg.DialogCode.Accepted:
        return

    win = BaccaratMainWindow(dlg.get_mode(), dlg.get_chips(), dlg.get_decks())
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QGroupBox, QScrollArea,
    QDialog, QRadioButton, QSpinBox, QButtonGroup, QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush

from game_logic import BaccaratGame

# ------------------------------------------------------------------ #
#  Constants
# ------------------------------------------------------------------ #
TABLE_BG = '#1B5E20'
DARK_BG = '#0D3B0F'
GOLD = '#FFD700'

BET_CONFIG = [
    # (key, name, payout_trad, payout_cf, tooltip)
    ('banker',       '\u5e84',       '1:1(\u62bd\u4f635%)', '1:1 / 6\u70b91:0.5',
     '\u5e84\u5bb6\u8d62\u5219\u83b7\u80dc'),
    ('player',       '\u95f2',       '1:1',           '1:1',
     '\u95f2\u5bb6\u8d62\u5219\u83b7\u80dc'),
    ('tie',          '\u548c',       '1:8',           '1:8',
     '\u53cc\u65b9\u540c\u70b9\u5219\u83b7\u80dc'),
    ('banker_pair',  '\u5e84\u5bf9',     '1:11',          '1:11',
     '\u5e84\u5bb6\u9996\u4e24\u724c\u540c\u70b9'),
    ('player_pair',  '\u95f2\u5bf9',     '1:11',          '1:11',
     '\u95f2\u5bb6\u9996\u4e24\u724c\u540c\u70b9'),
    ('lucky6',       '\u5e78\u8fd06',    '1:12/1:20',     '1:12/1:20',
     '\u5e84\u4ee56\u70b9\u80dc\u51fa\n\u4e24\u724c1:12 \u4e09\u724c1:20'),
    ('lucky6_2card', '\u4e24\u724c\u5e78\u8fd06', '1:22',  '1:22',
     '\u5e84\u4ee5\u4e24\u5f20\u724c6\u70b9\u80dc\u51fa'),
    ('lucky6_3card', '\u4e09\u724c\u5e78\u8fd06', '1:50',  '1:50',
     '\u5e84\u4ee5\u4e09\u5f20\u724c6\u70b9\u80dc\u51fa'),
    ('super_lucky7', '\u8d85\u7ea7\u5e78\u8fd07', '1:30/40/100', '1:30/40/100',
     '\u95f2\u4ee57\u70b9\u80dc+\u5e846\u70b9\n4\u724c1:30 5\u724c1:40 6\u724c1:100'),
    ('lucky7_2card', '\u4e24\u724c\u95f2\u5e787', '1:6',   '1:6',
     '\u95f2\u9996\u4e24\u724c7\u70b9\u80dc\u51fa'),
    ('lucky7_3card', '\u4e09\u724c\u95f2\u5e787', '1:15',  '1:15',
     '\u95f2\u8865\u724c\u540e\u4ee57\u70b9\u80dc\u51fa'),
]

CHIP_VALUES = [10, 50, 100, 500, 1000, 5000]
CHIP_COLORS = {
    10: ('#FFFFFF', '#000000'),   # bg, text
    50: ('#E53935', '#FFFFFF'),
    100: ('#43A047', '#FFFFFF'),
    500: ('#1E88E5', '#FFFFFF'),
    1000: ('#333333', '#FFFFFF'),
    5000: ('#8E24AA', '#FFD700'),
}


# ------------------------------------------------------------------ #
#  Start Dialog
# ------------------------------------------------------------------ #
class StartDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("\u767e\u5bb6\u4e50\u6a21\u62df\u5668")
        self.setFixedSize(380, 300)
        self.setStyleSheet("background-color: #1a3a1a; color: white;")

        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        title = QLabel("\u6b22\u8fce\u6765\u5230\u767e\u5bb6\u4e50")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {GOLD};")
        lay.addWidget(title)

        # Mode
        mode_box = QGroupBox("\u9009\u62e9\u6e38\u620f\u6a21\u5f0f")
        mode_box.setStyleSheet(
            "QGroupBox{color:#FFD700;border:1px solid #4A7A4A;border-radius:4px;padding-top:14px;}"
            "QGroupBox::title{subcontrol-position:top center;}"
        )
        ml = QVBoxLayout(mode_box)
        self.radio_trad = QRadioButton("\u4f20\u7edf\u767e\u5bb6\u4e50\uff08\u5e84\u8d62\u62bd\u4f635%\uff09")
        self.radio_cf = QRadioButton("\u514d\u4f63\u767e\u5bb6\u4e50\uff08\u5e846\u70b9\u80dc\u8d54\u7387\u51cf\u534a\uff09")
        self.radio_trad.setChecked(True)
        for r in (self.radio_trad, self.radio_cf):
            r.setStyleSheet("color:white; font-size:13px;")
        ml.addWidget(self.radio_trad)
        ml.addWidget(self.radio_cf)
        lay.addWidget(mode_box)

        # Chips
        cl = QHBoxLayout()
        cl.addWidget(QLabel("\u521d\u59cb\u7b79\u7801:"))
        self.chips_spin = QSpinBox()
        self.chips_spin.setRange(100, 10_000_000)
        self.chips_spin.setValue(10000)
        self.chips_spin.setSingleStep(100)
        self.chips_spin.setPrefix("\u00a5 ")
        self.chips_spin.setStyleSheet(
            "QSpinBox{background:#2a4a2a;color:white;border:1px solid #4A7A4A;"
            "border-radius:3px;padding:4px;font-size:14px;}"
        )
        cl.addWidget(self.chips_spin)
        lay.addLayout(cl)

        # Start
        btn = QPushButton("\u5f00\u59cb\u6e38\u620f")
        btn.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        btn.setFixedHeight(44)
        btn.setStyleSheet(
            "QPushButton{background-color:#F57C00;color:white;border-radius:6px;}"
            "QPushButton:hover{background-color:#FB8C00;}"
        )
        btn.clicked.connect(self.accept)
        lay.addWidget(btn)

    def get_mode(self) -> str:
        return 'traditional' if self.radio_trad.isChecked() else 'commission_free'

    def get_chips(self) -> int:
        return self.chips_spin.value()


# ------------------------------------------------------------------ #
#  Card Widget  (custom-painted playing card)
# ------------------------------------------------------------------ #
class CardWidget(QWidget):
    W, H = 72, 104

    def __init__(self, parent=None):
        super().__init__(parent)
        self._card = None
        self._visible = False
        self.setFixedSize(self.W, self.H)

    def set_card(self, card):
        self._card = card
        self._visible = True
        self.update()

    def clear(self):
        self._card = None
        self._visible = False
        self.update()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(1, 1, self.W - 2, self.H - 2)

        if not self._visible:
            # Empty placeholder
            pen = QPen(QColor('#55FFFFFF'), 1.5, Qt.PenStyle.DashLine)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(rect, 7, 7)
            p.end()
            return

        if self._card is None:
            # Card back
            p.setPen(QPen(QColor('#0D47A1'), 1.5))
            p.setBrush(QColor('#1565C0'))
            p.drawRoundedRect(rect, 7, 7)
            p.setPen(QPen(QColor(GOLD), 0.6))
            for i in range(8, int(rect.width()), 8):
                p.drawLine(QPointF(rect.left() + i, rect.top() + 6),
                           QPointF(rect.left() + i, rect.bottom() - 6))
            p.end()
            return

        # Card face
        p.setPen(QPen(QColor('#888888'), 1))
        p.setBrush(QColor('white'))
        p.drawRoundedRect(rect, 7, 7)

        color = QColor(self._card.color)
        p.setPen(color)

        # Top-left rank
        f = QFont('Arial', 12, QFont.Weight.Bold)
        p.setFont(f)
        p.drawText(QRectF(rect.left() + 4, rect.top() + 2, 30, 17),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                   self._card.rank_str)
        # Top-left suit
        f.setPointSize(10)
        p.setFont(f)
        p.drawText(QRectF(rect.left() + 4, rect.top() + 17, 30, 15),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                   self._card.suit_symbol)
        # Centre suit (large)
        f2 = QFont('Arial', 30)
        p.setFont(f2)
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._card.suit_symbol)
        # Bottom-right rank
        f.setPointSize(12)
        p.setFont(f)
        p.drawText(QRectF(rect.right() - 34, rect.bottom() - 19, 30, 17),
                   Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom,
                   self._card.rank_str)
        p.end()


# ------------------------------------------------------------------ #
#  Bet Area Widget
# ------------------------------------------------------------------ #
class BetAreaWidget(QFrame):
    left_clicked = pyqtSignal(str)
    right_clicked = pyqtSignal(str)

    def __init__(self, key, name, payout, tooltip, parent=None):
        super().__init__(parent)
        self.key = key
        self._amount = 0
        self._hl = ''  # '', 'win', 'lose'
        self.setObjectName('betArea')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(tooltip)
        self.setMinimumSize(105, 72)
        self.setMaximumHeight(76)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 3, 4, 3)
        lay.setSpacing(1)

        self.name_lbl = QLabel(name)
        self.name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_lbl.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.name_lbl.setStyleSheet(f"color:{GOLD}; background:transparent;")

        self.payout_lbl = QLabel(payout)
        self.payout_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.payout_lbl.setStyleSheet("color:#AAAAAA; font-size:9px; background:transparent;")

        self.amount_lbl = QLabel('')
        self.amount_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.amount_lbl.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        self.amount_lbl.setStyleSheet("color:white; background:transparent;")

        lay.addWidget(self.name_lbl)
        lay.addWidget(self.payout_lbl)
        lay.addWidget(self.amount_lbl)
        self._refresh_style()

    def set_amount(self, v):
        self._amount = v
        self.amount_lbl.setText(f"\u00a5{v:.0f}" if v > 0 else '')
        self._refresh_style()

    def set_highlight(self, state):
        self._hl = state
        self._refresh_style()

    def _refresh_style(self):
        if self._hl == 'win':
            border, bg = '#FFD700', '#1B4D1B'
        elif self._hl == 'lose':
            border, bg = '#CC0000', '#3D1414'
        elif self._amount > 0:
            border, bg = '#FFD700', '#1A4028'
        else:
            border, bg = '#4A7A4A', '#163D1A'
        self.setStyleSheet(
            f"QFrame#betArea{{background:{bg};border:2px solid {border};border-radius:6px;}}"
        )

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.left_clicked.emit(self.key)
        elif ev.button() == Qt.MouseButton.RightButton:
            self.right_clicked.emit(self.key)


# ------------------------------------------------------------------ #
#  Chip Button
# ------------------------------------------------------------------ #
class ChipButton(QPushButton):
    def __init__(self, value, parent=None):
        super().__init__(parent)
        self.value = value
        bg, fg = CHIP_COLORS[value]
        self._bg = bg
        self._fg = fg
        self.setFixedSize(58, 58)
        self.setCheckable(True)
        if value >= 1000:
            self.setText(f"{value // 1000}K")
        else:
            self.setText(str(value))
        self.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self._apply(False)

    def _apply(self, sel):
        bdr = f"3px solid {GOLD}" if sel else f"2px solid #888"
        self.setStyleSheet(
            f"QPushButton{{background:{self._bg};color:{self._fg};"
            f"border:{bdr};border-radius:29px;font-weight:bold;}}"
            f"QPushButton:hover{{border:3px solid {GOLD};}}"
        )

    def setChecked(self, v):
        super().setChecked(v)
        self._apply(v)


# ------------------------------------------------------------------ #
#  Main Window
# ------------------------------------------------------------------ #
class BaccaratMainWindow(QMainWindow):

    def __init__(self, mode: str, balance: int):
        super().__init__()
        self.mode = mode
        self.balance = float(balance)
        self.game = BaccaratGame(mode)

        self.current_bets: dict[str, float] = {}
        self.last_bets: dict[str, float] = {}
        self.selected_chip = 100
        self.is_dealing = False
        self.current_result = None
        self.deal_steps: list[tuple] = []
        self.deal_idx = 0

        self.deal_timer = QTimer(self)
        self.deal_timer.timeout.connect(self._on_deal_step)

        self._build_ui()
        self._update_all()

    # ============================================================== #
    #  UI construction
    # ============================================================== #
    def _build_ui(self):
        self.setWindowTitle("\u767e\u5bb6\u4e50\u6a21\u62df\u5668 \u2014 Baccarat Simulator")
        self.resize(1120, 820)

        cw = QWidget()
        self.setCentralWidget(cw)
        cw.setStyleSheet(f"background-color:{TABLE_BG};")

        root = QVBoxLayout(cw)
        root.setSpacing(6)
        root.setContentsMargins(14, 8, 14, 8)

        # ---- top bar ----
        top = QHBoxLayout()
        self.mode_lbl = QLabel()
        self.mode_lbl.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.mode_lbl.setStyleSheet(f"color:{GOLD};")

        self.switch_btn = QPushButton("\u5207\u6362\u6a21\u5f0f")
        self.switch_btn.setFixedWidth(80)
        self.switch_btn.setStyleSheet(
            "QPushButton{background:#2E7D32;color:white;border:1px solid #FFD700;"
            "border-radius:3px;padding:4px;}"
            "QPushButton:hover{background:#388E3C;}"
        )
        self.switch_btn.clicked.connect(self._switch_mode)

        self.bal_lbl = QLabel()
        self.bal_lbl.setFont(QFont("Microsoft YaHei", 15, QFont.Weight.Bold))
        self.bal_lbl.setStyleSheet(f"color:{GOLD};")

        self.shoe_lbl = QLabel()
        self.shoe_lbl.setStyleSheet("color:#AAAAAA; font-size:12px;")

        top.addWidget(self.mode_lbl)
        top.addWidget(self.switch_btn)
        top.addStretch()
        top.addWidget(self.bal_lbl)
        top.addSpacing(18)
        top.addWidget(self.shoe_lbl)
        root.addLayout(top)

        # ---- card area ----
        card_area = QHBoxLayout()
        card_area.setSpacing(30)

        # player
        p_col = QVBoxLayout()
        p_title = QLabel("\u95f2  PLAYER")
        p_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p_title.setFont(QFont("Microsoft YaHei", 15, QFont.Weight.Bold))
        p_title.setStyleSheet("color:#42A5F5;")
        p_cards = QHBoxLayout()
        p_cards.setSpacing(6)
        p_cards.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.p_cw = [CardWidget() for _ in range(3)]
        for c in self.p_cw:
            p_cards.addWidget(c)
        self.p_pts = QLabel('')
        self.p_pts.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.p_pts.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        self.p_pts.setStyleSheet("color:white;")
        p_col.addWidget(p_title)
        p_col.addLayout(p_cards)
        p_col.addWidget(self.p_pts)

        vs = QLabel("VS")
        vs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        vs.setStyleSheet(f"color:{GOLD};")

        # banker
        b_col = QVBoxLayout()
        b_title = QLabel("\u5e84  BANKER")
        b_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        b_title.setFont(QFont("Microsoft YaHei", 15, QFont.Weight.Bold))
        b_title.setStyleSheet("color:#EF5350;")
        b_cards = QHBoxLayout()
        b_cards.setSpacing(6)
        b_cards.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.b_cw = [CardWidget() for _ in range(3)]
        for c in self.b_cw:
            b_cards.addWidget(c)
        self.b_pts = QLabel('')
        self.b_pts.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.b_pts.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        self.b_pts.setStyleSheet("color:white;")
        b_col.addWidget(b_title)
        b_col.addLayout(b_cards)
        b_col.addWidget(self.b_pts)

        card_area.addStretch()
        card_area.addLayout(p_col)
        card_area.addWidget(vs)
        card_area.addLayout(b_col)
        card_area.addStretch()
        root.addLayout(card_area)

        # ---- result banner ----
        self.result_lbl = QLabel('')
        self.result_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_lbl.setFont(QFont("Microsoft YaHei", 15, QFont.Weight.Bold))
        self.result_lbl.setFixedHeight(32)
        self.result_lbl.setStyleSheet(f"color:{GOLD};")
        root.addWidget(self.result_lbl)

        # ---- betting grid ----
        self.bet_ws: dict[str, BetAreaWidget] = {}
        bet_box = QVBoxLayout()
        bet_box.setSpacing(5)

        row1 = QHBoxLayout()
        row1.setSpacing(5)
        row1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row2 = QHBoxLayout()
        row2.setSpacing(5)
        row2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for i, (key, name, pt, pcf, tip) in enumerate(BET_CONFIG):
            payout = pt if self.mode == 'traditional' else pcf
            bw = BetAreaWidget(key, name, payout, tip)
            bw.left_clicked.connect(self._bet_add)
            bw.right_clicked.connect(self._bet_remove)
            self.bet_ws[key] = bw
            if i < 6:
                row1.addWidget(bw)
            else:
                row2.addWidget(bw)

        bet_box.addLayout(row1)
        bet_box.addLayout(row2)
        root.addLayout(bet_box)

        # ---- chips & buttons ----
        ctrl = QHBoxLayout()
        ctrl.setSpacing(6)
        ctrl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.chip_grp = QButtonGroup(self)
        self.chip_btns: dict[int, ChipButton] = {}
        for v in CHIP_VALUES:
            cb = ChipButton(v)
            self.chip_grp.addButton(cb)
            self.chip_btns[v] = cb
            cb.clicked.connect(lambda _, val=v: self._pick_chip(val))
            ctrl.addWidget(cb)
        self.chip_btns[100].setChecked(True)

        ctrl.addSpacing(18)

        self.repeat_btn = self._make_btn("\u91cd\u590d\u4e0a\u5c40", 80, 36, '#455A64', '#546E7A')
        self.repeat_btn.setEnabled(False)
        self.repeat_btn.clicked.connect(self._repeat_bets)
        ctrl.addWidget(self.repeat_btn)

        self.clear_btn = self._make_btn("\u6e05\u9664\u4e0b\u6ce8", 80, 36, '#C62828', '#D32F2F')
        self.clear_btn.clicked.connect(self._clear_bets)
        ctrl.addWidget(self.clear_btn)

        self.deal_btn = QPushButton("\u53d1  \u724c")
        self.deal_btn.setFixedSize(100, 42)
        self.deal_btn.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        self.deal_btn.setStyleSheet(
            "QPushButton{background:#F57C00;color:white;border-radius:6px;}"
            "QPushButton:hover{background:#FB8C00;}"
            "QPushButton:disabled{background:#5D4037;color:#999;}"
        )
        self.deal_btn.setEnabled(False)
        self.deal_btn.clicked.connect(self._on_deal)
        ctrl.addWidget(self.deal_btn)

        root.addLayout(ctrl)

        # ---- settle detail ----
        self.settle_lbl = QLabel('')
        self.settle_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.settle_lbl.setWordWrap(True)
        self.settle_lbl.setStyleSheet("color:#CCCCCC; font-size:12px;")
        self.settle_lbl.setMinimumHeight(36)
        root.addWidget(self.settle_lbl)

        # ---- bottom: road map + stats ----
        bottom = QHBoxLayout()

        # road
        road_grp = QGroupBox("\u8def\u5355\u8bb0\u5f55")
        road_grp.setStyleSheet(
            "QGroupBox{color:#FFD700;border:1px solid #4A7A4A;border-radius:4px;padding-top:14px;}"
            "QGroupBox::title{subcontrol-position:top center;}"
        )
        rl = QVBoxLayout(road_grp)
        self.road_scroll = QScrollArea()
        self.road_scroll.setFixedHeight(56)
        self.road_scroll.setWidgetResizable(True)
        self.road_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.road_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.road_scroll.setStyleSheet(f"background:{DARK_BG}; border:none;")
        self.road_lbl = QLabel('')
        self.road_lbl.setContentsMargins(6, 4, 6, 4)
        self.road_scroll.setWidget(self.road_lbl)
        rl.addWidget(self.road_scroll)

        # stats
        stats_grp = QGroupBox("\u7edf\u8ba1\u4fe1\u606f")
        stats_grp.setStyleSheet(
            "QGroupBox{color:#FFD700;border:1px solid #4A7A4A;border-radius:4px;padding-top:14px;}"
            "QGroupBox::title{subcontrol-position:top center;}"
        )
        sg = QGridLayout(stats_grp)
        sg.setSpacing(3)
        self.s_lbl: dict[str, QLabel] = {}
        defs = [
            ('total', '\u603b\u5c40\u6570', 0, 0),
            ('bw', '\u5e84\u8d62', 0, 1),
            ('pw', '\u95f2\u8d62', 1, 0),
            ('tw', '\u548c\u5c40', 1, 1),
            ('bp', '\u5e84\u5bf9', 2, 0),
            ('pp', '\u95f2\u5bf9', 2, 1),
            ('streak', '\u8fde\u80dc', 3, 0),
            ('shoe', '\u724c\u9774', 3, 1),
        ]
        for k, nm, r, c in defs:
            lb = QLabel(f"{nm}: 0")
            lb.setStyleSheet("color:#CCCCCC; font-size:11px;")
            self.s_lbl[k] = lb
            sg.addWidget(lb, r, c)

        bottom.addWidget(road_grp, 3)
        bottom.addWidget(stats_grp, 2)
        root.addLayout(bottom)

    @staticmethod
    def _make_btn(text, w, h, bg, hover):
        b = QPushButton(text)
        b.setFixedSize(w, h)
        b.setStyleSheet(
            f"QPushButton{{background:{bg};color:white;border:1px solid #78909C;border-radius:4px;}}"
            f"QPushButton:hover{{background:{hover};}}"
            f"QPushButton:disabled{{background:#37474F;color:#666;}}"
        )
        return b

    # ============================================================== #
    #  Chip / Bet interaction
    # ============================================================== #
    def _pick_chip(self, val):
        self.selected_chip = val
        for v, btn in self.chip_btns.items():
            btn._apply(v == val)

    def _bet_add(self, key):
        if self.is_dealing:
            return
        amt = self.selected_chip
        if self.balance < amt:
            return
        self.current_bets[key] = self.current_bets.get(key, 0) + amt
        self.balance -= amt
        self._refresh_bets()
        self._refresh_bal()
        self._refresh_deal_btn()

    def _bet_remove(self, key):
        if self.is_dealing:
            return
        cur = self.current_bets.get(key, 0)
        rm = min(self.selected_chip, cur)
        if rm <= 0:
            return
        self.current_bets[key] = cur - rm
        if self.current_bets[key] <= 0:
            del self.current_bets[key]
        self.balance += rm
        self._refresh_bets()
        self._refresh_bal()
        self._refresh_deal_btn()

    def _clear_bets(self):
        if self.is_dealing:
            return
        self.balance += sum(self.current_bets.values())
        self.current_bets.clear()
        self._refresh_bets()
        self._refresh_bal()
        self._refresh_deal_btn()

    def _repeat_bets(self):
        if self.is_dealing or not self.last_bets:
            return
        need = sum(self.last_bets.values())
        if self.balance < need:
            QMessageBox.warning(
                self, "\u7b79\u7801\u4e0d\u8db3",
                f"\u91cd\u590d\u4e0a\u5c40\u9700 \u00a5{need:.0f}\uff0c\u5f53\u524d \u00a5{self.balance:.0f}")
            return
        self._clear_bets()
        for k, a in self.last_bets.items():
            self.current_bets[k] = a
            self.balance -= a
        self._refresh_bets()
        self._refresh_bal()
        self._refresh_deal_btn()

    # ============================================================== #
    #  Deal & Animation
    # ============================================================== #
    def _on_deal(self):
        if not self.current_bets or self.is_dealing:
            return
        self.is_dealing = True
        self.deal_btn.setEnabled(False)
        self.result_lbl.setText('')
        self.settle_lbl.setText('')
        for bw in self.bet_ws.values():
            bw.set_highlight('')
        for c in self.p_cw + self.b_cw:
            c.clear()
        self.p_pts.setText('')
        self.b_pts.setText('')

        self.current_result = self.game.play_round()
        self.deal_steps = self._build_steps(self.current_result)
        self.deal_idx = 0
        self.deal_timer.start(500)

    def _build_steps(self, r):
        s = [('p', 0), ('b', 0), ('p', 1), ('b', 1)]
        if not r.is_natural:
            if r.player_drew:
                s.append(('p', 2))
            if r.banker_drew:
                s.append(('b', 2))
        s.append(('end', 0))
        return s

    def _on_deal_step(self):
        if self.deal_idx >= len(self.deal_steps):
            self.deal_timer.stop()
            return
        action, idx = self.deal_steps[self.deal_idx]
        self.deal_idx += 1

        if action == 'p':
            card = self.current_result.player_cards[idx]
            self.p_cw[idx].set_card(card)
            val = self.game.hand_value(self.current_result.player_cards[:idx + 1])
            self.p_pts.setText(f"\u70b9\u6570: {val}")
        elif action == 'b':
            card = self.current_result.banker_cards[idx]
            self.b_cw[idx].set_card(card)
            val = self.game.hand_value(self.current_result.banker_cards[:idx + 1])
            self.b_pts.setText(f"\u70b9\u6570: {val}")
        elif action == 'end':
            self._do_settle()

    # ============================================================== #
    #  Settlement
    # ============================================================== #
    def _do_settle(self):
        self.deal_timer.stop()
        self.is_dealing = False
        r = self.current_result

        self.p_pts.setText(f"\u70b9\u6570: {r.player_value}")
        self.b_pts.setText(f"\u70b9\u6570: {r.banker_value}")

        # Result banner
        nat = "  [\u4f8b\u724c]" if r.is_natural else ""
        if r.winner == 'banker':
            self.result_lbl.setText(
                f"\u5e84\u5bb6\u80dc\uff01 \u5e84 {r.banker_value} \u70b9 > \u95f2 {r.player_value} \u70b9{nat}")
            self.result_lbl.setStyleSheet("color:#EF5350; font-size:16px; font-weight:bold;")
        elif r.winner == 'player':
            self.result_lbl.setText(
                f"\u95f2\u5bb6\u80dc\uff01 \u95f2 {r.player_value} \u70b9 > \u5e84 {r.banker_value} \u70b9{nat}")
            self.result_lbl.setStyleSheet("color:#42A5F5; font-size:16px; font-weight:bold;")
        else:
            self.result_lbl.setText(f"\u548c\u5c40\uff01 \u53cc\u65b9 {r.player_value} \u70b9{nat}")
            self.result_lbl.setStyleSheet("color:#66BB6A; font-size:16px; font-weight:bold;")

        # Settle each bet
        settlements = self.game.settle_bets(self.current_bets, r)
        total_profit = 0.0
        details = []

        for key, amt in self.current_bets.items():
            if key not in settlements:
                continue
            profit, desc = settlements[key]
            payout = amt + profit       # money returned to player
            self.balance += payout
            total_profit += profit
            details.append(desc)
            if profit > 0:
                self.bet_ws[key].set_highlight('win')
            elif profit < 0:
                self.bet_ws[key].set_highlight('lose')

        # Display settlement
        sign = '+' if total_profit >= 0 else ''
        self.settle_lbl.setText(
            f"\u672c\u5c40\u76c8\u4e8f: {sign}{total_profit:.0f}  |  " + '  |  '.join(details))

        self.last_bets = dict(self.current_bets)
        self.current_bets.clear()

        self._refresh_bets()
        self._refresh_bal()
        self._refresh_road()
        self._refresh_stats()
        self.repeat_btn.setEnabled(bool(self.last_bets))
        self._refresh_deal_btn()
        self._refresh_shoe()

        # Game over check
        if self.balance < min(CHIP_VALUES):
            QTimer.singleShot(800, self._game_over)

    def _game_over(self):
        ans = QMessageBox.question(
            self, "\u6e38\u620f\u7ed3\u675f",
            "\u60a8\u7684\u7b79\u7801\u5df2\u7528\u5b8c\uff01\n\u662f\u5426\u91cd\u65b0\u5f00\u59cb\uff1f",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if ans == QMessageBox.StandardButton.Yes:
            self._restart()
        else:
            self.close()

    def _restart(self):
        dlg = StartDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.mode = dlg.get_mode()
            self.balance = float(dlg.get_chips())
            self.game = BaccaratGame(self.mode)
            self.current_bets.clear()
            self.last_bets.clear()
            for c in self.p_cw + self.b_cw:
                c.clear()
            self.p_pts.setText('')
            self.b_pts.setText('')
            self.result_lbl.setText('')
            self.settle_lbl.setText('')
            for bw in self.bet_ws.values():
                bw.set_highlight('')
            self.repeat_btn.setEnabled(False)
            self._update_payouts()
            self._update_all()
        else:
            self.close()

    # ============================================================== #
    #  Mode switch
    # ============================================================== #
    def _switch_mode(self):
        if self.is_dealing:
            return
        self.mode = 'commission_free' if self.mode == 'traditional' else 'traditional'
        self.game.mode = self.mode
        self._update_payouts()
        self._refresh_mode()

    def _update_payouts(self):
        for key, name, pt, pcf, tip in BET_CONFIG:
            if key in self.bet_ws:
                self.bet_ws[key].payout_lbl.setText(
                    pt if self.mode == 'traditional' else pcf)

    # ============================================================== #
    #  Refresh helpers
    # ============================================================== #
    def _update_all(self):
        self._refresh_mode()
        self._refresh_bal()
        self._refresh_bets()
        self._refresh_shoe()
        self._refresh_deal_btn()
        self._refresh_stats()
        self._refresh_road()

    def _refresh_mode(self):
        t = "\u4f20\u7edf\u767e\u5bb6\u4e50" if self.mode == 'traditional' else "\u514d\u4f63\u767e\u5bb6\u4e50"
        self.mode_lbl.setText(f"\u6a21\u5f0f: {t}")

    def _refresh_bal(self):
        self.bal_lbl.setText(f"\u7b79\u7801: \u00a5{self.balance:,.0f}")

    def _refresh_bets(self):
        for k, bw in self.bet_ws.items():
            bw.set_amount(self.current_bets.get(k, 0))

    def _refresh_shoe(self):
        self.shoe_lbl.setText(
            f"\u724c\u9774: {self.game.shoe.remaining}/{self.game.shoe.total_cards}")
        self.s_lbl['shoe'].setText(
            f"\u724c\u9774: {self.game.shoe.remaining}\u5f20")

    def _refresh_deal_btn(self):
        ok = bool(self.current_bets) and not self.is_dealing
        self.deal_btn.setEnabled(ok)

    def _refresh_road(self):
        html_parts = []
        for r in self.game.history[-60:]:
            if r.winner == 'banker':
                html_parts.append('<span style="color:#EF5350;font-size:20px;">\u25cf</span>')
            elif r.winner == 'player':
                html_parts.append('<span style="color:#42A5F5;font-size:20px;">\u25cf</span>')
            else:
                html_parts.append('<span style="color:#66BB6A;font-size:20px;">\u25cf</span>')
        self.road_lbl.setText(' '.join(html_parts))
        # auto-scroll right
        sb = self.road_scroll.horizontalScrollBar()
        sb.setValue(sb.maximum())

    def _refresh_stats(self):
        h = self.game.history
        n = len(h)
        if n == 0:
            return
        bw = sum(1 for r in h if r.winner == 'banker')
        pw = sum(1 for r in h if r.winner == 'player')
        tw = sum(1 for r in h if r.winner == 'tie')
        bp = sum(1 for r in h if r.banker_pair)
        pp = sum(1 for r in h if r.player_pair)

        self.s_lbl['total'].setText(f"\u603b\u5c40\u6570: {n}")
        self.s_lbl['bw'].setText(f"\u5e84\u8d62: {bw} ({bw/n*100:.1f}%)")
        self.s_lbl['pw'].setText(f"\u95f2\u8d62: {pw} ({pw/n*100:.1f}%)")
        self.s_lbl['tw'].setText(f"\u548c\u5c40: {tw} ({tw/n*100:.1f}%)")
        self.s_lbl['bp'].setText(f"\u5e84\u5bf9: {bp}")
        self.s_lbl['pp'].setText(f"\u95f2\u5bf9: {pp}")

        # streak
        last = h[-1].winner
        cnt = 0
        for r in reversed(h):
            if r.winner == last:
                cnt += 1
            else:
                break
        names = {'banker': '\u5e84', 'player': '\u95f2', 'tie': '\u548c'}
        self.s_lbl['streak'].setText(f"\u8fde\u80dc: {names[last]} \u00d7{cnt}")

    # ============================================================== #
    #  Keyboard shortcut
    # ============================================================== #
    def keyPressEvent(self, ev):
        if ev.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            if self.deal_btn.isEnabled():
                self._on_deal()
        super().keyPressEvent(ev)

import json
from types import TracebackType
from typing import Tuple, Type

import keyboard
from PySide6 import QtCore, QtGui, QtWidgets

from src.overlay.api_checking import find_player
from src.overlay.custom_widgets import CustomKeySequenceEdit
from src.overlay.logging_func import get_logger
from src.overlay.overlay_widget import AoEOverlay
from src.overlay.settings import settings
from src.overlay.worker import scheldule

str_profile_en = "Profile"
str_no_player_identified_en = "No player identified"
str_id_en = "Steam ID / Profile ID / Name"
str_search_en = "Search"
str_overlay_en = "Overlay"
str_hotkey_en = "Hotkey for showing and hiding overlay:"
str_hotkey_tip_en = "Hotkey for showing and hiding overlay."
str_overlay_fontsize_en = "Overlay font size:"
str_overlay_position_en = "Change/fix overlay position"

str_profile = "Profile 玩家信息"
str_no_player_identified = "没有辨别到玩家"
str_id = "SteamID / 玩家档案ID/ 玩家昵称"
str_search = "搜索"
str_overlay = "Overlay 游戏内覆盖"
str_hotkey = "快捷键（显示/关闭游戏内覆盖）:"
str_hotkey_tip = "设置 显示/关闭游戏内覆盖 的快捷键"
str_overlay_fontsize = "游戏内覆盖的字体大小:"
str_overlay_position = "修改游戏内覆盖的位置(再点一次锁定位置)"

logger = get_logger(__name__)


class SettingsTab(QtWidgets.QWidget):
    new_profile = QtCore.Signal()
    show_hide_overlay = QtCore.Signal()

    def __init__(self, parent):
        super().__init__(parent)
        self.overlay_widget = AoEOverlay()
        self.init_UI()
        self.show_hide_overlay.connect(self.overlay_widget.show_hide)

    def init_UI(self):
        # Layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(25)
        self.setLayout(self.main_layout)

        ### Profile box
        profile_box = QtWidgets.QGroupBox(str_profile)
        profile_box.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                  QtWidgets.QSizePolicy.Fixed))
        profile_box.setMinimumSize(400, 100)
        profile_box_layout = QtWidgets.QGridLayout()
        profile_box.setLayout(profile_box_layout)
        self.main_layout.addWidget(profile_box)

        # Profile info
        self.profile_info = QtWidgets.QLabel(str_no_player_identified)
        self.profile_info.setStyleSheet("font-weight: bold")
        self.profile_info.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse)
        profile_box_layout.addWidget(self.profile_info)

        self.profile_link = QtWidgets.QLabel("")
        self.profile_link.setOpenExternalLinks(True)
        profile_box_layout.addWidget(self.profile_link, 1, 0)

        # Multi search
        self.multi_search = QtWidgets.QLineEdit()
        self.multi_search.setPlaceholderText(str_id)
        self.multi_search.setToolTip(
            'Search for your account with one of these (Steam ID / Profile ID / Name).'
            ' Searching by name might not find the correct player.')
        self.multi_search.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.multi_search.setMaximumWidth(220)
        profile_box_layout.addWidget(self.multi_search, 2, 0)

        # Multi search button
        self.multi_search_btn = QtWidgets.QPushButton(str_search)
        self.multi_search_btn.clicked.connect(self.find_profile)
        self.multi_search_btn.setShortcut("Return")
        self.multi_search_btn.setToolTip(
            'Search for your account with one of these (Steam ID / Profile ID / Name).'
            ' Searching by name might not find the correct player.')
        profile_box_layout.addWidget(self.multi_search_btn, 2, 1)

        # Notification
        self.notification_label = QtWidgets.QLabel()
        profile_box_layout.addWidget(self.notification_label, 3, 0)

        ### Overlay box
        overlay_box = QtWidgets.QGroupBox(str_overlay)
        overlay_box.setMinimumSize(400, 100)
        overlay_box.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                  QtWidgets.QSizePolicy.Fixed))
        overlay_layout = QtWidgets.QGridLayout()
        overlay_box.setLayout(overlay_layout)
        self.main_layout.addWidget(overlay_box)

        # Hotkey for overlay
        key_label = QtWidgets.QLabel(str_hotkey)
        overlay_layout.addWidget(key_label, 0, 0)

        self.key_showhide = CustomKeySequenceEdit(self)
        self.key_showhide.setMaximumWidth(100)
        self.key_showhide.setToolTip(str_hotkey_tip)
        overlay_layout.addWidget(self.key_showhide, 0, 1)
        self.key_showhide.key_changed.connect(self.hotkey_changed)

        # Overlay font
        font_label = QtWidgets.QLabel(str_overlay_fontsize)
        overlay_layout.addWidget(font_label, 1, 0)

        self.font_size_combo = QtWidgets.QComboBox()
        for i in range(1, 50):
            self.font_size_combo.addItem(f"{i} pt")
        self.font_size_combo.setCurrentIndex(settings.font_size - 1)
        self.font_size_combo.currentIndexChanged.connect(
            self.font_size_changed)
        overlay_layout.addWidget(self.font_size_combo, 1, 1)

        # Position change button
        self.btn_change_position = QtWidgets.QPushButton(
            str_overlay_position)
        self.btn_change_position.setToolTip(
            "Click to change overlay position. Click again to fix its position."
        )
        self.btn_change_position.clicked.connect(
            self.overlay_widget.change_state)
        overlay_layout.addWidget(self.btn_change_position, 2, 0, 1, 2)

        ### Messages
        self.msg = QtWidgets.QLabel()
        self.msg.setOpenExternalLinks(True)
        self.main_layout.addWidget(self.msg)

        # Create update button
        self.update_button = QtWidgets.QPushButton("New update!")
        self.update_button.setMaximumWidth(400)
        self.update_button.setToolTip("Click here to download new app version")
        self.update_button.setStyleSheet(
            'background-color: #3bb825; color: black')
        self.update_button.hide()
        self.main_layout.addWidget(self.update_button)

        ### chs box
        chs_box = QtWidgets.QGroupBox("汉化补丁")
        chs_box.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                  QtWidgets.QSizePolicy.Fixed))
        chs_box.setMinimumSize(400, 100)
        chs_box_layout = QtWidgets.QGridLayout()
        chs_box.setLayout(chs_box_layout)
        self.main_layout.addWidget(chs_box)
        # chs info
        self.chs_info = QtWidgets.QLabel('汉化补丁由帝国时代4中文社区<a href="https://www.aoe4cn.com/">www.aoe4cn.com</a>提供支持。')
        self.chs_info.setOpenExternalLinks(True)
        chs_box_layout.addWidget(self.chs_info)

    def start(self):
        # Initialize
        self.update_profile_info()
        self.init_hotkeys()

        if settings.steam_id or settings.profile_id:
            self.new_profile.emit()

    def init_hotkeys(self):
        if settings.overlay_hotkey:
            try:
                self.key_showhide.setKeySequence(
                    QtGui.QKeySequence.fromString(settings.overlay_hotkey))
                keyboard.add_hotkey(settings.overlay_hotkey,
                                    self.show_hide_overlay.emit)
            except Exception:
                logger.exception("Failed to set hotkey")
                settings.overlay_hotkey = ""
                self.key_showhide.setKeySequence(
                    QtGui.QKeySequence.fromString(""))

    def update_profile_info(self):
        """ Updates profile information based on found steam_id and profile_id"""
        s = []
        if settings.player_name:
            # s.append(settings.player_name)
            s.append(f"玩家昵称：{settings.player_name}")
        if settings.steam_id:
            # s.append(f"Steam_id: {settings.steam_id}")
            s.append(f"Steam ID: {settings.steam_id}")
        if settings.profile_id:
            # s.append(f"Profile_id: {settings.profile_id}")
            s.append(f"玩家档案ID: {settings.profile_id}")

        if s:
            self.profile_info.setText('\n'.join(s))
            self.profile_info.setStyleSheet(
                "color: #359c20; font-weight: bold")
            self.profile_link.setText(
                # f'<a href="https://aoe4world.com/players/{settings.profile_id}">AoE4 World profile</a>'
                f'<a href="https://aoe4world.com/players/{settings.profile_id}">AoE4 World 玩家档案</a>'
            )
        else:
            self.profile_info.setText("No player identified")
            self.profile_link.setText("")

    def notification(self, text: str, color: str = "black"):
        """ Shows a notification"""
        self.notification_label.setText(text)
        self.notification_label.setStyleSheet(f"color: {color}")

    def message(self, text: str, color: str = "black"):
        """ Shows a message"""
        self.msg.setText(text)
        self.msg.setStyleSheet(f"color: {color}")

    def aoe4net_error_msg(self):
        self.message(
            f'An issue with <a href="https://aoeiv.net/">AoEIV.net</a> servers. Data shown on the overlay are unaffected,<br> \
             but other stats in this app might not show correctly.<br>For additional stats check your <a href="https://aoe4world.com/players/{settings.profile_id}">AoE4 World profile</a>.',
            color='red')

    def find_profile(self):
        """ Attempts to find player ids based on provided text (name, either id)"""
        self.notification_label.setText("")
        text = self.multi_search.text().strip()
        if not text:
            return
        logger.info(f"Finding a player with key: {text}")

        scheldule(self.find_profile_finish,
                  find_player,
                  text,
                  error_callback=self.error_when_finding_profile)

    def error_when_finding_profile(self,
                                   exc_data: Tuple[Type[BaseException],
                                                   Exception, TracebackType]):
        """ Decoding error when finding player profile indicates an issue with AoEIV.net"""
        exctype, value, formatted = exc_data
        if exctype == json.decoder.JSONDecodeError:
            self.aoe4net_error_msg()
            logger.warning(
                f"Decoding error when finding a player\n{formatted}")
        else:
            logger.warning(formatted)

    def find_profile_finish(self, result: bool):
        if result:
            self.new_profile.emit()
            self.update_profile_info()
            self.notification("Player found!", "#359c20")
        else:
            self.notification("Failed to find such player!", "red")

    def font_size_changed(self):
        font_size = self.font_size_combo.currentIndex() + 1
        settings.font_size = font_size
        self.overlay_widget.update_style(font_size)

    def hotkey_changed(self, new_hotkey: str):
        """ Checks whether the hotkey is actually new and valid.
        Updates keyboard threads"""
        old_hotkey = settings.overlay_hotkey
        new_hotkey = CustomKeySequenceEdit.convert_hotkey(new_hotkey)

        if new_hotkey == "Del":
            self.key_showhide.setKeySequence(QtGui.QKeySequence.fromString(""))
            settings.overlay_hotkey = ""
            return
        elif not new_hotkey or new_hotkey == settings.overlay_hotkey:
            return

        try:
            keyboard.add_hotkey(new_hotkey, self.show_hide_overlay.emit)
            if settings.overlay_hotkey:
                keyboard.remove_hotkey(settings.overlay_hotkey)
            settings.overlay_hotkey = new_hotkey
            logger.info(f"Setting new hotkey to: {new_hotkey}")
        except Exception:
            logger.exception(f"Failed to set hotkey: {new_hotkey}")
            self.message("Failed to use this hotkey", color='red')
            self.key_showhide.setKeySequence(
                QtGui.QKeySequence.fromString(old_hotkey))

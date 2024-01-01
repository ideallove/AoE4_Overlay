import random
from typing import Dict, Optional

from PySide2 import QtCore, QtGui, QtWidgets

from overlay.aoe4_data import civ_data, map_data
from overlay.helper_func import file_path

str_random_civ_en = "Randomize civ"
str_random_map_en = "Randomize map"

str_random_civ = "随机文明"
str_random_map = "随机地图"


class RandomTab(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.current_map: Optional[str] = None
        self.current_civ: Optional[str] = None
        self.pixmaps: Dict[str, QtGui.QPixmap] = dict()
        self.initUI()
        self.randomize_map()
        self.randomize_civ()

    def initUI(self):
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(10, 40, 10, 10)
        self.setLayout(layout)

        # Civ layout
        civ_layout = QtWidgets.QVBoxLayout()
        civ_layout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        layout.addLayout(civ_layout)
        civ_layout.addItem(QtWidgets.QSpacerItem(0, 50))

        # Civ image
        self.civ_image = QtWidgets.QLabel()
        self.civ_image.setFixedSize(QtCore.QSize(270, 150))
        civ_layout.addWidget(self.civ_image)

        # Civ label
        self.civ_label = QtWidgets.QLabel()
        self.civ_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.civ_label.setStyleSheet("font-weight: bold; font-size: 20px")
        civ_layout.addWidget(self.civ_label)
        civ_layout.addItem(QtWidgets.QSpacerItem(0, 100))

        # Randomize civ
        rnd_civ = QtWidgets.QPushButton(str_random_civ)
        rnd_civ.clicked.connect(self.randomize_civ)
        rnd_civ.setMinimumHeight(30)
        civ_layout.addWidget(rnd_civ)

        # Map layout
        map_layout = QtWidgets.QVBoxLayout()
        map_layout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        layout.addLayout(map_layout)

        # Map image
        self.map_image = QtWidgets.QLabel()
        self.map_image.setFixedSize(QtCore.QSize(270, 270))
        map_layout.addWidget(self.map_image)

        # Map label
        self.map_label = QtWidgets.QLabel()
        self.map_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.map_label.setStyleSheet("font-weight: bold; font-size: 20px")
        map_layout.addWidget(self.map_label)
        map_layout.addItem(QtWidgets.QSpacerItem(0, 30))

        # Randomize map
        rnd_map = QtWidgets.QPushButton(str_random_map)
        rnd_map.clicked.connect(self.randomize_map)
        rnd_map.setMinimumHeight(30)
        map_layout.addWidget(rnd_map)

    def get_pixmap(self, file_path: str,
                   widget: QtWidgets.QWidget) -> QtGui.QPixmap:
        """ Asset manager for pixmaps

        Returns a pixmap from `file_path` scaled for `widget`"""
        if file_path in self.pixmaps:
            return self.pixmaps[file_path]
        pixmap = QtGui.QPixmap(file_path)
        pixmap = pixmap.scaled(widget.width(), widget.height(),
                               QtCore.Qt.KeepAspectRatio,
                               QtCore.Qt.FastTransformation)
        self.pixmaps[file_path] = pixmap
        return pixmap

    def randomize_civ(self):
        civ_name = random.choice(tuple(civ_data.values()))
        if civ_name == self.current_civ:
            self.randomize_civ()
            return
        self.current_civ = civ_name

        img_path = file_path(f"img/flags/{civ_name}.webp")
        pixmap = self.get_pixmap(img_path, self.civ_image)
        self.civ_image.setPixmap(pixmap)
        self.civ_label.setText(civ_name)

    def randomize_map(self):
        map_name = random.choice(tuple(map_data.values()))
        if map_name in (self.current_map, map_data[-1]):
            self.randomize_map()
            return
        self.current_map = map_name

        img_path = file_path(f"img/maps/{map_name.replace(' ','_')}.png")
        pixmap = self.get_pixmap(img_path, self.map_image)
        self.map_image.setPixmap(pixmap)
        self.map_label.setText(map_name)

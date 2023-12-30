#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import subprocess
import sys
import webbrowser
from functools import partial
from types import TracebackType
from typing import Type

from PySide6 import QtCore, QtGui, QtWidgets

from src.overlay.email_log import send_email_log
from src.overlay.helper_func import file_path, is_compiled, pyqt_wait
from src.overlay.logging_func import get_logger
from src.overlay.settings import CONFIG_FOLDER, settings
from src.overlay.tab_main import TabWidget

str_file = "文件"
str_setting = "设置"
str_link = "链接"

logger = get_logger(__name__)

VERSION = "1.4.5"
title_chs = "帝国时代4:游戏工具箱 (Overlay1.4.5汉化版内部测试)"

# Might or might not help
os.environ["PYTHONIOENCODING"] = "utf-8"


def excepthook(exc_type: Type[BaseException], exc_value: Exception, exc_tback: TracebackType):
    """ 提供最顶层的异常处理。记录未处理的异常并清理地关闭应用程序。"""

    # 检查是否是Unicode编码错误
    if isinstance(exc_value, UnicodeEncodeError):
        logger.warning("Unicode error")  # 记录Unicode错误的警告
        return  # 返回，不执行后续代码

    # 记录异常信息
    logger.exception("Unhandled exception!", exc_info=(exc_type, exc_value, exc_tback))

    # 如果程序被编译，则发送电子邮件日志
    # try:
    #     if is_compiled() and settings.send_email_logs:
    #         send_email_log(VERSION, exc_type, exc_value, exc_tback)
    # except Exception:
    #     logger.exception("Failed to send a log through email")  # 如果发送邮件失败，则记录异常

    # 尝试保存设置
    try:
        settings.save()  # 尝试保存程序设置
    except Exception:
        logger.exception("Failed to save settings")  # 如果保存设置失败，记录异常

    # 关闭其他线程
    try:
        Main.centralWidget().stop_checking_api()  # 尝试停止检查API的线程
    except Exception:
        pass  # 如果出现异常，忽略

    sys.exit()  # 退出程序


sys.excepthook = excepthook  # 将全局异常处理钩子设置为excepthook函数


class MainApp(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUI()
        self.centralWidget().start()

    def initUI(self):
        # self.setWindowTitle(f"AoE IV: Overlay ({VERSION})")
        self.setWindowTitle(title_chs)
        self.setWindowIcon(QtGui.QIcon(file_path('img/aoe4_sword_shield.ico')))
        self.setGeometry(0, 0, settings.app_width, settings.app_height)
        self.move(QtGui.QGuiApplication.primaryScreen().availableGeometry().center() -
                  QtCore.QPoint(int(self.width() / 2), int(self.height() / 2)))

        # Create central widget
        self.setCentralWidget(TabWidget(self, VERSION))

        ### Create menu bar items
        menubar = self.menuBar()
        file_menu = menubar.addMenu(str_file)
        # graphs_menu = menubar.addMenu('Graphs')
        settings_menu = menubar.addMenu(str_setting)
        link_menu = menubar.addMenu(str_link)

        # Html
        icon = self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_DirLinkIcon'))
        htmlAction = QtGui.QAction(icon, 'Html files', self)
        htmlAction.triggered.connect(
            lambda: subprocess.run(['explorer', file_path("html")]))
        file_menu.addAction(htmlAction)

        # Config
        icon = self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_DirLinkIcon'))
        htmlAction = QtGui.QAction(icon, 'Config/logs', self)
        htmlAction.triggered.connect(
            lambda: subprocess.run(['explorer', CONFIG_FOLDER]))
        file_menu.addAction(htmlAction)

        # Exit
        icon = self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_DialogCloseButton'))
        exitAction = QtGui.QAction(icon, 'Exit', self)
        exitAction.triggered.connect(QtCore.QCoreApplication.instance().quit)
        file_menu.addAction(exitAction)

        # Report crashes
        # email_action = QtGui.QAction('Report crashes', self)
        # email_action.setCheckable(True)
        # email_action.setChecked(settings.send_email_logs)
        # email_action.triggered.connect(lambda: setattr(
        #     settings, "send_email_logs", not settings.send_email_logs))
        # settings_menu.addAction(email_action)

        # Log matches
        mach_log_action = QtGui.QAction('Log match data', self)
        mach_log_action.setCheckable(True)
        mach_log_action.setChecked(settings.log_matches)
        mach_log_action.triggered.connect(
            lambda: setattr(settings, "log_matches", not settings.log_matches))
        settings_menu.addAction(mach_log_action)

        # Github
        icon = QtGui.QIcon(file_path("img/github.png"))
        githubAction = QtGui.QAction(icon, 'App on Github', self)
        githubAction.triggered.connect(
            partial(webbrowser.open,
                    "https://github.com/FluffyMaguro/AoE4_Overlay"))
        link_menu.addAction(githubAction)

        # Discord
        icon = QtGui.QIcon(file_path("img/discord.png"))
        mdiscordAction = QtGui.QAction(icon, 'My discord', self)
        mdiscordAction.triggered.connect(
            partial(webbrowser.open, "https://discord.gg/FtGdhqD"))
        link_menu.addAction(mdiscordAction)

        # Maguro
        icon = QtGui.QIcon(file_path("img/maguro.jpg"))
        maguroAction = QtGui.QAction(icon, 'Maguro.one', self)
        maguroAction.triggered.connect(
            partial(webbrowser.open, "https://www.maguro.one/"))
        link_menu.addAction(maguroAction)

        # Paypal
        icon = QtGui.QIcon(file_path("img/paypal.png"))
        paypalAction = QtGui.QAction(icon, 'Donate', self)
        paypalAction.triggered.connect(
            partial(webbrowser.open,
                    "https://www.paypal.com/paypalme/FluffyMaguro"))
        link_menu.addAction(paypalAction)

        # AoEIV.net
        icon = QtGui.QIcon(file_path("img/aoeivnet.png"))
        aoe4netaction = QtGui.QAction(icon, 'AoEIV.net', self)
        aoe4netaction.triggered.connect(
            partial(webbrowser.open, "https://aoeiv.net/"))
        link_menu.addAction(aoe4netaction)

        # AoE4 World
        icon = QtGui.QIcon(file_path("img/aoe4worldcom.ico"))
        aoe4worldaction = QtGui.QAction(icon, 'AoE4 World', self)
        aoe4worldaction.triggered.connect(
            partial(webbrowser.open, "https://aoe4world.com/"))
        link_menu.addAction(aoe4worldaction)

        # AoE4 CN
        icon = QtGui.QIcon(file_path("img/aoe4worldcom.ico"))
        aoe4cnaction = QtGui.QAction(icon, 'AoE4 CN', self)
        aoe4cnaction.triggered.connect(
            partial(webbrowser.open, "https://www.aoe4cn.com/"))
        link_menu.addAction(aoe4cnaction)

        # Which graphs to show
        # self.show_graph_actions = []
        # for i in (1, 2, 3, 4):
        #     action = QtGui.QAction(f'Show {i}v{i}', self)
        #     self.show_graph_actions.append(action)
        #     action.setCheckable(True)
        #     action.setChecked(True)
        #     action.changed.connect(
        #         partial(self.centralWidget().graph_tab.change_plot_visibility,
        #                 i - 1, action))
        #     action.setChecked(settings.show_graph[str(i)])
        #     graphs_menu.addAction(action)

        # lastday = QtGui.QAction("Last 24h", self)
        # lastday.setCheckable(True)
        # lastday.changed.connect(
        #     partial(self.centralWidget().graph_tab.limit_to_day, lastday))
        # graphs_menu.addAction(lastday)
        self.show()

    def closeEvent(self, _):
        """Function called when closing the widget."""
        self.centralWidget().close()

    def update_title(self, name: str):
        self.setWindowTitle(f"AoE IV: Overlay ({VERSION}) – {name}")

    def finish(self):
        try:
            """ Give it some time to stop everything correctly"""
            settings.app_width = self.width()
            settings.app_height = self.height()
            # for i, action in enumerate(self.show_graph_actions):
            #     settings.show_graph[str(i + 1)] = action.isChecked()
            settings.save()
            self.centralWidget().stop_checking_api()
            pyqt_wait(1000)
        except Exception:
            logger.exception("")


if __name__ == '__main__':
    settings.load()
    app = QtWidgets.QApplication(sys.argv)
    Main = MainApp()
    exit_event = app.exec()
    Main.finish()
    sys.exit(exit_event)

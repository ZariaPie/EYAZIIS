import os
import requests
from collections import Counter
from bs4 import BeautifulSoup
from PyQt5 import QtWidgets
from .main_window import Ui_MainWindow
from .help_dialog import Ui_Dialog
from methods import ngram_method as ng, alphabetic_method as al, neural_method as nn


class HelpDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


def benchmark(method):
    import time

    def b_method(ref):
        start = time.time()
        method(ref)
        end = time.time()
        print(f'Execution time: {end - start}')
        ref.local_text_browser.append(f'Execution time: {end - start}')

    return b_method


class Application(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.l_method_combo_box.addItems(['DNN', 'Alphabetic', 'N-gram'])
        self.l_mode_combo_box.addItems(['Local dir', 'Local file', 'Web'])
        self.bind_functions()

    def single_start(self):
        self.local_text_browser.clear()

        src_path = self.l_file_path_text.toPlainText()
        if not src_path:
            return

        text = ''
        mode = self.l_mode_combo_box.currentText()
        if mode == 'Local file':
            try:
                file = open(src_path, 'r', encoding='utf-8')
                text = BeautifulSoup(file.read(), features='html.parser').get_text()
                self.local_text_browser.append(f'Successfully read file: {src_path}\n')
            except OSError:
                self.local_text_browser.append(f'Unable to read file: {src_path}\n')
                return

        elif mode == 'Web':
            document = requests.get(src_path)
            if document.status_code == 200:
                text = BeautifulSoup(document.text, features='html.parser').get_text()
                self.local_text_browser.append(f'Successfully read text from url: {src_path}\n')
            else:
                self.local_text_browser.append(f'Unable to read text from url: {src_path}. '
                                               f'Status code {document.status_code}.\n')
                return

        method = self.l_method_combo_box.currentIndex()
        result = [nn.lang, al.lang, ng.lang][method](text)
        self.local_text_browser.append(f'Language: {result}')

    @benchmark
    def dir_start(self):
        self.local_text_browser.clear()

        src_path = self.l_file_path_text.toPlainText()
        if not src_path:
            return

        method = self.l_method_combo_box.currentIndex()
        summary = list()

        for file_name in os.listdir(src_path):
            print(file_name)
            self.local_text_browser.append(file_name)

            try:
                file = open(src_path + '/' + file_name, 'r', encoding='utf-8')
                text = BeautifulSoup(file.read(), features='html.parser').get_text()
                self.local_text_browser.append(f'Read success.')
            except OSError:
                self.local_text_browser.append(f'Read failure.\n'
                                               f'############################')
                summary.append('Unable to read')
                continue

            result = [nn.lang, al.lang, ng.lang][method](text)
            self.local_text_browser.append(f'Language: {result}\n'
                                           f'############################')
            summary.append(result)

        counter = Counter(summary)
        self.local_text_browser.append(f'Summary:\n'
                                       f'Russian: {counter["Russian"]}\n'
                                       f'English: {counter["English"]}\n'
                                       f'Unable to recognize: {counter["Unable to recognize"]}\n'
                                       f'Unable to read: {counter["Unable to read"]}')

    def select_method(self):
        method = self.l_mode_combo_box.currentText()

        for m in [self.select_file, self.select_dir]:
            try:
                self.l_file_path_browse_btn.clicked.disconnect(m)
            except:
                pass  # ignored

        for m in [self.single_start, self.dir_start]:
            try:
                self.l_method_start_btn.clicked.disconnect(m)
            except:
                pass  # ignored

        if method == 'Local dir':
            self.l_file_path_browse_btn.setEnabled(True)
            self.l_file_path_browse_btn.clicked.connect(self.select_dir)
            self.l_method_start_btn.clicked.connect(self.dir_start)
        elif method == 'Local file':
            self.l_file_path_browse_btn.setEnabled(True)
            self.l_file_path_browse_btn.clicked.connect(self.select_file)
            self.l_method_start_btn.clicked.connect(self.single_start)
        elif method == 'Web':
            self.l_file_path_browse_btn.setEnabled(False)
            self.l_method_start_btn.clicked.connect(self.single_start)

    def select_file(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self)
        if file_name:
            self.l_file_path_text.setPlainText(file_name)

    def select_dir(self):
        dir_name = QtWidgets.QFileDialog.getExistingDirectory(self)
        if dir_name:
            self.l_file_path_text.setPlainText(dir_name)

    def save_as(self):
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, filter='*.txt')
        if file_name:
            file = open(file_name, 'w')
            file.write(self.local_text_browser.toPlainText())

    def bind_functions(self):
        self.action_about.triggered.connect(lambda: HelpDialog().exec_())
        self.l_mode_combo_box.currentTextChanged.connect(self.select_method)
        self.action_save_as.triggered.connect(self.save_as)
        self.l_file_path_browse_btn.clicked.connect(self.select_dir)
        self.l_method_start_btn.clicked.connect(self.dir_start)

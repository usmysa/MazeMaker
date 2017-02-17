#-*- coding:utf-8 -*-

import cv2
import os
import sys
import time
import random

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# constant
PASSAGE = 0
WALL = 1
EDGES = 2

MAX_HEIGHT = 900

class Widget(QWidget):
    WIDTH = 77 #MAX => 1440
    HEIGHT = 77 #MAX => 900
    BOX_SIZE = 10

    CORRECTION_X = 0
    CORRECTION_Y = 0

    block = []
    row = 0 # HEIGHT
    col = 0 # WIDTH
    rand_direct = ""
    stack = []

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.initialize()
        self.resize(20 + self.BOX_SIZE * self.WIDTH, 20 + self.BOX_SIZE * self.HEIGHT)
        self.setWindowTitle('MazeMaker')

        self.timer = QTimer()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def paintEvent(self, event):
        self.digging()
        painter = QPainter(self)
        for height in range(self.HEIGHT):
            for width in range(self.WIDTH):
                if self.block[height][width] == WALL:
                    painter.setPen(Qt.black)
                    painter.setBrush(Qt.black)
                    painter.drawRect(10 + self.BOX_SIZE * width, 10 + self.BOX_SIZE * height, self.BOX_SIZE, self.BOX_SIZE)
                elif self.block[height][width] == PASSAGE:
                    painter.setPen(Qt.black)
                    painter.setBrush(Qt.white)
                    painter.drawRect(10 + self.BOX_SIZE * width, 10 + self.BOX_SIZE * height, self.BOX_SIZE, self.BOX_SIZE)
                elif self.block[height][width] == EDGES:
                    painter.setPen(Qt.black)
                    painter.setBrush(Qt.gray)
                    painter.drawRect(10 + self.BOX_SIZE * width, 10 + self.BOX_SIZE * height, self.BOX_SIZE, self.BOX_SIZE)

    def stopTimer(self):
        print "Created Maze"
        self.timer.stop()

    def goBack(self):
        try:
            self.row, self.col = self.stack.pop()
        except:
            self.stopTimer()

    def checkWall(self, tmp_row, tmp_col, sec_row, sec_col):
        if (0 < sec_row and sec_row < self.HEIGHT) and (0 < sec_col and sec_col < self.WIDTH):
            if self.block[sec_row][sec_col] != PASSAGE and self.block[sec_row][sec_col] != EDGES:
                self.block[tmp_row][tmp_col] = PASSAGE
                self.block[sec_row][sec_col] = PASSAGE
                self.row = sec_row
                self.col = sec_col
                self.stack.append([self.row, self.col])
            else:
                try:
                    self.digging()
                except:
                    self.goBack()
        else:
            self.goBack()

    def digging(self):
        _row_tmp = self.row
        _col_tmp = self.col
        row_second = self.row
        col_second = self.col
        rand_direct = random.choice(["top", "bottom", "left", "right"])

        if rand_direct == "top" and 0 < self.col:
            col_second -= 2
            _col_tmp -= 1
        elif rand_direct == "bottom" and self.col < self.HEIGHT:
            col_second += 2
            _col_tmp += 1
        elif rand_direct == "left" and 0 < self.row:
            row_second -= 2
            _row_tmp -= 1
        elif rand_direct == "right" and self.row < self.WIDTH:
            row_second += 2
            _row_tmp += 1

        self.checkWall(_row_tmp, _col_tmp, row_second, col_second)

    def CannyEdgeDetection(self):
        gray_img = cv2.imread(sys.argv[1], 0)
        canny_edges = cv2.Canny(gray_img, 100, 200)

        self.HEIGHT, self.WIDTH = canny_edges.shape
        self.BOX_SIZE = (MAX_HEIGHT - 10) / self.HEIGHT

        if self.WIDTH % 2 == 0:
            self.CORRECTION_X += 1
        if self.HEIGHT % 2 == 0:
            self.CORRECTION_Y += 1

        self.WIDTH += self.CORRECTION_X
        self.HEIGHT += self.CORRECTION_Y

        return canny_edges

    def createPitPicture(self, canny_edges):
        origin_width = self.WIDTH - self.CORRECTION_X
        origin_height = self.HEIGHT - self.CORRECTION_Y
        for height in range(0, origin_height):
            for width in range(0, origin_width):
                pixelColor = canny_edges[height, width]
                if pixelColor == 255:
                    self.block[height][width] = EDGES
                    if 0 < height:
                        self.block[height - 1][width] = EDGES
                    if height + 1 < origin_height:
                        self.block[height + 1][width] = EDGES
                    if 0 < width:
                        self.block[height][width - 1] = EDGES
                    if width + 1 < origin_width:
                        self.block[height][width + 1] = EDGES

    def initialize(self):
        canny_edges = self.CannyEdgeDetection()

        for height in range(self.HEIGHT):
            _block_tmp = []
            for width in range(self.WIDTH):
                _block_tmp.append(WALL)
            self.block.append(_block_tmp)

        self.createPitPicture(canny_edges)
        self.randomPosition()
        self.block[self.row][self.col] = PASSAGE
        self.stack.append([self.row, self.col])

    def randomPosition(self):
        rand_width = random.randint(1, self.WIDTH - 1)
        rand_height = random.randint(1, self.HEIGHT - 1)
        if (rand_width % 2 == 0 or rand_height % 2 == 0) and self.block[rand_height][rand_width] != EDGES:
            return self.randomPosition()
        else:
            self.col = rand_width
            self.row = rand_height

def initWidget():
    app = QApplication(sys.argv) # アプリケーション作成
    window = Widget()            # ウィジェットの作成
    window.show()                # ウィジェットの表示
    sys.exit(app.exec_())        # アプリケーション実行

if __name__ == '__main__':
    initWidget()

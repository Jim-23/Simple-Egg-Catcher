# Copyright (C) 2024 [Jesse Sadowý, VNT electronics s.r.o.]

import sys
import random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class EggCatcher(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Egg Catcher Game')
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)
        # set background colour

        self.eggs = []
        self.score = 0
        self.basket_position = 400

        self.main_label = QLabel('Catch 10 eggs to win!', self)
        self.main_label.setGeometry(10, 10, 300, 30)
        self.main_label.setAlignment(Qt.AlignCenter)
        self.main_label.setStyleSheet('font-size: 20px; font-weight: bold; color: white;')
        
        # Label for displaying the score
        self.scoreLabel = QLabel(f'Score: {self.score}', self)
        self.scoreLabel.setGeometry(700, 10, 80, 30)
        self.scoreLabel.setAlignment(Qt.AlignRight)
        self.scoreLabel.setStyleSheet('font-size: 16px; font-weight: bold; color: white;')

        # Label for displaying the winning message
        self.winLabel = QLabel('', self)
        self.winLabel.setGeometry(300, 250, 200, 50)
        self.winLabel.setAlignment(Qt.AlignCenter)
        
        # Timer for eggs dropping
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.dropEggs)
        self.timer.start(1000)  # Drop eggs every second
        
        # Timer for updating the game state
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.updateGame)
        self.update_timer.start(50)

        self.show()

    def dropEggs(self):
        # Create an egg at a random position at the top
        egg_x = random.randint(10, 790)
        egg_color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.eggs.append((egg_x, 0, egg_color))
        
        if len(self.eggs) > 30:  # Limit the number of eggs on screen
            self.eggs.pop(0)
    
    def updateGame(self):
        # Move eggs down
        self.eggs = [(x, y + 20, color) for (x, y, color) in self.eggs if y + 20 < 560]
        self.checkCollision()
        self.update()
        
    def checkCollision(self):
        # Check if any egg is within the basket's range
        basket_x1 = self.basket_position - 50
        basket_x2 = self.basket_position + 50
        before_catch = len(self.eggs)
        self.eggs = [(x, y, color) for (x, y, color) in self.eggs if not (basket_x1 < x < basket_x2 and y >= 540)]
        after_catch = len(self.eggs)
        self.score += (before_catch - after_catch)
        self.scoreLabel.setText(f'Score: {self.score}')
        if self.score >= 10:
            self.winGame()
    
    def winGame(self):
        self.winLabel.setText("You won!")
        self.update_timer.stop()  # Stop updating the game
        QTimer.singleShot(2000, QCoreApplication.instance().quit)  # Close after 2 seconds
    
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

        # Draw the sky
        sky_color = QColor(135, 206, 235)  # Sky Blue
        qp.setBrush(QBrush(sky_color))
        qp.drawRect(0, 0, self.width(), int(self.height() * 0.95))  # Sky covers top 85% of the window

        # Create a wavy grass effect
        grass_color = QColor(0, 128, 0)  # Green
        qp.setBrush(QBrush(grass_color))
        qp.setPen(Qt.NoPen)  # No outline for the grass
        
        path = QPainterPath()
        path.moveTo(0, int(self.height() * 0.85))
        amplitude = 20  # Height of the waves
        wavelength = 100  # How wide each wave is
        # Draw waves using quadratic Bezier curves
        for x in range(0, self.width() + wavelength, wavelength):
            control_x = x + wavelength // 2
            control_y = int(self.height() * 0.85) + (amplitude if (x // wavelength) % 2 == 0 else -amplitude)
            end_x = x + wavelength
            end_y = int(self.height() * 0.85)
            path.quadTo(control_x, control_y, end_x, end_y)

        # Make sure the path goes to the bottom corners of the window to completely fill the area
        path.lineTo(self.width(), self.height())
        path.lineTo(0, self.height())
        path.closeSubpath()  # Close the path to fill completely
        
        qp.drawPath(path)
        
        # Draw eggs and basket on top of the background
        self.drawEggs(qp)
        self.drawBasket(qp)
        
        qp.end()

    def drawEggs(self, qp):
        for x, y, color in self.eggs:
            qp.setBrush(QBrush(color))
            # Set the pen for the outline with a color and thickness
            qp.setPen(QPen(Qt.white, 2))  # Black outline with a thickness of 2 pixels
            qp.drawEllipse(x, y, 20, 30)
    
    def drawBasket(self, qp):
        basket_x = self.basket_position - 50
        basket_y = 560
        basket_width = 100
        basket_height = 40

        # Set color and brush for the basket
        qp.setBrush(QBrush(QColor(139, 69, 19)))  # A brown color for the basket
        qp.setPen(Qt.NoPen)  # No outline

        # Draw the main body of the basket
        qp.drawRoundedRect(basket_x, basket_y, basket_width, basket_height, 10, 10)

        # Add lines to create a woven texture
        qp.setPen(QColor(160, 82, 45))  # Darker shade of brown for the lines
        for i in range(5):  # Horizontal lines
            qp.drawLine(basket_x, basket_y + i * 8, basket_x + basket_width, basket_y + i * 8)
        for i in range(basket_width // 20):  # Vertical lines
            qp.drawLine(basket_x + i * 20, basket_y, basket_x + i * 20, basket_y + basket_height)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Left:
            self.basket_position = max(50, self.basket_position - 20)
        elif e.key() == Qt.Key_Right:
            self.basket_position = min(750, self.basket_position + 20)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EggCatcher()
    sys.exit(app.exec_())

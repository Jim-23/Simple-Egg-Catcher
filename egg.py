# Copyright (C) 2024 [Jesse Sadowý, VNT electronics s.r.o.]

import sys
import json
import random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

COLOR = '#4afd4a'

class EggCatcher(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_high_scores()
        self.left_pressed = False
        self.right_pressed = False
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.moveBasket)
        self.move_timer.start(5)  # Update basket position every 20 ms
        
    def initUI(self):
        self.setWindowTitle('Egg Catcher Game')
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)
        # set background colour

        self.eggs = []
        self.score = 0
        self.missed_eggs = 0
        self.basket_position = 400

        self.main_label = QLabel('Catch 10 eggs to win!', self)
        self.main_label.setGeometry(10, 10, 300, 30)
        self.main_label.setAlignment(Qt.AlignLeft)
        self.main_label.setStyleSheet('font-size: 20px; font-weight: bold; color: #777777;')
        
        # Label for displaying the score
        self.scoreLabel = QLabel(f'Score: {self.score}', self)
        self.scoreLabel.setGeometry(650, 15, 150, 30)
        self.scoreLabel.setAlignment(Qt.AlignLeft)
        self.scoreLabel.setStyleSheet('font-size: 16px; font-weight: bold; color: #00911f;')

        self.missedLabel = QLabel(f'Missed Eggs: {self.missed_eggs}', self)
        self.missedLabel.setGeometry(650, 45, 150, 30)
        self.missedLabel.setAlignment(Qt.AlignLeft)
        self.missedLabel.setStyleSheet('font-size: 16px; font-weight: bold; color: #a04c1b;')

        # Label for displaying the winning message
        self.winLabel = QLabel('', self)
        self.winLabel.setGeometry(300, 250, 200, 50)
        self.winLabel.setAlignment(Qt.AlignCenter)
        self.winLabel.setStyleSheet('font-size: 20px; font-weight: bold; color: white;')

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
        new_eggs = []
        for x, y, color in self.eggs:
            if y + 20 < 560:  # If the egg is still above the basket line
                new_eggs.append((x, y + 20, color))
            else:
                # Check if the egg is at the basket level and not caught
                if not (self.basket_position - 50 < x < self.basket_position + 50 and y >= 540):
                    self.missed_eggs += 1
                    self.missedLabel.setText(f'Missed Eggs: {self.missed_eggs}')  # Update the missed label
                    if self.missed_eggs >= 5:
                        self.gameOver()

        self.eggs = new_eggs
        self.checkCollision()
        self.update()

    def checkCollision(self):
        # Check if any egg is within the basket's range and at the bottom level
        new_eggs = []
        for x, y, color in self.eggs:
            if not (self.basket_position - 50 < x < self.basket_position + 50 and y >= 540):
                new_eggs.append((x, y, color))
            else:
                self.score += 1  # Increment score when an egg is caught
        self.eggs = new_eggs
        self.scoreLabel.setText(f'Score: {self.score}')
        if self.score >= 10:
            self.winGame()

    
    def winGame(self):
        # Check for high score and update if necessary
        if len(self.high_scores) < 5 or self.score > min(self.high_scores):
            self.high_scores.append(self.score)
            self.high_scores = sorted(self.high_scores, reverse=True)[:5]  # Keep top 5 scores
            self.save_high_scores()

        self.winLabel.setText("You won!")
        self.winLabel.setStyleSheet("QLabel { color : #4afd4a; font: 40px; }")
        self.update_timer.stop()  # Stop updating the game
        QTimer.singleShot(2000, QCoreApplication.instance().quit)

    def gameOver(self):
        self.winLabel.setText("Game Over! You missed too many eggs.")
        self.winLabel.setGeometry(200, 250, 400, 50)  # Adjust geometry as needed
        self.winLabel.setStyleSheet("QLabel { color : red; font: 40px; }")
        self.update_timer.stop()  # Stop updating the game
        QTimer.singleShot(2000, QCoreApplication.instance().quit)
    
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
            qp.drawEllipse(x, y, 30, 40)
    
    def drawBasket(self, qp):
        basket_x = self.basket_position - 50
        basket_y = 560
        basket_width = 100
        basket_height = 35

        # Set color and brush for the basket
        qp.setBrush(QBrush(QColor(139, 69, 19)))  # A brown color for the basket
        qp.setPen(Qt.NoPen)  # No outline

        # Draw the main body of the basket
        qp.drawRoundedRect(basket_x, basket_y, basket_width, basket_height, 15, 15)

        # Add lines to create a woven texture
        qp.setPen(QColor(160, 82, 45))  # Darker shade of brown for the lines
        for i in range(5):  # Horizontal lines
            qp.drawLine(basket_x, basket_y + i * 8, basket_x + basket_width, basket_y + i * 8)
        for i in range(basket_width // 20):  # Vertical lines
            qp.drawLine(basket_x + i * 20, basket_y, basket_x + i * 20, basket_y + basket_height)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Left:
            self.left_pressed = True
        elif e.key() == Qt.Key_Right:
            self.right_pressed = True

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_Left:
            self.left_pressed = False
        elif e.key() == Qt.Key_Right:
            self.right_pressed = False

    def moveBasket(self):
        if self.left_pressed:
            self.basket_position = max(50, self.basket_position - 5)
        if self.right_pressed:
            self.basket_position = min(750, self.basket_position + 5)
        self.update()  # Redraw the widget with the updated basket position
    
    def load_high_scores(self, file_name="high_scores.json"):
        try:
            with open(file_name, "r") as file:
                self.high_scores = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.high_scores = []

    def save_high_scores(self, file_name="high_scores.json"):
        with open(file_name, "w") as file:
            json.dump(self.high_scores, file, indent=4)

    def show_high_scores(self):
        high_scores_text = "High Scores:\n" + "\n".join(str(score) for score in self.high_scores)
        self.highScoreLabel = QLabel(high_scores_text, self)
        self.highScoreLabel.setGeometry(550, 100, 200, 200)
        self.highScoreLabel.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EggCatcher()
    sys.exit(app.exec_())

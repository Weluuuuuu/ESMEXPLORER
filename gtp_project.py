from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, Qt, pyqtSignal
import sys
import random
import pickle
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QGridLayout, QAction, QDialog, QLabel, QLineEdit, QMessageBox, QToolBar, QFileDialog
from PyQt5.QtGui import QIcon, QKeySequence

# Création d'un fenêtre pour choisir la difficulté du jeu
class Difficulty(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sélectionnez la difficulté")

        layout = QVBoxLayout()

        label = QLabel("Choisissez votre niveau de difficulté : ")
        layout.addWidget(label)

        facile = QPushButton("Facile")
        facile.clicked.connect(lambda: self.difficulty_validation(8, 10))
        layout.addWidget(facile)

        moyen = QPushButton("Moyen")
        moyen.clicked.connect(lambda: self.difficulty_validation(16, 40))
        layout.addWidget(moyen)

        difficile = QPushButton("Difficile")
        difficile.clicked.connect(lambda: self.difficulty_validation(24, 99))
        layout.addWidget(difficile)

        self.setLayout(layout)

    def difficulty_validation(self, dimension, nb_mines):
        self.dimension = dimension
        self.nb_mines = nb_mines
        self.accept()

# Création d'un classe permettant de s'identifier
class Name(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("S'identifier")
        layout = QVBoxLayout()
        label = QLabel("Entrez votre nom : ")
        
        layout.addWidget(label)
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        # Permet de valider
        submit_button = QPushButton("OK")
        submit_button.clicked.connect(self.accept_name)
        layout.addWidget(submit_button)
        
        self.setLayout(layout)

    def accept_name(self):
        self.name = self.name_input.text()
        self.accept()

# Création d'un classe pour la fenêtre "A propos"
class Information(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("A propos")

        layout = QVBoxLayout()
        text_label = QLabel(
            "1. Règles de base :\n"
            "Au début d'une partie de démineur, vous avez une grille composée de cases vierges.\n"
            "Lorsque vous cliquez sur l'une d'elles, certaines cases sont indiquées comme vides, d'autres restent vierges et d'autres encore affichent des chiffres.\n"
            "Vous devez vous servir de ces chiffres pour déterminer quelles cases vierges contiennent des mines et quelles sont celles que vous pouvez activer sans danger.\n"
            "Le démineur peut être comparé au sudoku dans la mesure où le but est d'essayer d'éliminer un maximum de possibilités jusqu'à ce qu'il n'en reste qu'une seule afin de réussir.\n\n"
            "Utilisez la souris :\n"
            "Vous avez seulement besoin des deux boutons principaux de la souris pour jouer.\n"
            "Le clic gauche sert à sélectionner des cases qui ne contiennent pas de mine.\n"
            "Le clic droit permet de marquer des cases qui pourraient contenir des mines en attendant de savoir si c'est le cas ou non.\n\n"
            "Par Angèle Lecardonnel et Mathys Karim Grisoni"
        )
        layout.addWidget(text_label)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    
    # Envoie d'un signal
    difficulte_choisit = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.dark_mode_enabled = False  # Initialiser la variable pour le mode sombre
        self.setWindowTitle("ESMEXPLORER")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        #Creation de la bar de menu
        self.create_menu_bar()
        
        # On définie la difficulté du jeu
        self.difficulty = Difficulty()
        if not self.difficulty.exec_():
            sys.exit(0)

        # Définition des paramètre du jeu
        self.dimension = self.difficulty.dimension
        self.nb_mines = self.difficulty.nb_mines
        self.cells = self.dimension * self.dimension


        #Chemin des images lié au jeu
        self.Blorks = "C:/Users/Skiiw/Documents/Esme/2ème Année/IHM/Projet/spider24"  # Chemin d'accès à l'icône de Blork
        self.flag_path = "asset/yellow_flag.png"  # Chemin d'accès à l'icône de drapeau
        self.clock_path = "C:/Users/Skiiw/Documents/Esme/2ème Année/IHM/Projet/clock"  # Chemin d'accès à l'icône de la minuterie

        # Charger le son "trumpet.mp3"
        self.trumpet_sound = QMediaPlayer()
        self.trumpet_sound.setMedia(QMediaContent(QUrl.fromLocalFile("trumpet.mp3")))

        # Variable permettant de savoir si le premier clic a été fait
        self.first_click_check = False  
        self.difficulte_choisit.connect(self.show_difficulty)

        # Création de la grille de jeu
        self.create_grid()
        
        # Création de la barre d'outil
        self.create_toolbar()
  
    # Méthode lié au à la création de la grille
    def create_grid(self):
        self.grid_layout = QGridLayout()
        self.buttons = []
        self.mine_counts = [[0] * self.dimension for x in range(self.dimension)]  # Matrice pour stocker le nombre de mines voisines
        self.revealed_count = 0
        for i in range(self.dimension):
            row = []
            for j in range(self.dimension):
                button = QPushButton()
                button.setFixedSize(40, 40)
                button.clicked.connect(lambda x, row=i, col=j: self.First_click(row, col))
                button.setContextMenuPolicy(Qt.CustomContextMenu)
                button.customContextMenuRequested.connect(lambda x, row=i, col=j: self.on_clic_droit(row, col))
                row.append(button)
                self.grid_layout.addWidget(button, i, j)
            self.buttons.append(row)
        self.layout.addLayout(self.grid_layout)

    # Méthode lié à la création de la barre d'outil
    def create_toolbar(self):
        if hasattr(self, 'toolbar'):
            self.removeToolBar(self.toolbar)
        self.toolbar = QToolBar("Toolbar")
        self.addToolBar(self.toolbar)

        blorks_label = QLabel()
        blorks_label.setPixmap(QIcon(self.Blorks).pixmap(16, 16))
        self.blorks_count = QLabel(str(self.nb_mines))
        self.toolbar.addWidget(blorks_label)
        self.toolbar.addWidget(self.blorks_count)

        self.toolbar.addSeparator()

        self.name_label = QLabel(" ")
        self.toolbar.addWidget(self.name_label)
    

    # Méthode liée à la génération des mines
    def generate_mines(self, initial_row, initial_col):
        self.mines = set()
        while len(self.mines) < self.nb_mines:
            row = random.randint(0, self.dimension - 1)
            col = random.randint(0, self.dimension - 1)
            if (row, col) != (initial_row, initial_col) and (row, col) not in self.mines and not (abs(row - initial_row) <= 1 and abs(col - initial_col) <= 1):
                self.mines.add((row, col))

    # Nombre de mine restante
    def nb_mine_counts(self):
        for i in range(self.dimension):
            for j in range(self.dimension):
                if (i, j) not in self.mines:
                    count = sum(1 for dx in [-1, 0, 1] for dy in [-1, 0, 1] if (i+dx, j+dy) in self.mines)
                    self.mine_counts[i][j] = count

    # Permet de faire en sorte que les mines soient générées après le premier clic
    def First_click(self, row, col):
        if not self.first_click_check:
            self.generate_mines(row, col)
            self.nb_mine_counts()
            self.first_click_check = True

        # Actions à réaliser si une bombe est cliqué
        if (row, col) in self.mines:
            self.buttons[row][col].setIcon(QIcon(self.Blorks))
            self.buttons[row][col].setIconSize(self.buttons[row][col].size())
            self.buttons[row][col].setEnabled(False)
            self.trumpet_sound.play()  # Joue le son si une bombe est cliquée
            self.reveal_all_mines()
            QMessageBox.critical(self, "ESMEXPLORER", "Bleuuurks!!! Vous avez touché un Blorks. Game Over!!!")
            self.difficulte_choisit.emit()
        else:
            self.reveal_cell(row, col)
            if self.revealed_count == self.cells - self.nb_mines:
                QMessageBox.information(self, "ESMEXPLORER", "Félicitations !!! Vous avez terminé le niveau !!!")
                self.difficulte_choisit.emit()

    # Clic droit permettant de poser un drapeau
    def on_clic_droit(self, row, col):
        button = self.buttons[row][col]
        if button.isEnabled() and not button.icon():
            button.setIcon(QIcon(self.flag_path))
            button.setIconSize(button.size())
        elif button.icon():
            button.setIcon(QIcon())

    # Affichage de la grille contenant les mines
    def reveal_all_mines(self):
        for row, col in self.mines:
            self.buttons[row][col].setIcon(QIcon(self.Blorks))
            self.buttons[row][col].setIconSize(self.buttons[row][col].size())
            self.buttons[row][col].setEnabled(False)

    # Révélation des cellules vides adjacentes
    def reveal_cell(self, row, col):
        if not self.buttons[row][col].isEnabled() or (row, col) in self.mines:
            return
        self.buttons[row][col].setEnabled(False)
        self.revealed_count += 1
        if self.mine_counts[row][col] > 0:
            self.buttons[row][col].setText(str(self.mine_counts[row][col]))
        else:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    new_row, new_col = row + dx, col + dy
                    if 0 <= new_row < self.dimension and 0 <= new_col < self.dimension:
                        self.reveal_cell(new_row, new_col)

    # Création de la bar de menu
    def create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("Fichier")

        save_action = QAction("Sauvegarder", self)
        save_action.triggered.connect(self.save_game)
        file_menu.addAction(save_action)

        load_action = QAction("Charger", self)
        load_action.triggered.connect(self.load_game)
        file_menu.addAction(load_action)

        exit_action = QAction("Quitter", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("Aide")

        about_action = QAction("A propos", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
        # Ajouter un bouton pour le mode sombre
        dark_mode_action = QAction("Toggle Dark Mode", self)
        dark_mode_action.triggered.connect(self.toggle_dark_mode)
        help_menu.addAction(dark_mode_action)
        
        # Nouveau
        menu_Nouveau = QAction(QIcon('C:/Users/Skiiw/Documents/Esme/2ème Année/IHM/Projet/reset.png'), "Nouveau", self)
        menu_Nouveau.triggered.connect(self.reset_game)
        menu_Nouveau.setShortcut(QKeySequence("Ctrl+N"))
        file_menu.addAction(menu_Nouveau)
        
        
        # Méthode lié à la réinisialisation du jeu
    def reset_game(self):
        self.first_click_check = False
        self.revealed_count = 0
        self.blorks_count.setText(str(self.nb_blorks))
        
            
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
            self.create_grid()
            self.create_toolbar()

    # Permet de sauvegarder la partie
    def save_game(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Game", "", "Pickle Files (*.pkl)")
        if file_path:
            with open(file_path, 'wb') as file:
                pickle.dump((self.mine_counts, self.mines, self.first_click_check, self.revealed_count), file)
            QMessageBox.information(self, "Sauvegarde", "La partie a été sauvegardée avec succès.")

    # Permet de charger une partie
    def load_game(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Game", "", "Pickle Files (*.pkl)")
        if file_path:
            with open(file_path, 'rb') as file:
                self.mine_counts, self.mines, self.first_click_check, self.revealed_count = pickle.load(file)
            self.update_grid_from_loaded_game()
            QMessageBox.information(self, "Chargement", "La partie a été chargée avec succès.")

    # Mettre à jour la grille après chargement
    def update_grid_from_loaded_game(self):
        for i in range(self.dimension):
            for j in range(self.dimension):
                button = self.buttons[i][j]
                button.setEnabled(True)
                button.setText("")
                button.setIcon(QIcon())
                if not button.isEnabled():
                    self.reveal_cell(i, j)

    # Affichage de la fenêtre "A propos"
    def show_about_dialog(self):
        dialog = Information(self)
        dialog.exec_()
    
    # Permet d'afficher le niveau de difficulté choisit
    def show_difficulty(self):
        self.reset_grid()
        self.difficulty = Difficulty()
        if self.difficulty.exec_():
            self.dimension = self.difficulty.dimension
            self.nb_mines = self.difficulty.nb_mines
            self.cells = self.dimension * self.dimension
            self.create_grid()
            self.create_toolbar()
            self.first_click_check = False
            self.adjustSize()  # Redimensionne la fenêtre à sa taille minimale
        # Ajuste la taille de la fenêtre pour correspondre à la taille minimale requise par les nouveaux widgets
        self.setFixedSize(self.minimumSizeHint())

    # Permet de remettre à 0 la grille
    def reset_grid(self):
        for i in range(self.grid_layout.count()):
            item = self.grid_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

    # Méthode pour basculer le mode sombre
    def toggle_dark_mode(self):
        self.dark_mode_enabled = not self.dark_mode_enabled
        self.update_stylesheet()

    # Mettre à jour le style des widgets
    def update_stylesheet(self):
        if self.dark_mode_enabled:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2E2E2E;
                }
                QPushButton {
                    background-color: #5A5A5A;
                    color: #FFFFFF;
                    border: 1px solid #1E1E1E;
                    font-size: 16px;
                }
                QLabel {
                    color: #FFFFFF;
                }
                QMenuBar {
                    background-color: #2E2E2E;
                    color: #FFFFFF;
                }
                QMenu {
                    background-color: #2E2E2E;
                    color: #FFFFFF;
                }
                QToolBar {
                    background-color: #2E2E2E;
                }
                QMessageBox {
                    background-color: #2E2E2E;
                    color: #FFFFFF;
                }
            """)
        else:
            self.setStyleSheet("")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

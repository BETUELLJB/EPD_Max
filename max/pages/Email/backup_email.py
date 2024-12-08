import os
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PySide6.QtGui import QIcon, QCursor
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEvent
from datetime import datetime

from pages.Email.recebido import EmailRecebido
from pages.Email.enviado import EmailEnviado
from pages.Email.rascunho import EmailRascunho
from pages.Email.lixeira import Lixeira
from pages.Email.configuracao import Configuracao


# Caminho base do gestor de emails e diretório de logs
BASE_DIR = "B:\\Estudos\\Projetos\\Python\\Max\\max\\pages\\Email\\Gestor_Email"
LOG_DIR = "B:\\Estudos\\Projetos\\Python\\Max\\max\\pages\\Email\\Gestor_Email\\Logs"
PASTAS = {
    "enviados": "enviados",
    "recebidos": "recebidos",
    "rascunhos": "rascunhos",
    "lixeira": "lixeira"
}

# Função para inicializar o sistema de logs
def inicializar_logs():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)  # Cria o diretório de logs se não existir

    log_file = os.path.join(LOG_DIR, "logs_email.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s - [%(pathname)s:%(lineno)d]",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

# Inicializa o sistema de logs no início
inicializar_logs()

def inicializar_pastas():
    """Cria a estrutura de pastas se não existir."""
    try:
        if not os.path.exists(BASE_DIR):
            os.makedirs(BASE_DIR)  # Cria a pasta principal

        for pasta in PASTAS.values():
            caminho = os.path.join(BASE_DIR, pasta)
            os.makedirs(caminho, exist_ok=True)  # Cria cada subpasta
    except Exception as e:
        logging.error(f"Erro ao inicializar as pastas: {e}")

# Inicializar as pastas no início
inicializar_pastas()

class EmailDashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        # Inicializa as pastas ao iniciar o dashboard
        inicializar_pastas()

        # Definindo o layout principal (vertical)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove as margens do layout
        main_layout.setSpacing(0)  # Remove o espaçamento entre os widgets

        # Adicionando a navbar
        self.navbar = QWidget()
        self.navbar_layout = QHBoxLayout()
        self.navbar.setLayout(self.navbar_layout)
        self.navbar.setFixedHeight(40)  # Altura fixa da navbar
        self.navbar.setStyleSheet("background-color: rgba(0, 21, 42, 180);")  # Cor de fundo igual ao sidebar
        main_layout.addWidget(self.navbar)

        # Adicionando botão "Compor" à navbar
        self.botao_compor = QPushButton("Compor")
        self.botao_compor.setIcon(QIcon("max/assets/icon/compor.png"))  # Defina o ícone que deseja usar
        self.botao_compor.setIconSize(QSize(24, 24))  # Tamanho do ícone
        self.botao_compor.setStyleSheet(
            "background: #2496be; "
            "border: none; "
            "color: white; "
            "font-size: 14px; "
            "padding: 3px 15px; "
            "border-radius: 5px;"
        )
        self.botao_compor.setFocusPolicy(Qt.NoFocus)
        self.navbar_layout.addWidget(self.botao_compor, alignment=Qt.AlignLeft)

        # Definindo o layout horizontal para a sidebar e parte central
        central_layout = QHBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)  # Remove as margens do layout central
        central_layout.setSpacing(0)  # Remove espaçamento no layout central

        # Adicionando a sidebar
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)
        self.sidebar.setFixedWidth(50)  # Sidebar oculta inicialmente
        self.sidebar.setStyleSheet("background-color: rgba(0, 21, 42, 180); margin: 0; padding: 0;")
        central_layout.addWidget(self.sidebar)

        # Adicionando a parte central
        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout()
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        self.central_widget.setLayout(self.central_layout)
        central_layout.addWidget(self.central_widget)

        # Adicionando botões à sidebar
        self.botoes = self.criar_botoes_sidebar()

        # Exibe a página de "Emails Recebidos" por padrão
        self.exibir_conteudo(EmailRecebido)

        # Conectar eventos de mouse para a sidebar
        self.sidebar.installEventFilter(self)

        # Adicionar o layout central ao layout principal
        main_layout.addLayout(central_layout)

        # Configurando o widget central
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def criar_botoes_sidebar(self):
        """Cria os botões da sidebar com ícones."""    
        botoes_info = [
            ("Recebidos", "max/assets/icon/circular.png", EmailRecebido),
            ("Enviados", "max/assets/icon/circular.png", EmailEnviado),
            ("Rascunhos", "max/assets/icon/circular.png", EmailRascunho),
            ("Lixeira", "max/assets/icon/circular.png", Lixeira),
            ("Configurações", "max/assets/icon/circular.png", Configuracao)
        ]

        for nome, icone, janela_class in botoes_info:
            botao = QPushButton(nome)
            botao.setIcon(QIcon(icone))  # Define o ícone do botão
            botao.setIconSize(QSize(24, 24))  # Corrigido para usar QSize corretamente
            botao.setStyleSheet(
                "background: none; "
                "border: none; "
                "color: #2496be; "
                "font-size: 16px; "
                "padding: 5px; "
                "text-align: left;"
            )
            botao.setFocusPolicy(Qt.NoFocus)
            botao.clicked.connect(lambda checked, janela=janela_class: self.exibir_conteudo(janela))
            self.sidebar_layout.addWidget(botao)

        # Espaço entre os botões e a parte central
        self.sidebar_layout.addStretch()

    def exibir_conteudo(self, janela_class):
        """Exibe o conteúdo de uma nova janela na parte central."""
        nova_janela = janela_class()  # Instancia a nova janela
        # Limpa o layout central
        for i in reversed(range(self.central_layout.count())):
            widget = self.central_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()  # Remove o widget existente
        # Adiciona a nova janela ao layout central
        self.central_layout.addWidget(nova_janela)

    def eventFilter(self, source, event):
        """Filtro de evento para controlar a exibição da sidebar."""
        try:
            if source == self.sidebar:
                if event.type() == QEvent.Enter:
                    # Quando o mouse entra na sidebar, exibe a sidebar
                    self.mostrar_sidebar()
                    return True
                elif event.type() == QEvent.Leave:
                    # Verifique se o mouse ainda está dentro da sidebar
                    mouse_pos = self.mapFromGlobal(QCursor.pos())  # Pega a posição do cursor no espaço da janela
                    if not self.sidebar.rect().contains(mouse_pos):  # Se o mouse está fora da sidebar
                        self.ocultar_sidebar()
                    return True
            return super().eventFilter(source, event)
        except Exception as e:
            logging.error(f"Erro no eventFilter: {e}")
            return False


    def mostrar_sidebar(self):
        """Exibe a sidebar com animação."""
        animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        animation.setDuration(300)  # Duração da animação em milissegundos
        animation.setStartValue(self.sidebar.width())  # Largura inicial
        animation.setEndValue(200)  # Largura final
        self.sidebar.setFixedWidth(170)
        animation.start()

    def ocultar_sidebar(self):
        """Oculta a sidebar com animação."""
        animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        animation.setDuration(300)  # Duração da animação em milissegundos
        animation.setStartValue(self.sidebar.width())  # Largura inicial
        animation.setEndValue(50)  # Largura final (apenas ícones visíveis)
        animation.start()
        self.sidebar.setFixedWidth(50)  # Defina a largura fixa após iniciar a animação

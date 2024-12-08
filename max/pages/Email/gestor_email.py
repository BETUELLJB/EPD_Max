
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PySide6.QtGui import QIcon, QCursor
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEvent
from email.mime.multipart import MIMEMultipart
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton, QLabel, QFileDialog, QMessageBox

from config.config import pastas_email, BASE_DIR_Email, LOG_DIR_Email
from pages.Email.recebido import EmailRecebido
from pages.Email.enviado import EmailEnviado
from pages.Email.rascunho import EmailRascunho
from pages.Email.lixeira import Lixeira
from pages.Email.configuracao import Configuracao
from pages.Email.email_enviar import EmailCompor
from email.mime.text import MIMEText
from datetime import datetime
import traceback
import smtplib
import json
import os



class EmailDashboard(QMainWindow):
    def __init__(self, LOG_DIR_Email= LOG_DIR_Email, BASE_DIR_Email= BASE_DIR_Email ):
        super().__init__()
        if not os.path.exists(LOG_DIR_Email ):
            os.makedirs(LOG_DIR_Email )
        self.log_file = os.path.join(LOG_DIR_Email, "Logs_Email.log")

        # Inicializa as pastas ao iniciar o dashboard
        pastas_email(self)
        
        self.email_recebido_widget = EmailRecebido()  # Inicializa antes de email_exibir_conteudo ser chamado
        # Variáveis para cada janela interna
        self.janela_recebidos = None
        self.janela_enviados = None
        self.janela_rascunho = None
        self.janela_lixeira = None
        self.janela_configuracao = None

        # Definindo o layout principal (vertical)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove as margens do layout
        main_layout.setSpacing(0)  # Remove o espaçamento entre os widgets

        # Adicionando a navbar
        self.navbar = QWidget()
        self.navbar_layout = QHBoxLayout()
        self.navbar.setLayout(self.navbar_layout)
        self.navbar.setFixedHeight(46)  # Altura fixa da navbar
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
        self.botao_compor.clicked.connect(self.abrir_compor_email)
       
        # Adicionando botão "Compor" à navbar
        self.botao_recarregar = QPushButton("recarregar")
        self.botao_recarregar.setIcon(QIcon("max/assets/icon/recarregar.png"))  # Defina o ícone que deseja usar
        self.botao_recarregar.setIconSize(QSize(24, 24))  # Tamanho do ícone
        self.botao_recarregar.setStyleSheet(
            "background: #2496be; "
            "border: none; "
            "color: white; "
            "font-size: 14px; "
            "padding: 3px 15px; "
            "border-radius: 5px;"
        )
        self.botao_recarregar.setFocusPolicy(Qt.NoFocus)
        self.navbar_layout.addWidget(self.botao_recarregar, alignment=Qt.AlignLeft)
        # Conectando o clique do botão à função de atualização dos e-mails
        self.botao_recarregar.clicked.connect(self.abrir_recarregar_email)
        

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
        self.email_exibir_conteudo(EmailRecebido)

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
            botao.clicked.connect(lambda checked, janela=janela_class: self.email_exibir_conteudo(janela))
            self.sidebar_layout.addWidget(botao)

        # Espaço entre os botões e a parte central
        self.sidebar_layout.addStretch()

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
            self.log_erro(f"Erro no eventFilter: {e}")
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

    def abrir_recarregar_email(self):
        # EmailRecebido.sincronizar_emails(self)  
        self.email_recebido_widget.atualizar_emails()
    
    def notificar_sucesso(self, mensagem):
        QMessageBox.information(self, "Sucesso", mensagem)

    def notificar_erro(self, mensagem):
        QMessageBox.critical(self, "Erro", mensagem)
        
    def abrir_compor_email(self):
        modal = EmailCompor(BASE_DIR_Email)
        modal.exec()
        
    def email_exibir_conteudo(self, janela_class):
        """Exibe o conteúdo de uma nova janela na parte central."""
        # Instancia a janela e atribui à variável correspondente
        if janela_class == EmailRecebido:
            self.janela_recebidos = janela_class()
            nova_janela = self.janela_recebidos
        elif janela_class == EmailEnviado:
            self.janela_enviados = janela_class()
            nova_janela = self.janela_enviados
        elif janela_class == EmailRascunho:
            self.janela_rascunho = janela_class()
            nova_janela = self.janela_rascunho
        elif janela_class == Lixeira:
            self.janela_lixeira = janela_class()
            nova_janela = self.janela_lixeira
        elif janela_class == Configuracao:
            self.janela_configuracao = janela_class()
            nova_janela = self.janela_configuracao
        else:
            nova_janela = janela_class()

        # Limpa o layout central antes de adicionar nova janela
        for i in reversed(range(self.central_layout.count())):
            widget = self.central_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        self.central_layout.addWidget(nova_janela)

    def fechar_janela_interna(self, nome_janela):
        """Fecha uma janela interna específica por nome."""
        try:
            if nome_janela == "recebidos" and self.janela_recebidos:
                self.janela_recebidos.close()
                self.janela_recebidos = None
            elif nome_janela == "enviados" and self.janela_enviados:
                self.janela_enviados.close()
                self.janela_enviados = None
            elif nome_janela == "rascunho" and self.janela_rascunho:
                self.janela_rascunho.close()
                self.janela_rascunho = None
            elif nome_janela == "lixeira" and self.janela_lixeira:
                self.janela_lixeira.close()
                self.janela_lixeira = None
            elif nome_janela == "configuracao" and self.janela_configuracao:
                self.janela_configuracao.close()
                self.janela_configuracao = None
            else:
                mensagem = (f"Janela '{nome_janela}' não encontrada ou já está fechada.")
                self.notificar_erro(mensagem)
        except Exception as e:
            self.log_erro(f"Erro ao fechar a janela '{nome_janela}': {e}")
    
    def log_erro(self, mensagem):
        """Registra mensagens de erro no arquivo de log com traceback completo."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - ERROR - {mensagem}\n")
                # Adiciona o traceback completo se houver uma exceção ativa
                log_file.write(traceback.format_exc() + "\n")
        except Exception as e:
            print(f"Erro ao registrar log: {e}")  
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QCheckBox
from PySide6.QtGui import QPalette, QBrush, QPixmap, QIcon, QColor, QPainter, QCursor
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEvent,QTimer, QObject, QThread, Signal
from pages.Tasks.gestor_tarefa import CalendarioDashboard
from pages.Email.gestor_email import EmailDashboard
from pages.configuracao import Configuracao
from config.config import BASE_DIR_Log_Main, BASE_DIR_Config
from pages.comando import Comando
from pages.home import Home
from pages.login import Login
from max1 import Sylla
from pages.chat import Chat
from datetime import datetime
import subprocess
import pyautogui
import traceback
import psutil
import webbrowser
import os
import socket
import smtplib
import json

from threading import Timer

import random

from email.mime.text import MIMEText
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bcrypt import hashpw, gensalt
from bcrypt import checkpw
from dotenv import load_dotenv
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.fernet import Fernet
from dotenv import load_dotenv, set_key
import base64
import sys
import platform
import uuid
import socket
from getmac import get_mac_address
from dotenv import set_key

import json
import os
from datetime import datetime
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class CadastroDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastro")
        self.setGeometry(300, 200, 300, 250)

        # Layout
        layout = QVBoxLayout()
        self.label_nome = QLabel("Nome:")
        self.input_nome = QLineEdit()
        self.label_senha = QLabel("Senha:")
        self.input_senha = QLineEdit()
        self.input_senha.setEchoMode(QLineEdit.Password)
        
        # Checkbox para ativação do 2FA
        self.checkbox_2fa = QCheckBox("Ativar verificação de dois fatores (2FA)")

        self.botao_cadastrar = QPushButton("Cadastrar")
        self.botao_cadastrar.clicked.connect(self.cadastrar)

        # Adiciona widgets ao layout
        layout.addWidget(self.label_nome)
        layout.addWidget(self.input_nome)
        layout.addWidget(self.label_senha)
        layout.addWidget(self.input_senha)
        layout.addWidget(self.checkbox_2fa)
        layout.addWidget(self.botao_cadastrar)
        self.setLayout(layout)

    def cadastrar(self):
        nome = self.input_nome.text().strip()
        senha = self.input_senha.text().strip()
        ativar_2fa = self.checkbox_2fa.isChecked()

        if not nome or not senha:
            QMessageBox.warning(self, "Erro", "Todos os campos são obrigatórios.")
            return

        if len(senha) < 6:
            QMessageBox.warning(self, "Erro", "A senha deve ter pelo menos 6 caracteres.")
            return

        # Gerar o hash da senha
        hash_senha = hashpw(senha.encode('utf-8'), gensalt()).decode('utf-8')

        # Aceder e atualizar a configuração
        config = self.parent().carregar_config_login()
        if "login" not in config:
            config["login"] = {}  # Garante que a chave exista

        # Atualiza os dados do utilizador com o nome e senha codificados
        config["login"]["usuario"] = {
            "nome": self.parent().codificar_campo(nome),
            "senha": self.parent().codificar_campo(hash_senha),
            "email": None,  # Placeholder, pode ser preenchido posteriormente
        }

        # Atualiza a configuração de segurança
        if "seguranca" not in config:
            config["seguranca"] = {}  # Garante que a chave exista

        config["seguranca"]["dois_fatores_ativo"] = self.parent().codificar_campo(str(ativar_2fa))

        # Salva as configurações atualizadas
        self.parent().salvar_config_login(config)

        QMessageBox.information(self, "Sucesso", "Cadastro realizado com sucesso!")
        self.accept()  # Fecha o modal
   

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setGeometry(300, 200, 300, 200)

        # Layout
        layout = QVBoxLayout()
        self.label_nome = QLabel("Nome:")
        self.input_nome = QLineEdit()
        self.label_senha = QLabel("Senha:")
        self.input_senha = QLineEdit()
        self.input_senha.setEchoMode(QLineEdit.Password)
        self.botao_login = QPushButton("Login")
        self.botao_login.clicked.connect(self.logar)

        # Adiciona widgets ao layout
        layout.addWidget(self.label_nome)
        layout.addWidget(self.input_nome)
        layout.addWidget(self.label_senha)
        layout.addWidget(self.input_senha)
        layout.addWidget(self.botao_login)
        self.setLayout(layout)

    def logar(self):
        """Realiza o login do utilizador verificando as credenciais."""
        nome = self.input_nome.text().strip()
        senha = self.input_senha.text().strip()

        # Aceder à configuração
        config = self.parent().carregar_config_login()
        login_config = config.get("login", {})
        usuario = login_config.get("usuario")

        if not usuario:
            QMessageBox.warning(self, "Erro", "Nenhum utilizador cadastrado. Por favor, realize o cadastro primeiro.")
            return

        try:
            # Descriptografar os dados codificados
            fernet = Fernet(self.parent().config_key.encode())
            nome_decodificado = fernet.decrypt(usuario.get("nome").encode()).decode()
            senha_codificada = usuario.get("senha")
            senha_descriptografada = fernet.decrypt(senha_codificada.encode()).decode()
            
            # Verificar o estado de autenticação em dois fatores
            dois_fatores_codificado = config.get("seguranca", {}).get("dois_fatores_ativo", False)
            dois_fatores_ativo = fernet.decrypt(str(dois_fatores_codificado).encode()).decode() == "True"

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar os dados codificados: {e}")
            return

        # Verificar o nome de utilizador
        if nome_decodificado == nome:
            # Comparar a senha inserida com o hash armazenado
            if checkpw(senha.encode('utf-8'), senha_descriptografada.encode('utf-8')):
                if dois_fatores_ativo:
                    # Executar o fluxo de verificação de 2FA
                    verificacao_2fa = Verificacao2FADialog(self)
                    verificacao_2fa.iniciar_verificacao(email=usuario["email"])  # E-mail cadastrado do utilizador

                    if verificacao_2fa.exec() == QDialog.Accepted:
                        login_config["ultimo_acesso"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        config["login"] = login_config  # Atualiza a chave login
                        self.parent().salvar_config_login(config)
                        QMessageBox.information(self, "Sucesso", "Login realizado com sucesso!")
                        self.accept()  # Fecha o modal
                    else:
                        QMessageBox.warning(self, "Erro", "Autenticação de dois fatores falhou.")
                else:
                    # Login direto se 2FA estiver desativado
                    login_config["ultimo_acesso"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    config["login"] = login_config  # Atualiza a chave login
                    self.parent().salvar_config_login(config)
                    QMessageBox.information(self, "Sucesso", "Login realizado com sucesso!")
                    self.accept()  # Fecha o modal
            else:
                QMessageBox.warning(self, "Erro", "Senha incorreta.")
        else:
            QMessageBox.warning(self, "Erro", "Utilizador não encontrado.")


class Verificacao2FADialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Verificação de Dois Fatores")
        self.setGeometry(300, 200, 300, 150)
        
        # Carregar o arquivo de configuração com o caminho especificado
        load_dotenv("B:\\Estudos\\Projetos\\Python\\Max\\max\\config\\config.env")
        # Layout
        layout = QVBoxLayout()
        self.label_codigo = QLabel("Código de Verificação:")
        self.input_codigo = QLineEdit()
        self.input_codigo.setMaxLength(6)
        self.input_codigo.setPlaceholderText("Insira o código de 6 dígitos")
        self.botao_verificar = QPushButton("Verificar")
        self.botao_verificar.clicked.connect(self.verificar_codigo)

        # Adiciona widgets ao layout
        layout.addWidget(self.label_codigo)
        layout.addWidget(self.input_codigo)
        layout.addWidget(self.botao_verificar)
        self.setLayout(layout)

        # Código de verificação gerado
        self.codigo_gerado = None

    def iniciar_verificacao(self, email):
        """Gera e envia o código de verificação."""
        self.codigo_gerado = self.gerar_codigo_verificacao()
        if self.enviar_email(email, self.codigo_gerado):
            QMessageBox.information(self, "Código Enviado", f"Um código foi enviado para {email}.")
        else:
            QMessageBox.critical(self, "Erro", "Falha ao enviar o código. Tente novamente.")
            self.reject()

    def verificar_codigo(self):
        """Valida o código inserido pelo utilizador."""
        codigo_inserido = self.input_codigo.text().strip()
        if codigo_inserido == self.codigo_gerado:
            QMessageBox.information(self, "Sucesso", "Código verificado com sucesso!")
            self.accept()  # Fecha o modal e continua
        else:
            QMessageBox.warning(self, "Erro", "Código incorreto. Tente novamente.")
            
    def gerar_codigo_verificacao(self):
        """Gera um código de 6 dígitos para verificação."""
        return str(random.randint(100000, 999999))

    logging = logging.basicConfig(filename="2fa.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    def enviar_email(self, destinatario, codigo):
        """
        Envia o código de verificação ao utilizador por e-mail usando uma chave de aplicação segura.
        """
        remetente = os.getenv("EMAIL_REMETENTE")
        chave_aplicacao = os.getenv("EMAIL_CHAVE")
        smtp_server = os.getenv("SMTP_SERVIDOR")
        smtp_port = int(os.getenv("SMTP_PORTA"))
        assunto = "Código de Verificação - Assistente Virtual"
        corpo = f"O seu código de verificação é: {codigo}"

        try:
            if not all([os.getenv("EMAIL_REMETENTE"), os.getenv("EMAIL_CHAVE"), os.getenv("SMTP_SERVIDOR"), os.getenv("SMTP_PORTA")]):
                QMessageBox.critical(self, "Erro", "Configuração de e-mail incompleta.")
                return False
            
            # Configurações do e-mail
            msg = MIMEMultipart()
            msg['From'] = remetente
            msg['To'] = destinatario
            msg['Subject'] = assunto
            msg.attach(MIMEText(corpo, 'plain'))

            # Conexão com o servidor SMTP
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Inicia a criptografia TLS
                server.login(remetente, chave_aplicacao)  # Faz login com a chave de aplicação
                server.send_message(msg)

            print("E-mail enviado com sucesso.")
            logging.info(f"E-mail enviado para {destinatario}.")
            return True

        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")
            logging.error(f"Erro ao enviar e-mail para {destinatario}: {e}")
            return False


class MainWindow(QMainWindow):
    def __init__(self, BASE_DIR_Log_Main=BASE_DIR_Log_Main, BASE_DIR_Config=BASE_DIR_Config ):
        
        super().__init__()
        self.class_home = Home()
        self.salt = b"sal_secreto"  # Guarde este valor fixo e seguro
        # Caminho do .env
        self.dotenv_path = "B:\\Estudos\\Projetos\\Python\\Max\\max\\config\\config.env"
        self.config_key = self.obter_ou_gerar_chave()  # Carregar chave automaticamente

        # Carrega o arquivo .env
        load_dotenv(self.dotenv_path)
        
        if not os.path.exists(BASE_DIR_Log_Main ):
            os.makedirs(BASE_DIR_Log_Main )
        self.log_file = os.path.join(BASE_DIR_Log_Main, "Logs_Main.log")
        
        if not os.path.exists(BASE_DIR_Config):
            os.makedirs(BASE_DIR_Config)
        
        self.caminho_comandos_json = os.path.join(BASE_DIR_Config, "comandos.json")
        self.caminho_comandos_json = os.path.join(BASE_DIR_Config, "clima.json")
        
        # criar arquivo config_login
        self.config_login = os.path.join(BASE_DIR_Config, "config_login.json")
       
        
        self.verificar_ou_criar_arquivo_login()
        
        # Verificar login antes de carregar a interface principal
        if not self.verificar_login():
            QMessageBox.warning(self, "Encerrado", "Login ou cadastro necessário para continuar.")
            return  # Evita continuar a inicialização sem login
        
       
        self.setWindowTitle("Assistente Virtual")
        self.setGeometry(190, 40, 1000, 600)

        # Definindo o ícone da aplicação
        self.setWindowIcon(QIcon("max/assets/icon/circular.png"))

  
        # Inicializar a thread de reconhecimento de fala
        self.thread_reconhecimento = QThread()
        self.reconhecimento_fala = Sylla()
        self.reconhecimento_fala.moveToThread(self.thread_reconhecimento)
        self.modo_pesquisa = None  # Variável para armazenar o tipo de pesquisa selecionado

        # Conectar sinais e slots
        self.thread_reconhecimento.started.connect(self.reconhecimento_fala.iniciar_reconhecimento)
        self.reconhecimento_fala.fala_detectada.connect(self.processar_fala)

        # Iniciar a thread de reconhecimento de fala
        self.thread_reconhecimento.start() 
        self.enviar_boas_vindas()
        
        # Verificar e criar o arquivo se necessário
        self.verificar_ou_criar_arquivo_comandos()

        # Carregar comandos do arquivo JSON
        self.comandos_variacoes = self.carregar_comandos()

        # Definindo o layout principal (horizontal)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Adicionando a parte central
        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_layout)
        main_layout.addWidget(self.central_widget)

        self.exibir_conteudo(Home)

        # Adicionando a sidebar
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)
        self.sidebar.setFixedWidth(50)  # Oculta a sidebar inicialmente (mostrando apenas os ícones)
        self.sidebar.setAutoFillBackground(True)
        self.sidebar.setStyleSheet("background-color: rgba(0, 21, 42, 180); margin: 0; padding: 0;")
        main_layout.addWidget(self.sidebar)

        # Adicionando botões à sidebar
        self.botoes = self.criar_botoes_sidebar()

        # Conectar eventos de mouse para a sidebar
        self.sidebar.installEventFilter(self)  # Adiciona um filtro de evento para a sidebar

        # Configurando o widget central
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Definindo o fundo da janela
        self.definir_fundo()
        
 #/*********************** Login  *************************
    
    
    def obter_ou_gerar_chave(self):
        chave = os.getenv("CONFIG_KEY")
        if not chave:
            # Gerar uma nova chave
            chave = Fernet.generate_key().decode()
            # Salvar no .env
            set_key(self.dotenv_path, "CONFIG_KEY", chave)
        return chave

    def codificar_campo(self, valor):
        """Codifica um valor sensível."""
        fernet = Fernet(self.config_key.encode())
        return fernet.encrypt(valor.encode('utf-8')).decode('utf-8')

    def decodificar_campo(self, valor):
        """Decodifica um valor sensível."""
        fernet = Fernet(self.config_key.encode())
        return fernet.decrypt(valor.encode('utf-8')).decode('utf-8')

    def salvar_config_login(self, config):
        """Salva a configuração de login, criptografando apenas os dados sensíveis."""
        fernet = Fernet(self.config_key.encode())

        # Criptografar apenas os campos sensíveis
        if "login" in config and "usuario" in config["login"] and config["login"]["usuario"]:
            usuario = config["login"]["usuario"]
            if "senha" in usuario and usuario["senha"]:  # Verifica se a senha existe
                usuario["senha"] = fernet.encrypt(
                    str(usuario["senha"]).encode()
                ).decode()  # Transformar para string criptografada

        # Salvar como JSON normalmente
        with open(self.config_login, "w") as file:
          json.dump(config, file, indent=4)

    def carregar_config_login(self):
        """Carrega a configuração de login, descriptografando os dados sensíveis."""
        if not os.path.exists(self.config_login):
            raise FileNotFoundError("Arquivo de configuração não encontrado. Verifique ou crie um novo arquivo.")

        with open(self.config_login, "r") as file:
            config = json.load(file)

        fernet = Fernet(self.config_key.encode())

        # Descriptografar os campos sensíveis
        if "login" in config and "usuario" in config["login"] and config["login"]["usuario"]:
            usuario = config["login"]["usuario"]
            if "senha" in usuario and usuario["senha"]:  # Verifica se a senha existe
                try:
                    usuario["senha"] = fernet.decrypt(
                        usuario["senha"].encode()
                    ).decode()
                except Exception as e:
                    raise ValueError(f"Erro ao descriptografar a senha: {e}")

        return config

    def verificar_ou_criar_arquivo_login(self):
        """Verifica se o arquivo de login existe e o cria caso contrário."""
        estrutura_base = {
            "login": {
                "usuario": None,
                "ultimo_acesso": None,
            },
            "preferencias": {},  # Configurações gerais
            "seguranca": {},     # Configurações relacionadas à segurança
        }

        if not os.path.exists(self.config_login):
            print("Criando novo arquivo de login.")
            self.salvar_config_login(estrutura_base)
        else:
            try:
                self.carregar_config_login()
                print("Arquivo de login carregado com sucesso.")
            except ValueError:
                print("Arquivo corrompido ou chave inválida. Recriando o arquivo.")
                self.salvar_config_login(estrutura_base)

    def verificar_login(self):
        """Verifica se o utilizador está logado e realiza login ou cadastro, se necessário."""
        config = self.carregar_config_login()

        # Aceder à chave "login"
        login_config = config.get("login", {})
        usuario_codificado = login_config.get("usuario")

        if not usuario_codificado:
            # Se não há utilizador cadastrado, abrir modal de cadastro
            cadastro_modal = CadastroDialog(parent=self)
            if cadastro_modal.exec() == QDialog.Accepted:
                return self.verificar_login()  # Revalidar após cadastro
            else:
                QMessageBox.critical(self, "Erro", "Cadastro é obrigatório. O sistema será encerrado.")
                sys.exit()  # Encerrar o sistema

        try:
            # Descriptografar os dados do utilizador
            fernet = Fernet(self.config_key.encode())
            nome_decodificado = fernet.decrypt(usuario_codificado.get("nome").encode()).decode()

            # Validar se o nome decodificado é válido
            if not nome_decodificado.strip():
                raise ValueError("Nome do utilizador inválido após descriptografia.")

            # Abrir modal de login
            login_modal = LoginDialog(parent=self)
            if login_modal.exec() == QDialog.Accepted:
                return True  # Login realizado com sucesso
            else:
                QMessageBox.critical(self, "Erro", "Login é obrigatório. O sistema será encerrado.")
                sys.exit()  # Encerrar o sistema

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar os dados do utilizador: {e}")
            return False

 #****************** Fim  login *********************************   
 
    def resizeEvent(self, event):
        """Evento que redimensiona o fundo ao redimensionar a janela."""
        self.definir_fundo()
        super().resizeEvent(event)

    def atualizar_interface(self):
        pass

    def definir_fundo(self):
        """Define o fundo da janela com uma imagem e opacidade."""
        # Cria a paleta
        palette = QPalette()

        # Carrega e ajusta a imagem ao tamanho da janela
        pixmap = QPixmap("max/assets/img/fundo.png").scaled(
            self.size(),  # Escala a imagem para preencher a janela
            Qt.IgnoreAspectRatio,  # Ignora o aspecto da imagem para cobrir o fundo
            Qt.SmoothTransformation  # Usa uma transformação suave ao redimensionar
        )

        # Cria uma camada de opacidade sobre a imagem
        opacidade = QColor(0, 0, 1, 190)  # Uma cor preta com 170 de opacidade (valor entre 0 e 255)
        overlay_pixmap = QPixmap(self.size())  # Cria um QPixmap do tamanho da janela
        overlay_pixmap.fill(opacidade)  # Preenche a camada com a cor opaca

        # Combina a imagem de fundo com a opacidade
        final_pixmap = pixmap.copy()  # Copia o fundo original
        painter = QPainter(final_pixmap)
        painter.drawPixmap(0, 0, overlay_pixmap)  # Desenha a camada de opacidade sobre o fundo
        painter.end()

        # Define a imagem com opacidade na paleta
        palette.setBrush(QPalette.Window, QBrush(final_pixmap))
        self.setPalette(palette)

    def criar_botoes_sidebar(self):
        """Cria os botões da sidebar com ícones."""    
        botoes_info = [
            ("Home", "max/assets/icon/circular.png", Home),
            ("Email", "max/assets/icon/circular.png", EmailDashboard),
            ("Tarefas", "max/assets/icon/circular.png", CalendarioDashboard),
            ("Chat", "max/assets/icon/circular.png", Chat),
            ("Comandos", "max/assets/icon/circular.png", Comando),
            ("Configurações", "max/assets/icon/circular.png", Configuracao)
        ]

        for nome, icone, janela_class in botoes_info:
            botao = QPushButton(nome)
            botao.setIcon(QIcon(icone))  # Define o ícone do botão
            botao.setIconSize(QSize(24, 24))  # Corrigido para usar QSize corretamente
            botao.setStyleSheet(
                "background: none; "
                "border: none; "  # Remove a borda
                "color: #2496be; "
                "font-size: 16px; "
                "padding: 5px; "
                "text-align: left;"  # Alinhamento do texto à esquerda
            )
            botao.setFocusPolicy(Qt.NoFocus)  # Remove a borda ao focar
            botao.clicked.connect(lambda checked, janela=janela_class: self.exibir_conteudo(janela))  # Conecta o botão
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
        if source == self.sidebar:
            if event.type() == QEvent.Enter:
                self.mostrar_sidebar()
            elif event.type() == QEvent.Leave:
                # Verifique se o mouse ainda está sobre um dos botões
                mouse_pos = QCursor.pos()  # Obtém a posição global do mouse
                if self.sidebar.geometry().contains(mouse_pos):  # Verifica se está dentro da sidebar
                    return False  # Ignora o evento se o mouse ainda estiver sobre a sidebar
                self.ocultar_sidebar()
        return super().eventFilter(source, event)

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
##################################### Fim #####################################
   
########################################################
    #     Processamento de fala  
    def processar_fala(self, texto_reconhecido):
  

        # Lista de comandos e suas variações
        comandos = {
            "bom dia": ["bom dia", "bom dia max"],
            "boa tarde": ["boa tarde", "boa tarde max"],
            "boa noite": ["boa noite", "boa noite max"],
            "saber hora": ["que horas são", "me diga as horas", "qual é a hora agora", "hora atual", "hora"],
            "saber data": ["que dia é hoje", "me diga a data", "qual é a data de hoje", "data atual", "data"],
            "pesquisar youtube": ["pesquisar no youtube", "procurar no youtube", "buscar vídeo no youtube", "youtube busca"],

            
            "fechar navegador chrome": ["fechar o navegador", "encerrar o navegador", "feche o navegador", "fecha o chrome", "pare o navegador"],
            "abrir navegador chrome": ["abra o navegador", "iniciar o navegador", "abrir o chrome", "começar o navegador"],
            
            "reiniciar computador": ["reiniciar o computador", "reinicie o computador", "dar reboot na máquina", "reiniciar o pc"],
            "desligar computador": ["desligar o computador", "encerrar o sistema", "desligue o pc", "apagar a máquina"],
            # abrindo navegadores
            "abrir edge": ["edge","abrir edge", "iniciar edge", "abrir navegador edge", "abrir microsoft edge"],
            "fechar edge": ["fechar edge", "encerrar edge", "parar navegador edge"],
            
            "abrir opera": ["abrir opera", "iniciar opera", "abrir navegador opera", "abrir opera mini"],
            "fechar opera": ["fechar opera", "encerrar opera", "parar navegador opera mini"],
            
            "abrir firefox": ["abrir firefox", "navegador firefox", "iniciar firefox"],
            "fechar firefox": ["fechar firefox", "encerrar firefox", "parar firefox"],
            
            
            "abrir bloco de notas": ["abrir bloco de notas", "abrir notepad", "iniciar bloco de notas", "bloco de notas"],
            "fechar bloco de notas": ["fechar bloco de notas", "parar bloco de notas", "encerrar bloco de notas"],
            
            "abrir calculadora": ["abrir calculadora", "iniciar calculadora", "abrir app de calculadora"],
            
            "abrir cmd": ["abrir cmd", "iniciar terminal", "abrir prompt de comando", "abrir linha de comando"],
            "fechar cmd": ["fechar cmd", "encerrar terminal", "fechar prompt de comando", "parar linha de comando"],
            "abrir explorador de arquivos": ["abrir explorador", "abrir pasta de arquivos", "abrir arquivos", "iniciar explorador de arquivos"],
            "fechar explorador de arquivos": ["fechar explorador", "encerrar pasta de arquivos", "parar explorador de arquivos", "fechar arquivos"],
            "abrir gestor de tarefas": ["abrir gestor de tarefas", "abrir task manager", "iniciar gestor de tarefas", "gestor de tarefas"],
            "fechar gestor de tarefas": ["fechar gestor de tarefas", "parar gestor de tarefas", "encerrar task manager"],
            "abrir gestor de disco": ["abrir gestor de disco", "abrir disk manager", "iniciar gestor de disco", "gestor de disco"],
            "abrir word": ["abrir word", "iniciar word", "abrir microsoft word", "word"],
            "fechar word": ["fechar word", "encerrar word", "parar microsoft word"],
            "abrir excel": ["abrir excel", "iniciar excel", "abrir microsoft excel", "excel"],
            "fechar excel": ["fechar excel", "encerrar excel", "parar microsoft excel"],
            "abrir power point": ["abrir power point", "iniciar power point", "abrir microsoft power point", "power point"],
            "fechar power point": ["fechar power point", "encerrar power point", "parar microsoft power point"],
            "abrir vlc": ["abrir vlc", "iniciar vlc", "abrir reprodutor vlc"],
            "fechar vlc": ["fechar vlc", "parar vlc", "encerrar vlc"],
            "abrir vs code": ["abrir vscode", "iniciar visual studio code", "abrir code"],
            "fechar vs code": ["fechar vscode", "encerrar visual studio code", "fechar code"],
            "abrir painel de controle": ["abrir painel de controle", "abrir control panel", "iniciar painel de controle"],
            "abrir registo do windows": ["abrir registo do windows", "abrir editor de registo", "abrir registro"],
            "abrir explorador de redes": ["abrir explorador de redes", "abrir rede", "abrir configurações de rede"],
            "abrir facebook": ["abrir facebook", "acessar facebook", "entrar no facebook"],
            "abrir whatsapp": ["abrir whatsapp", "iniciar whatsapp", "abrir app whatsapp"],
            "pesquisar na internet": ["pesquisar na internet", "fazer uma pesquisa", "procurar algo"],
            "abrir ficheiro específico": ["abrir ficheiro", "abrir documento", "abrir arquivo específico"]
        }

        # Normalizar texto reconhecido
        texto_reconhecido = texto_reconhecido.lower()

        # Verificar comando correspondente
        comando_encontrado = None
        for comando, variacoes in comandos.items():
            if texto_reconhecido in variacoes:
                comando_encontrado = comando
                break

        if comando_encontrado:
            print(f"Comando reconhecido: {comando_encontrado}")

            try:
                # Executar ação correspondente
                if comando_encontrado == "bom dia":
                    resposta = self.verificar_saudacao("bom dia")
                    self.reconhecimento_fala.fala(resposta)
                elif comando_encontrado == "boa tarde":
                    resposta = self.verificar_saudacao("boa tarde")
                    self.reconhecimento_fala.fala(resposta)
                elif comando_encontrado == "boa noite":
                    resposta = self.verificar_saudacao("boa noite")
                    self.reconhecimento_fala.fala(resposta)
                elif comando_encontrado == "saber hora":
                    try:
                        from datetime import datetime
                        hora_atual = datetime.now().strftime("%H:%M")
                        self.reconhecimento_fala.fala(f"A hora atual é {hora_atual}")
                    except Exception as e:
                        print(f"Erro ao obter a hora atual: {e}")
                        self.reconhecimento_fala.fala("Desculpa, não consegui obter a hora atual")
                elif comando_encontrado == "saber data":
                    try:
                        from datetime import datetime
                        data_atual = datetime.now().strftime("%d de %B de %Y")
                        self.reconhecimento_fala.fala(f"A data de hoje é {data_atual}")
                    except Exception as e:
                        print(f"Erro ao obter a data atual: {e}")
                        self.reconhecimento_fala.fala("Desculpa, não consegui obter a data de hoje")

                
                elif comando_encontrado == "pesquisar youtube":
                    try:
                        self.reconhecimento_fala.fala("O que deseja pesquisar no YouTube?")
                        pesquisa = self.reconhecimento_fala.escutar()  # Captura a entrada de voz do utilizador
                        if pesquisa:
                            url = f"https://www.youtube.com/results?search_query={pesquisa.replace(' ', '+')}"
                            webbrowser.open(url)
                            self.reconhecimento_fala.fala(f"Pesquisando por '{pesquisa}' no YouTube")
                        else:
                            self.reconhecimento_fala.fala("Não entendi o que você deseja pesquisar.")
                    except Exception as e:
                        print(f"Erro ao pesquisar no YouTube: {e}")
                        self.reconhecimento_fala.fala("Houve um erro ao tentar realizar a pesquisa no YouTube.")
               
                elif comando_encontrado == "abrir vlc":
                    try:
                        subprocess.Popen("vlc")
                        self.reconhecimento_fala.fala("Abrindo VLC")
                    except Exception as e:
                        print(f"Erro ao abrir VLC: {e}")
                        self.reconhecimento_fala.fala("Erro ao abrir o VLC")

                elif comando_encontrado == "fechar vlc":
                    try:
                        os.system("taskkill /f /im vlc.exe")
                        self.reconhecimento_fala.fala("Fechando VLC")
                    except Exception as e:
                        print(f"Erro ao fechar VLC: {e}")
                        self.reconhecimento_fala.fala("Erro ao fechar o VLC")
                elif comando_encontrado == "abrir vs code":
                    try:
                        subprocess.Popen("code")
                        self.reconhecimento_fala.fala("Abrindo Visual Studio Code")
                    except Exception as e:
                        print(f"Erro ao abrir VS Code: {e}")
                        self.reconhecimento_fala.fala("Erro ao abrir o Visual Studio Code")

                elif comando_encontrado == "fechar vs code":
                    try:
                        os.system("taskkill /f /im Code.exe")
                        self.reconhecimento_fala.fala("Fechando Visual Studio Code")
                    except Exception as e:
                        print(f"Erro ao fechar VS Code: {e}")
                        self.reconhecimento_fala.fala("Erro ao fechar o Visual Studio Code")
                elif comando_encontrado == "abrir painel de controle":
                    try:
                        subprocess.Popen("control")
                        self.reconhecimento_fala.fala("Abrindo o Painel de Controle")
                    except Exception as e:
                        print(f"Erro ao abrir o Painel de Controle: {e}")
                        self.reconhecimento_fala.fala("Erro ao abrir o Painel de Controle")

                elif comando_encontrado == "abrir registo do windows":
                    try:
                        subprocess.Popen("regedit")
                        self.reconhecimento_fala.fala("Abrindo o Registo do Windows")
                    except Exception as e:
                        print(f"Erro ao abrir o Registo do Windows: {e}")
                        self.reconhecimento_fala.fala("Erro ao abrir o Registo do Windows")

                elif comando_encontrado == "abrir explorador de redes":
                    try:
                        subprocess.Popen("ncpa.cpl")
                        self.reconhecimento_fala.fala("Abrindo o Explorador de Redes")
                    except Exception as e:
                        print(f"Erro ao abrir o Explorador de Redes: {e}")
                        self.reconhecimento_fala.fala("Erro ao abrir o Explorador de Redes")

                elif comando_encontrado == "abrir facebook":
                    try:
                        webbrowser.open("https://www.facebook.com")
                        self.reconhecimento_fala.fala("Abrindo Facebook")
                    except Exception as e:
                        print(f"Erro ao abrir Facebook: {e}")
                        self.reconhecimento_fala.fala("Erro ao abrir o Facebook")

                elif comando_encontrado == "abrir whatsapp":
                    try:
                        webbrowser.open("https://web.whatsapp.com")
                        self.reconhecimento_fala.fala("Abrindo WhatsApp")
                    except Exception as e:
                        print(f"Erro ao abrir WhatsApp: {e}")
                        self.reconhecimento_fala.fala("Erro ao abrir o WhatsApp")

                elif comando_encontrado == "pesquisar na internet":
                    try:
                        self.reconhecimento_fala.fala("O que desejas pesquisar?")
                        query = self.reconhecimento_fala.escuta()
                        if query:
                            webbrowser.open(f"https://www.google.com/search?q={query}")
                            self.reconhecimento_fala.fala(f"A pesquisar por {query}")
                        else:
                            self.reconhecimento_fala.fala("Nenhuma pesquisa reconhecida.")
                    except Exception as e:
                        print(f"Erro ao realizar a pesquisa: {e}")
                        self.reconhecimento_fala.fala("Erro ao realizar a pesquisa")

                
                elif comando_encontrado == "fechar navegador chrome":
                    os.system("taskkill /f /im chrome.exe /t")
                    self.reconhecimento_fala.fala("Fechando Chrome")
                elif comando_encontrado == "abrir navegador chrome":
                    os.system("start chrome")
                    self.reconhecimento_fala.fala("Abrindo Chrome")
               
                elif comando_encontrado == "abrir edge":
                    try:
                        subprocess.Popen("msedge")
                        self.reconhecimento_fala.fala("Abrindo Microsoft Edge")
                    except Exception as e:
                        print(f"Erro ao abrir Edge: {e}")
                        self.reconhecimento_fala.fala("Erro ao abrir Microsoft Edge")
                elif comando_encontrado == "fechar edge":
                    try:
                        os.system("taskkill /f /im msedge.exe")
                        self.reconhecimento_fala.fala("Fechando Microsoft Edge")
                    except Exception as e:
                        print(f"Erro ao fechar Edge: {e}")
                        self.reconhecimento_fala.fala("Erro ao fechar Microsoft Edge")

                elif comando_encontrado == "abrir opera":
                    try:
                        subprocess.Popen("opera")
                        self.reconhecimento_fala.fala("Abrindo Opera Mini")
                    except Exception as e:
                        print(f"Erro ao abrir Opera: {e}")
                        self.reconhecimento_fala.fala("Erro ao abrir Opera Mini")

                elif comando_encontrado == "fechar opera":
                    try:
                        os.system("taskkill /f /im opera.exe")
                        self.reconhecimento_fala.fala("Fechando Opera Mini")
                    except Exception as e:
                        print(f"Erro ao fechar Opera: {e}")
                        self.reconhecimento_fala.fala("Erro ao fechar Opera Mini")

                            
                elif comando_encontrado == "reiniciar computador":
                    os.system("shutdown /r /t 0")
                    self.reconhecimento_fala.fala("Reiniciando computador")
                elif comando_encontrado == "desligar computador":
                    os.system("shutdown /s /t 0")
                    self.reconhecimento_fala.fala("Desligando computador")
                elif comando_encontrado == "abrir firefox":
                    subprocess.Popen("firefox")
                    self.reconhecimento_fala.fala("Abrindo Firefox")
                elif comando_encontrado == "fechar firefox":
                    os.system("taskkill /f /im firefox.exe")
                    self.reconhecimento_fala.fala("Fechando Firefox")
                elif comando_encontrado == "abrir bloco de notas":
                    subprocess.Popen("notepad")
                    self.reconhecimento_fala.fala("Abrindo Bloco de Notas")
                elif comando_encontrado == "fechar bloco de notas":
                    os.system("taskkill /f /im notepad.exe")
                    self.reconhecimento_fala.fala("Fechando Bloco de Notas")
                elif comando_encontrado == "abrir calculadora":
                    subprocess.Popen("calc")
                    self.reconhecimento_fala.fala("Abrindo Calculadora")
                elif comando_encontrado == "abrir cmd":
                    subprocess.Popen("cmd")
                    self.reconhecimento_fala.fala("Abrindo CMD")
                elif comando_encontrado == "fechar cmd":
                    os.system("taskkill /f /im cmd.exe /t")
                    self.reconhecimento_fala.fala("Fechando CMD")
                elif comando_encontrado == "abrir explorador de arquivos":
                    subprocess.Popen("explorer")
                    self.reconhecimento_fala.fala("Abrindo o Explorador de Arquivos")
                elif comando_encontrado == "fechar explorador de arquivos":
                    os.system("taskkill /f /im explorer.exe /t")
                    self.reconhecimento_fala.fala("Fechando o Explorador de Arquivos")
                elif comando_encontrado == "abrir gestor de tarefas":
                    subprocess.Popen("taskmgr")
                    self.reconhecimento_fala.fala("Abrindo Gestor de Tarefas")
                elif comando_encontrado == "fechar gestor de tarefas":
                    os.system("taskkill /f /im taskmgr.exe /t")
                    self.reconhecimento_fala.fala("Fechando Gestor de Tarefas")
                elif comando_encontrado == "abrir gestor de disco":
                    subprocess.Popen("diskmgmt.msc")
                    self.reconhecimento_fala.fala("Abrindo Gestor de Disco")
                elif comando_encontrado == "abrir word":
                    subprocess.Popen("start winword", shell=True)
                    self.reconhecimento_fala.fala("Abrindo Microsoft Word")
                elif comando_encontrado == "fechar word":
                    os.system("taskkill /f /im winword.exe")
                    self.reconhecimento_fala.fala("Fechando Microsoft Word")
                elif comando_encontrado == "abrir excel":
                    subprocess.Popen("start excel", shell=True)
                    self.reconhecimento_fala.fala("Abrindo Microsoft Excel")
                elif comando_encontrado == "fechar excel":
                    os.system("taskkill /f /im excel.exe")
                    self.reconhecimento_fala.fala("Fechando Microsoft Excel")
                elif comando_encontrado == "abrir power point":
                    subprocess.Popen("start powerpnt", shell=True)
                    self.reconhecimento_fala.fala("Abrindo Microsoft PowerPoint")
                elif comando_encontrado == "fechar power point":
                    os.system("taskkill /f /im powerpnt.exe")
                    self.reconhecimento_fala.fala("Fechando Microsoft PowerPoint")
            except Exception as e:
                print(f"Erro ao executar ação: {e}")
                self.reconhecimento_fala.fala("Ocorreu um erro ao tentar executar o comando.")
        else:
            print(f"Comando não reconhecido: '{texto_reconhecido}'")
            self.reconhecimento_fala.fala("Comando não reconhecido!")

    def calcular_segundos(tempo_str):
        try:
            partes = tempo_str.lower().split(" ")
            total_segundos = 0
            
            for i, palavra in enumerate(partes):
                if palavra.isdigit():
                    valor = int(palavra)
                    if "hora" in partes[i + 1]:
                        total_segundos += valor * 3600
                    elif "minuto" in partes[i + 1]:
                        total_segundos += valor * 60
            return total_segundos
        except Exception:
            return None

    # Função para interagir sobre reiniciar
    def interagir_acao(self, tipo_acao):
        if tipo_acao == "reiniciar":
            self.reconhecimento_fala.fala("Você deseja reiniciar agora ou prefere agendar?")
        else:  # Desligar
            self.reconhecimento_fala.fala("Você deseja desligar agora ou prefere agendar?")
        
        resposta = self.reconhecimento_fala.escutar()

        if "agendar" in resposta or "mais tarde" in resposta:
            self.reconhecimento_fala.fala("Por favor, diga o tempo. Por exemplo: 'daqui a 30 minutos' ou 'às 16:00'.")
            tempo_resposta = self.reconhecimento_fala.escutar()

            if "daqui" in tempo_resposta:
                segundos = self.calcular_segundos(tempo_resposta)
                if segundos:
                    os.system(f"shutdown {'/r' if tipo_acao == 'reiniciar' else '/s'} /t {segundos}")
                    self.reconhecimento_fala.fala(f"{tipo_acao.capitalize()} programado para daqui a {segundos // 60} minutos.")
                else:
                    self.reconhecimento_fala.fala("Desculpe, não consegui entender o tempo. Tente novamente.")
            elif "às" in tempo_resposta:
                try:
                    hora_programada = datetime.strptime(tempo_resposta.split("às")[1].strip(), "%H:%M")
                    agora = datetime.now()
                    segundos = (hora_programada - agora).seconds if hora_programada > agora else None
                    
                    if segundos:
                        os.system(f"shutdown {'/r' if tipo_acao == 'reiniciar' else '/s'} /t {segundos}")
                        self.reconhecimento_fala.fala(f"{tipo_acao.capitalize()} programado para às {hora_programada.strftime('%H:%M')}.")
                    else:
                        self.reconhecimento_fala.fala("O horário indicado já passou. Por favor, tente novamente.")
                except Exception:
                    self.reconhecimento_fala.fala("Desculpe, não consegui entender o horário. Tente novamente.")
        elif "agora" in resposta:
            os.system(f"shutdown {'/r' if tipo_acao == 'reiniciar' else '/s'} /t 0")
            self.reconhecimento_fala.fala(f"{tipo_acao.capitalize()} o computador agora.")
        elif "cancelar" in resposta:
            os.system("shutdown /a")
            self.reconhecimento_fala.fala("Ação agendada foi cancelada.")
        else:
            self.reconhecimento_fala.fala("Desculpe, não entendi sua resposta.")

    # Função para verificar comandos relacionados a tempo
    def verificar_comando_tempo(self, comando, tipo_acao):
        if "daqui a" in comando:
            tempo_str = comando.split("daqui a")[1].strip()
            segundos = self.calcular_segundos(tempo_str)
            if segundos:
                os.system(f"shutdown {'/r' if tipo_acao == 'reiniciar' else '/s'} /t {segundos}")
                self.reconhecimento_fala.fala(f"{tipo_acao.capitalize()} programado para daqui a {segundos // 60} minutos.")
            else:
                self.reconhecimento_fala.fala("Desculpe, não consegui entender o tempo.")
            return True
        elif "agora" in comando:
            os.system(f"shutdown {'/r' if tipo_acao == 'reiniciar' else '/s'} /t 0")
            self.reconhecimento_fala.fala(f"{tipo_acao.capitalize()} o computador agora.")
            return True
        return False
 
    def buscar_acao_por_comando(self, comando_reconhecido):
        comando_reconhecido = comando_reconhecido.strip().lower()  # Normaliza o comando reconhecido
        for acao, variacoes in self.comandos_variacoes.items():
            if comando_reconhecido in (var.strip().lower() for var in variacoes):
                return acao
        return None


    def verificar_saudacao(self, saudacao_reconhecida):
       
        horario_atual = datetime.now().hour

        if saudacao_reconhecida == "bom dia" and 6 <= horario_atual < 12:
            return "Bom dia, senhor! Como o senhor está?"
        elif saudacao_reconhecida == "boa tarde" and 12 <= horario_atual < 18:
            return "Boa tarde, senhor! Como o senhor está?"
        elif saudacao_reconhecida == "boa noite" and (18 <= horario_atual < 24 or 0 <= horario_atual < 6):
            return "Boa noite, senhor! Como o senhor está?"
        else:
            # Determina a saudação correta com base no horário
            if horario_atual < 12:
                saudacao_correta = "bom dia"
            elif horario_atual < 18:
                saudacao_correta = "boa tarde"
            else:
                saudacao_correta = "boa noite"

            return f"Agora é {saudacao_correta}, senhor, não {saudacao_reconhecida}. Como o senhor está?"
      
    def minimizar_todas_as_janelas(self):
        """Minimiza todas as janelas usando o atalho Win + M."""
        try:
            pyautogui.hotkey("win", "m")
            print("Todas as janelas foram minimizadas.")
        except Exception as e:
            self.log_error(f"Erro ao minimizar janelas: {e}")   
    
    def carregar_comandos(self):
        try:
            with open(self.caminho_comandos_json, "r", encoding="utf-8") as arquivo:
                comandos_variacoes = json.load(arquivo)
                print(f"Comandos carregados: {json.dumps(comandos_variacoes, indent=2, ensure_ascii=False)}")  # Verificar comandos
                return comandos_variacoes
        except Exception as e:
            self.log_error(f"Erro ao carregar o arquivo comandos.json: {e}")
            return {}
  
    
    def verificar_ou_criar_arquivo_comandos(self):
        """Verifica se o arquivo comandos.json existe, caso contrário, cria com estrutura inicial."""
        if not os.path.exists(self.caminho_comandos_json):
            try:
                # Estrutura inicial do arquivo
                estrutura_inicial = {"comandos": []}
                with open(self.caminho_comandos_json, "w", encoding="utf-8") as arquivo:
                    json.dump(estrutura_inicial, arquivo, indent=4, ensure_ascii=False)
                print(f"Arquivo {self.caminho_comandos_json} criado com sucesso.")
            except Exception as e:
               self.log_erro(f"Erro ao criar o arquivo comandos.json: {e}")
        else:
            print(f"O arquivo {self.caminho_comandos_json} já existe.")

    # Função para abrir uma janela
    def abrir_janela(self, janela, mensagem):
        self.exibir_conteudo(janela)
        self.reconhecimento_fala.fala(mensagem)

    # Função para fechar uma janela
    def fechar_janela(self, janela, mensagem):
        self.fechar_conteudo(janela)
        self.reconhecimento_fala.fala(mensagem)

    # Função para fechar o assistente
    def fechar_assistente(self):
        self.reconhecimento_fala.fala("Encerrando o assistente. Até logo!")
        sys.exit()

    # Função para monitorar o uso de CPU
    def monitorar_cpu(self):
        uso_cpu = psutil.cpu_percent(interval=1)
        mensagem = f"Uso atual da CPU é de {uso_cpu}%."
        self.reconhecimento_fala.fala(self, mensagem)

    # Função para monitorar o uso de memória
    def monitorar_memoria(self):
        memoria = psutil.virtual_memory()
        uso_memoria = memoria.percent
        memoria_livre = memoria.available / (1024 ** 3)  # em GB
        mensagem = f"Uso de memória está em {uso_memoria}%. Memória livre: {memoria_livre:.2f} GB."
        self.reconhecimento_fala.fala(self, mensagem)

    # Função para monitorar o nível da bateria
    def monitorar_bateria(self):
        bateria = psutil.sensors_battery()
        if bateria:
            nivel_bateria = bateria.percent
            status = "carregando" if bateria.power_plugged else "descarregando"
            tempo_restante = bateria.secsleft // 60 if bateria.secsleft > 0 else "desconhecido"
            mensagem = f"Nível da bateria: {nivel_bateria}%. Status: {status}. Tempo restante: {tempo_restante} minutos."
        else:
            mensagem = "Informação sobre a bateria não disponível."
            self.reconhecimento_fala.fala(self,mensagem)

    def enviar_boas_vindas(self):
        """Exibe e fala uma mensagem de boas-vindas personalizada com base no horário."""
        # Obter a hora atual
        hora_atual = datetime.now().hour

        # Determinar saudação com base na hora
        if 5 <= hora_atual < 12:
            saudacao = "Bom dia"
        elif 12 <= hora_atual < 18:
            saudacao = "Boa tarde"
        else:
            saudacao = "Boa noite"

        # Lista de mensagens criativas e empolgantes
        mensagens_padrao = [
            f"{saudacao}, senhor! O Cortex Virtual foi inicializado com sucesso. Em que posso ajudar?",
            f"{saudacao}, senhor! O sistema foi carregado sem erros e está operacional. Estou à disposição para ajudar.",
            f"{saudacao}, senhor! O Cortex foi iniciado com êxito. Como posso ajudar agora?",
            f"{saudacao}, senhor! O sistema está funcional e preparado para atender às suas solicitações. Em que posso ser útil?",
            f"{saudacao}, senhor! O Cortex Virtual System está funcionando perfeitamente. Estou aqui para facilitar o que precisar.",
            f"{saudacao}, senhor! A inicialização foi concluída com sucesso. Qual é a próxima tarefa?",
            f"{saudacao}, senhor! O sistema foi carregado corretamente. Como posso ajudar?"
        ]

        # Escolher uma mensagem aleatoriamente
        mensagem = random.choice(mensagens_padrao)

        self.reconhecimento_fala.fala(mensagem)
    #              Processamento de fala 
########################################################  
   
    # Função para fechar a janela
    def fechar_conteudo(self, janela_class):
        """Fecha a janela especificada se estiver aberta."""
        for i in reversed(range(self.central_layout.count())): 
            widget = self.central_layout.itemAt(i).widget()
            if isinstance(widget, janela_class):
                widget.deleteLater()  # Remove o widget existente
        
    def closeEvent(self, event):
        """Método para encerrar a thread ao fechar a janela."""
        self.reconhecimento_fala.parar_reconhecimento()
        self.thread_reconhecimento.quit()
        self.thread_reconhecimento.wait()
        super().closeEvent(event)
  
    def log_erro(self, mensagem):
        """Registra mensagens de erro no arquivo de log com traceback completo."""
        try:
            
            with open(self.log_file, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - ERROR - {mensagem}\n")
                # Adiciona o traceback completo se houver uma exceção ativa
                log_file.write(traceback.format_exc() + "\n")
        except Exception as e:
           self.log_erro(f"Erro ao registrar log: {e}")    
                   
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = MainWindow()
    janela.show()
    sys.exit(app.exec())

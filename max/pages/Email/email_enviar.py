
from email.mime.text import MIMEText
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                               QTextEdit, QLabel, QFileDialog, QMessageBox, QToolButton, QWidget)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
import logging
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import socket
from PySide6.QtWidgets import QMessageBox, QInputDialog
import json
import re
import os
class EmailCompor(QDialog):
    def __init__(self, base_dir):
        super().__init__()
        self.base_dir = base_dir
        self.enviados_path = os.path.join(self.base_dir, "enviados")
    
        self.upload_path = os.path.join(self.base_dir, "Upload")  # Pasta para arquivos enviados
        self.download_path = os.path.join(self.base_dir, "Download")  # Pasta para arquivos recebidos

        # Cria as pastas de Upload e Download se não existirem
        os.makedirs(self.upload_path, exist_ok=True)
        os.makedirs(self.download_path, exist_ok=True)

        # Variável para armazenar o caminho do arquivo anexado
        self.arquivo_anexado = None

        # Configurações da janela
        self.setWindowTitle("Compor E-mail")
        self.setFixedSize(800, 400)  # Ajustar tamanho para acomodar a sidebar
        self.setWindowIcon(QIcon("max/assets/icon/circular.png"))  # Alterar o ícone do modal

        # Adiciona fundo à janela
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(0, 21, 42, 180);  /* Cor de fundo do modal */
                border-radius: 10px;
            }
        """)

        layout = QHBoxLayout(self)  # Layout principal horizontal (para incluir sidebar)

        # Sidebar layout
        sidebar_layout = QVBoxLayout()

        # Criar um widget para a sidebar
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(100)
        sidebar_widget.setLayout(sidebar_layout)

        # Botão "Enviar"
        self.botao_enviar = QToolButton()
        self.botao_enviar.setIcon(QIcon("max/assets/icon/circular.png"))  # Substitua pelo caminho do seu ícone
        self.botao_enviar.setIconSize(QSize(32, 32))
        self.botao_enviar.setToolTip("Enviar mensagem")
        self.botao_enviar.clicked.connect(self.enviar_email)
        sidebar_layout.addWidget(self.botao_enviar)

        # Botão "Carregar Arquivo"
        self.botao_carregar = QToolButton()
        self.botao_carregar.setIcon(QIcon("max/assets/icon/circular.png"))  # Substitua pelo caminho do seu ícone
        self.botao_carregar.setIconSize(QSize(32, 32))
        self.botao_carregar.setToolTip("Carregar ficheiro")
        self.botao_carregar.clicked.connect(self.carregar_arquivo)
        sidebar_layout.addWidget(self.botao_carregar)

        # Botão "Cancelar"
        self.botao_cancelar = QToolButton()
        self.botao_cancelar.setIcon(QIcon("max/assets/icon/circular.png"))  # Substitua pelo caminho do seu ícone
        self.botao_cancelar.setIconSize(QSize(32, 32))
        self.botao_cancelar.setToolTip("Cancelar")
        self.botao_cancelar.clicked.connect(self.close)
        sidebar_layout.addWidget(self.botao_cancelar)

        # Adiciona espaço extra na parte inferior
        sidebar_layout.addStretch()

        # Adiciona o widget da sidebar no layout principal
        layout.addWidget(sidebar_widget)

        # Estilos CSS para os botões e sidebar
        sidebar_style = """
            padding: 10px;
            border-radius: 10px;
            border: 2px solid #2496be;
        """
        self.setStyleSheet(f"""
            QVBoxLayout {{
                {sidebar_style}
            }}
            QToolButton {{
                border: none;
                border-radius: 5px;
                padding: 4px;
                margin-bottom: 5px;
            }}
            QToolButton:hover {{
                background-color: #2496be;  /* Cor ao passar o mouse */
            }}
        """)

        # Layout para os campos do e-mail
        email_layout = QVBoxLayout()

        # Estilo das labels
        label_style = """
            color: #2496be;  /* Cor do texto das labels */
            font-weight: bold;  /* Negrito nas labels */
        """

        # Campo destinatário (estilizado)
        self.input_destinatario = QLineEdit()
        self.input_destinatario.setPlaceholderText("Destinatário")
        self.input_destinatario.setStyleSheet("""
            color: white;  /* Cor do texto dentro do campo */
            background-color: rgba(0, 21, 42, 180);  /* Cor de fundo do campo */
            border-bottom: 2px solid #2496be;

            border-left: none;
            border-top: none;
            border-right: none;
            border-radius: 5px;  /* Borda arredondada */
            padding: 5px;
            font-weight: bold;
        """)
        destinatario_label = QLabel("Para")
        destinatario_label.setStyleSheet(label_style)
        email_layout.addWidget(destinatario_label)
        email_layout.addWidget(self.input_destinatario)

        # Campo assunto (estilizado)
        self.input_assunto = QLineEdit()
        self.input_assunto.setPlaceholderText("Assunto")
        self.input_assunto.setStyleSheet("""
           color: white;  /* Cor do texto dentro do campo */
            background-color: rgba(0, 21, 42, 180);  /* Cor de fundo do campo */
            border-bottom: 2px solid #2496be;

            border-left: none;
            border-top: none;
            border-right: none;
            border-radius: 5px;  /* Borda arredondada */
            padding: 5px;
            font-weight: bold;
        """)
        assunto_label = QLabel("Assunto")
        assunto_label.setStyleSheet(label_style)
        email_layout.addWidget(assunto_label)
        email_layout.addWidget(self.input_assunto)

        # Campo corpo do e-mail (estilizado)
        self.input_corpo = QTextEdit()
        self.input_corpo.setPlaceholderText("Corpo do Email")
        self.input_corpo.setStyleSheet("""
            color: white;  /* Cor do texto dentro do campo */
            background-color: rgba(0, 21, 42, 180);  /* Cor de fundo do campo */
            border-bottom: 2px solid #2496be;

            border-left: none;
            border-top: none;
            border-right: none;
            border-radius: 5px;  /* Borda arredondada */
            padding: 5px;
            font-weight: bold;
        """)
        corpo_label = QLabel("Corpo do E-mail")
        corpo_label.setStyleSheet(label_style)
        email_layout.addWidget(corpo_label)
        email_layout.addWidget(self.input_corpo)

        # Adiciona o layout dos campos de e-mail ao layout principal
        layout.addLayout(email_layout)

    def validar_email(self, email):
        """Valida a sintaxe do e-mail."""
        padrao_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(padrao_email, email)
    
    def carregar_arquivo(self):
        """Abre um diálogo para carregar arquivos e os salva na pasta de upload."""
        arquivo, _ = QFileDialog.getOpenFileName(self, "Carregar Ficheiro", "", "Todos os arquivos (*)")
        if arquivo:
            try:
                # Copia o arquivo para a pasta de upload
                nome_arquivo = os.path.basename(arquivo)
                caminho_upload = os.path.join(self.upload_path, nome_arquivo)
                
                # Cria a pasta de upload se não existir
                if not os.path.exists(self.upload_path):
                    os.makedirs(self.upload_path)

                # Copia o arquivo selecionado para a pasta de upload
                with open(arquivo, 'rb') as f_src:
                    with open(caminho_upload, 'wb') as f_dest:
                        f_dest.write(f_src.read())

                # Armazena o caminho do arquivo anexado
                self.arquivo_anexado = caminho_upload
                self.notificar_sucesso(f"Arquivo Selecionado:Arquivo {nome_arquivo} carregado com sucesso!")
            except Exception as e:
                logging.error(f"Erro ao carregar arquivo: {e}")
                self.notificar_erro(f"Erro ao carregar arquivo: {e}")
     
    def enviar_email(self):
        """Envia o e-mail com validação e anexa arquivos, se houver."""
        destinatario = self.input_destinatario.text()
        assunto = self.input_assunto.text()
        corpo = self.input_corpo.toPlainText()

        # Validações básicas
        if not destinatario or not assunto or not corpo:
            self.notificar_erro("Erro de Validação. Todos os campos devem estar preenchidos.")
            return

        # Validação do formato de e-mail
        if not self.validar_email(destinatario):
            self.notificar_erro("Erro de Validação. E-mail do destinatário inválido.")
            return

        # Verificar conexão de internet
        if not self.verificar_conexao():
            self.notificar_erro("Erro de conexão com a internet. Verifique sua conexão e tente novamente.")
            return

        try:
            # Configurações do e-mail
            msg = MIMEMultipart()
            msg['From'] = 'betuelsumbane2000@gmail.com'  # Trocar pelo seu e-mail
            msg['To'] = destinatario
            msg['Subject'] = assunto
            msg.attach(MIMEText(corpo, 'plain'))

            # Verifica se há arquivo anexado
            if self.arquivo_anexado:
                with open(self.arquivo_anexado, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(self.arquivo_anexado)}')
                    msg.attach(part)

            # Configurações do servidor SMTP (Gmail como exemplo)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            seu_email = 'betuelsumbane2000@gmail.com'  # Trocar pelo seu e-mail
            sua_senha = 'hush hurf dnqc wjtp'  # Trocar pela sua senha ou senha de app

            # Conexão com o servidor SMTP
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Inicia a criptografia TLS
                server.login(seu_email, sua_senha)  # Faz login no servidor
                server.send_message(msg)

            # Salva o e-mail na pasta "Enviados"
            self.salvar_email_enviado(destinatario, assunto, corpo)
            self.notificar_sucesso("E-mail enviado com sucesso!")
            self.close()
        
        except Exception as e:
            logging.error(f"Erro ao enviar e-mail: {e}")
            # Perguntar se deseja salvar no rascunho
            resposta = QMessageBox.question(self, "Falha ao enviar", "Falha ao enviar o e-mail. Deseja salvar no rascunho?",
                                            QMessageBox.Yes | QMessageBox.No)
            if resposta == QMessageBox.Yes:
                self.salvar_rascunho(destinatario, assunto, corpo)
            else:
                self.notificar_erro("E-mail não enviado e não salvo.")
     
    def salvar_email_enviado(self, destinatario, assunto, corpo):
        """Salva o e-mail enviado com um ID sequencial no arquivo enviados.json."""
        
        # Caminho do arquivo enviados.json
        enviados_file = os.path.join(self.enviados_path, "enviados.json")

        # Verificar se o arquivo existe, senão criar com uma lista vazia
        if os.path.exists(enviados_file):
            with open(enviados_file, 'r') as f:
                enviados_data = json.load(f)
                # Define o próximo ID como o último ID + 1
                if enviados_data:
                    ultimo_id = int(enviados_data[-1]["id"])
                    email_id = ultimo_id + 1
                else:
                    email_id = 1
        else:
            enviados_data = []
            email_id = 1

        email_data = {
            "id": str(email_id),
            "destinatario": destinatario,
            "assunto": assunto,
            "corpo": corpo,
            "anexo": os.path.basename(self.arquivo_anexado) if self.arquivo_anexado else None,
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Adicionar o novo e-mail aos dados existentes
        enviados_data.append(email_data)

        # Salvar de volta no arquivo JSON
        with open(enviados_file, 'w') as f:
            json.dump(enviados_data, f, indent=4)

        print(f"E-mail enviado e salvo com ID {email_id}.")

    def validar_email(self, email):
        """Valida a sintaxe do e-mail."""
        import re
        padrao = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(padrao, email) is not None

    def salvar_anexos_recebidos(self, anexos):
        """Salva os anexos recebidos na pasta de downloads."""
        """Envia o e-mail com validação e anexo."""
        destinatario = self.input_destinatario.text()
        assunto = self.input_assunto.text()
        corpo = self.input_corpo.toPlainText()
        
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        
        for anexo in anexos:
            caminho_anexo = os.path.join(self.download_path, anexo['nome'])
            with open(caminho_anexo, 'wb') as f:
                f.write(anexo['conteudo'])
            logging.info(f"Anexo {anexo['nome']} salvo em {caminho_anexo}")
    
    def verificar_conexao(self):
        """Verifica se há conexão com a internet tentando conectar-se ao Google."""
        try:
            # Tentativa de conexão ao servidor do Google (porta 80, HTTP)
            socket.create_connection(("www.google.com", 80))
            return True
        except OSError:
            return False

    def salvar_rascunho(self, destinatario, assunto, corpo):
        """Salva o e-mail como rascunho."""
        rascunho_path = os.path.join(self.base_dir, "rascunhos")
        if not os.path.exists(rascunho_path):
            os.makedirs(rascunho_path)

        # Dados do e-mail
        email_data = {
            "destinatario": destinatario,
            "assunto": assunto,
            "corpo": corpo,
            "anexo": os.path.basename(self.arquivo_anexado) if self.arquivo_anexado else None,
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Salva o e-mail como rascunho
        rascunho_file = os.path.join(rascunho_path, f"rascunho_{datetime.now().timestamp()}.json")
        with open(rascunho_file, 'w') as f:
            json.dump(email_data, f, indent=4)

        self.notificar_sucesso("Rascunho Salvo. E-mail salvo como rascunho.")
        

    def notificar_sucesso(self, mensagem):
        QMessageBox.information(self, "Sucesso", mensagem)

    def notificar_erro(self, mensagem):
        QMessageBox.critical(self, "Erro", mensagem)
import os
import json
import imaplib
import email
from email.header import decode_header
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QCheckBox, QPushButton, QHBoxLayout,
                               QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                               QTextEdit, QLabel, QFileDialog, QMessageBox, QToolButton, QWidget)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon, QCursor
import logging
from datetime import datetime
import socket
import re
from dateutil import parser  # Adicionar importação do parser
from PySide6.QtCore import QThread, Signal
from cryptography.fernet import Fernet
from dotenv import load_dotenv, set_key 
import base64

# Caminho para o arquivo JSON que contém os emails recebidos
EMAILS_RECEBIDOS_PATH = os.path.join("B:\\Estudos\\Projetos\\Python\\Max\\max\\pages\\Email\\Gestor_Email", "recebidos", "emails_recebidos.json")
LOG_DIR = "B:\\Estudos\\Projetos\\Python\\Max\\max\\pages\\Email\\Gestor_Email\\Logs"

# Configurações do servidor IMAP (Gmail)
IMAP_SERVER = "imap.gmail.com"
SEU_EMAIL = 'betuelsumbane2000@gmail.com'
SUA_SENHA = 'hush hurf dnqc wjtp'  # Senha de app do Gmail

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

class EmailSyncThread(QThread):
    # Sinal para enviar emails sincronizados de volta à interface principal
    emails_sync_done = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        novos_emails = EmailRecebido().receber_emails_do_servidor()
        self.emails_sync_done.emit(novos_emails)

class EmailRecebido(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.email_sync_thread = EmailSyncThread()
        self.email_sync_thread.emails_sync_done.connect(self.processar_emails_sincronizados)
        
        # Caminho do .env
        self.dotenv_path = "B:\\Estudos\\Projetos\\Python\\Max\\max\\config\\config.env"
        # Carrega o arquivo .env
        load_dotenv(self.dotenv_path)
        self.config_key = self.obter_ou_gerar_chave()  # Carregar chave automaticamente
        
        self.chave =  self.config_key
        self.fernet = Fernet(self.chave)
        
        # Iniciar a sincronização periodicamente
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.iniciar_sincronizacao_assincrona)
        self.timer.start(120000) 

        # Tabela para mostrar os e-mails recebidos
        self.tabela_emails = QTableWidget()
        self.tabela_emails.setColumnCount(6)  # Seis colunas: Caixa de marcação, Remetente, Assunto, Data, Status, Ações
        self.tabela_emails.setHorizontalHeaderLabels(["", "Remetente", "Assunto", "Data", "Status", "Ações"])
        self.tabela_emails.horizontalHeader().setStretchLastSection(True)  # A última coluna se ajusta
        self.tabela_emails.itemDoubleClicked.connect(self.abrir_detalhes_email)

       # Estilo da tabela
        self.tabela_emails.setStyleSheet("""
            QTableWidget {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #00152a, stop: 1 #0d3c55
                );
                color: white;                /* Cor do texto */
                border-radius: 7px;
                border: 2px solid #2496be;
            }
            QTableWidget::item {
                background-color: none;   /* Fundo das células */
                border-bottom: 1px solid #2496be;   /* Borda das células */
                border-top: none;   /* Borda das células */
                border-left: none;   /* Borda das células */
                border-right: none;   /* Borda das células */
            }
            QTableWidget::item:selected {
                background-color: #2496be;   /* Fundo das células selecionadas */
                color: black;                /* Cor do texto selecionado */
            }
            QHeaderView::section {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #00152a, stop: 1 #0d3c55
                );  /* Gradiente de azul escuro para azul médio */
                color: #2496be;  /* Azul claro */
                font-size: 14px;             /* Tamanho da fonte */
                padding: 3px; 
                border: 2px solid #2496be;   /* Borda das células */
                border-left: none;
                border-right: none;
                border-top: none;
            }
            /* Estilo da barra de rolagem vertical */
            QScrollBar:vertical {
                background: none;
                width: 12px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #2496be; /* Cor da barra de rolagem */
                min-height: 20px;
                border-radius: 6px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
            /* Estilo da barra de rolagem horizontal */
            QScrollBar:horizontal {
                background-color: none; /* Fundo da barra de rolagem */
                height: 15px;
                margin: 0px 3px 0px 3px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background-color: #2496be; /* Cor da barra de rolagem */
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                background: none;
            }
        """)
        self.tabela_emails.setSelectionBehavior(QTableWidget.SelectRows)  # Selecionar linhas inteiras
        layout.addWidget(self.tabela_emails)

        # Carregar os e-mails do arquivo JSON
        self.carregar_emails()
        
        self.setLayout(layout)

    def iniciar_sincronizacao_assincrona(self):
        """Inicia a sincronização dos e-mails em uma nova thread."""
        if not self.email_sync_thread.isRunning():
            self.email_sync_thread.start()

    def processar_emails_sincronizados(self, novos_emails):
        """Processa e exibe os e-mails sincronizados após o término da sincronização."""
        if novos_emails:
            self.atualizar_emails_json(novos_emails)
            self.carregar_emails()
        else:
            print("Nenhum e-mail novo encontrado para sincronizar.")
            
    def sincronizar_emails(self):
        """Sincroniza os e-mails com o servidor Gmail e atualiza o arquivo JSON."""
        try:
            socket.create_connection((IMAP_SERVER, 993), timeout=10)  # Testa a conexão com o servidor IMAP
            novos_emails = self.receber_emails_do_servidor()

            if novos_emails:
                self.atualizar_emails_json(novos_emails)
                self.carregar_emails()  # Atualiza a interface
            else:
                print("Nenhum e-mail novo encontrado para sincronizar.")
        except (socket.timeout, socket.gaierror) as e:
            erro_msg = "Sem conexão com a Internet ou erro ao conectar ao servidor IMAP."
            logging.error(f"{erro_msg}: {e}")
            self.notificar_erro(erro_msg)
        except Exception as e:
            erro_msg = f"Erro ao sincronizar os emails: {e}"
            logging.error(erro_msg)
            self.notificar_erro(erro_msg)



    # def atualizar_emails_json(self, novos_emails):
    #     """Atualiza o arquivo JSON com novos e-mails, evitando duplicatas e encriptando os dados sensíveis."""
    #     try:
    #         # Inicializa a lista de e-mails existentes
    #         emails_existentes = []

    #         # Verifica se o arquivo JSON já existe
    #         if os.path.exists(EMAILS_RECEBIDOS_PATH):
    #             with open(EMAILS_RECEBIDOS_PATH, 'r', encoding='utf-8') as f:
    #                 conteudo = f.read().strip()
    #                 if conteudo:  # Só tenta carregar se o arquivo não estiver vazio
    #                     emails_existentes = json.loads(conteudo)

    #         # Cria um conjunto de identificadores únicos para evitar duplicatas
    #         ids_existentes = {(email.get("id"), email.get("data")) for email in emails_existentes}

    #         # Lista para armazenar novos e-mails a serem salvos
    #         emails_a_salvar = []

    #         for email in novos_emails:
    #             # Ajusta a data do e-mail (ou atribui uma data padrão, se necessário)
    #             email["data"] = self.ajustar_formato_data(email.get("data", ""))

    #             # Verifica se o e-mail já existe
    #             if (email.get("id"), email["data"]) not in ids_existentes:
    #                 # Encripta os campos sensíveis do e-mail e converte para Base64
    #                 email["remetente"] = base64.b64encode(self.encriptar(email.get("remetente", ""), self.fernet)).decode("utf-8")
    #                 email["assunto"] = base64.b64encode(self.encriptar(email.get("assunto", ""), self.fernet)).decode("utf-8")
    #                 email["body"] = base64.b64encode(self.encriptar(email.get("body", ""), self.fernet)).decode("utf-8")
    #                 email["status"] = base64.b64encode(self.encriptar(email.get("status", ""), self.fernet)).decode("utf-8")

    #                 # Adiciona o e-mail encriptado à lista
    #                 emails_a_salvar.append(email)

    #         if emails_a_salvar:
    #             # Atualiza a lista de e-mails existentes com os novos
    #             emails_existentes.extend(emails_a_salvar)

    #             # Salva os e-mails atualizados no arquivo JSON
    #             with open(EMAILS_RECEBIDOS_PATH, 'w', encoding='utf-8') as f:
    #                 json.dump(emails_existentes, f, indent=4, ensure_ascii=False)

    #             print(f"{len(emails_a_salvar)} e-mail(s) novo(s) salvo(s).")
    #         else:
    #             print("Nenhum novo e-mail para atualizar no JSON.")

    #     except json.JSONDecodeError as e:
    #         logging.error(f"Erro ao ler o arquivo JSON: {e}")
    #         self.notificar_erro(f"Erro ao ler o arquivo JSON. Verifique o arquivo e tente novamente.")
    #     except Exception as e:
    #         logging.error(f"Erro ao salvar e-mails localmente: {e}")
    #         self.notificar_erro(f"Erro inesperado ao salvar e-mails: {str(e)}")


    # def carregar_emails(self):
    #     """Carrega os e-mails do arquivo JSON e os exibe na tabela."""
    #     if os.path.exists(EMAILS_RECEBIDOS_PATH):
    #         try:
    #             with open(EMAILS_RECEBIDOS_PATH, 'r', encoding='utf-8') as f:
    #                 conteudo = f.read()
    #                 if conteudo.strip():  # Verifica se o arquivo não está vazio
    #                     emails = json.loads(conteudo)

    #                     # Decodifica e desencripta os campos sensíveis
    #                     for email in emails:
    #                         # Verifica se os campos são strings (como esperado) antes de processar
    #                         if isinstance(email["remetente"], str):
    #                             email["remetente"] = self.decriptar(base64.b64decode(email["remetente"]), self.fernet)
    #                         if isinstance(email["assunto"], str):
    #                             email["assunto"] = self.decriptar(base64.b64decode(email["assunto"]), self.fernet)
    #                         if isinstance(email["body"], str):
    #                             email["body"] = self.decriptar(base64.b64decode(email["body"]), self.fernet)
    #                         if isinstance(email["status"], str):
    #                             email["status"] = self.decriptar(base64.b64decode(email["status"]), self.fernet)

    #                     # Ordena os emails pela data (mais recentes primeiro)
    #                     emails.sort(
    #                         key=lambda x: datetime.strptime(x.get('data', ''), '%d-%m-%Y %H:%M:%S'),
    #                         reverse=True
    #                     )

    #                     self.exibir_emails(emails)
    #                 else:
    #                     print("Arquivo JSON vazio.")
    #                     self.exibir_emails([])  # Exibe uma lista vazia se o arquivo estiver vazio
    #         except (json.JSONDecodeError, OSError, ValueError, Exception) as e:
    #             logging.error(f"Erro ao carregar o arquivo JSON: {e}")
    #             QMessageBox.critical(self, "Erro", f"Não foi possível carregar os emails: {e}")
    #             print(f"Erro ao carregar o arquivo JSON: {e}")
    #     else:
    #         print(f"O arquivo {EMAILS_RECEBIDOS_PATH} não foi encontrado.")
    #         with open(EMAILS_RECEBIDOS_PATH, 'w', encoding='utf-8') as f:
    #             json.dump([], f)  # Cria um arquivo JSON vazio se não existir


    def receber_emails_do_servidor(self):
        """Recebe os e-mails via IMAP e retorna uma lista de e-mails."""
        emails_recebidos = []

        try:
            
            # Conectar ao servidor IMAP
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(SEU_EMAIL, SUA_SENHA)
            mail.select("inbox")

            # Procurar e-mails
            status, mensagens = mail.search(None, "ALL")
            if status != "OK":
                raise Exception("Erro ao procurar emails.")

            email_ids = mensagens[0].split()

            for email_id in email_ids[-10:]:  # Busca os últimos 10 e-mails
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                if status != "OK":
                    raise Exception(f"Erro ao buscar o email ID {email_id}")

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        remetente = decode_header(msg["From"])[0][0]
                        if isinstance(remetente, bytes):
                            remetente = remetente.decode('utf-8', errors='ignore')

                        assunto = decode_header(msg["Subject"])[0][0]
                        if isinstance(assunto, bytes):
                            assunto = assunto.decode('utf-8', errors='ignore')
                            

                        data = msg["Date"]
                        status_email = "Lido" if '\\Seen' in mail.fetch(email_id, '(FLAGS)')[1][0].decode() else "Não Lido"
                        
                        # Extraindo o corpo do e-mail
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))

                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    body = part.get_payload(decode=True).decode()  # Decodifica o conteúdo
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode()

                        emails_recebidos.append({
                            "id": email_id.decode(),
                            "remetente": remetente,
                            "assunto": assunto,
                            "data": data,
                            "status": status_email,
                            "body": body  # Adiciona o corpo ao dicionário
                        })

            mail.logout()
        except Exception as e:
            logging.error(f"Erro ao receber emails do servidor: {e}")
            print(f"Erro ao receber emails do servidor: {e}")

        return emails_recebidos

    def ajustar_formato_data(self, data_str):
        # Remove o nome do dia da semana em inglês
        data_str = re.sub(r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b', '', data_str)
        data_str = re.sub(r'\(.*\)', '', data_str).strip()  # Remove informações entre parênteses

        # Converte a data automaticamente
        try:
            dt_obj = parser.parse(data_str)
            return dt_obj.strftime('%d-%m-%Y %H:%M:%S')
        except ValueError as e:
            logging.error(f"Erro ao interpretar a data: {e}")
            return None

    # Ajuste na função que salva os emails localmente para usar o novo formato
    def obter_ou_gerar_chave(self):
        chave = os.getenv("CONFIG_KEY_EMAIL")
        if not chave:
            # Gerar uma nova chave
            chave = Fernet.generate_key().decode()
            # Salvar no .env
            set_key(self.dotenv_path, "CONFIG_KEY_EMAIL", chave)
        return chave
    
    def encriptar(self,campo, fernet):
        if campo:
            return fernet.encrypt(campo.encode('utf-8')).decode('utf-8')
        return ""


    def decriptar(self, campo, fernet):
        if campo:
            return fernet.decrypt(campo.encode('utf-8')).decode('utf-8')
        return ""
    

    def salvar_emails_localmente(self, novos_emails):
        """Salva novos e-mails no arquivo JSON local, encriptando campos sensíveis."""
        try:
            # Carrega a chave e inicializa o Fernet
            chave =  self.config_key
            fernet = Fernet(chave)

            emails_existentes = []
            if os.path.exists(EMAILS_RECEBIDOS_PATH):
                with open(EMAILS_RECEBIDOS_PATH, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                    if conteudo.strip():  # Verifica se o arquivo não está vazio
                        emails_existentes = json.loads(conteudo)

            # Extrai IDs e datas dos e-mails existentes para evitar duplicados
            ids_existentes = {(email["id"], email["data"]) for email in emails_existentes}

            # Filtra apenas os e-mails que ainda não estão no arquivo JSON
            emails_a_salvar = []
            for email in novos_emails:
                email["data"] = self.ajustar_formato_data(email["data"])
                email["status"] = email.get("status", "não lido")  # Define o status padrão como "não lido"

                if (email["id"], email["data"]) not in ids_existentes:
                    # Encripta os campos sensíveis
                    email["remetente"] = base64.b64encode(self.encriptar(email.get("remetente", ""), self.fernet)).decode("utf-8")
                    email["assunto"] = base64.b64encode(self.encriptar(email.get("assunto", ""), self.fernet)).decode("utf-8")
                    email["body"] = base64.b64encode(self.encriptar(email.get("body", ""), self.fernet)).decode("utf-8")
                    email["status"] = base64.b64encode(self.encriptar(email.get("status", ""), self.fernet)).decode("utf-8")
                    emails_a_salvar.append(email)

            # Adiciona apenas os novos e-mails
            if emails_a_salvar:
                emails_existentes.extend(emails_a_salvar)

                # Salvar de volta no arquivo JSON
                with open(EMAILS_RECEBIDOS_PATH, 'w') as f:
                    json.dump(emails_existentes, f, indent=4)
            else:
                print("Nenhum e-mail novo para salvar.")

        except Exception as e:
            logging.error(f"Erro ao salvar emails localmente: {e}")
            print(f"Erro ao salvar emails localmente: {e}")

    def atualizar_emails_json(self, novos_emails):
        """Atualiza o arquivo JSON com novos e-mails, evitando duplicatas e encriptando os dados sensíveis."""
        try:
            emails_existentes = []

            # Carregar e-mails existentes, se houver
            if os.path.exists(EMAILS_RECEBIDOS_PATH):
                with open(EMAILS_RECEBIDOS_PATH, 'r', encoding='utf-8') as f:
                    conteudo = f.read().strip()
                    if conteudo:
                        emails_existentes = json.loads(conteudo)

            ids_existentes = {(email.get("id"), email.get("data")) for email in emails_existentes}

            emails_a_salvar = []
            for email in novos_emails:
                email["data"] = self.ajustar_formato_data(email.get("data", ""))

                # Evitar duplicatas
                if (email.get("id"), email["data"]) not in ids_existentes:
                    # Encripta diretamente os campos sensíveis
                    email["remetente"] = self.encriptar(email.get("remetente", ""), self.fernet)
                    email["assunto"] = self.encriptar(email.get("assunto", ""), self.fernet)
                    email["body"] = self.encriptar(email.get("body", ""), self.fernet)
                    email["status"] = self.encriptar(email.get("status", ""), self.fernet)

                    emails_a_salvar.append(email)

            if emails_a_salvar:
                emails_existentes.extend(emails_a_salvar)
                with open(EMAILS_RECEBIDOS_PATH, 'w', encoding='utf-8') as f:
                    json.dump(emails_existentes, f, indent=4, ensure_ascii=False)
                print(f"{len(emails_a_salvar)} e-mail(s) novo(s) salvo(s).")
            else:
                print("Nenhum novo e-mail para atualizar no JSON.")

        except Exception as e:
            logging.error(f"Erro ao salvar e-mails: {e}")
            self.notificar_erro(f"Erro ao salvar e-mails: {e}")

    def carregar_emails(self):
        """Carrega os e-mails do arquivo JSON e os exibe na tabela."""
        if not os.path.exists(EMAILS_RECEBIDOS_PATH):
            print(f"O arquivo {EMAILS_RECEBIDOS_PATH} não foi encontrado.")
            with open(EMAILS_RECEBIDOS_PATH, 'w', encoding='utf-8') as f:
                json.dump([], f)
            self.exibir_emails([])
            return

        try:
            with open(EMAILS_RECEBIDOS_PATH, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                if not conteudo.strip():
                    print("O arquivo JSON está vazio.")
                    self.exibir_emails([])
                    return

                emails = json.loads(conteudo)
                emails_processados = []

                for email in emails:
                    try:
                        email["remetente"] = self.decriptar(email.get("remetente", ""), self.fernet)
                        email["assunto"] = self.decriptar(email.get("assunto", ""), self.fernet)
                        email["body"] = self.decriptar(email.get("body", ""), self.fernet)
                        email["status"] = self.decriptar(email.get("status", ""), self.fernet)

                        emails_processados.append(email)
                    except Exception as e:
                        logging.error(f"Erro ao processar e-mail: {e}")

                emails_processados.sort(
                    key=lambda x: datetime.strptime(x.get("data", ""), '%d-%m-%Y %H:%M:%S'),
                    reverse=True
                )
                self.exibir_emails(emails_processados)

        except json.JSONDecodeError as e:
            logging.error(f"Erro ao interpretar JSON: {e}")
            self.notificar_erro(f"Erro ao interpretar o arquivo JSON.")
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")
            self.notificar_erro(f"Erro inesperado ao carregar os e-mails.")

        
    def exibir_emails(self, emails):
        """Exibe os emails na tabela."""
        self.tabela_emails.setRowCount(len(emails))

        for row, email_data in enumerate(emails):
            # Adiciona checkbox à primeira coluna
            checkbox = QCheckBox()
            self.tabela_emails.setCellWidget(row, 0, checkbox)

            # Cria itens para as colunas relevantes
            remetente_item = QTableWidgetItem(email_data.get("remetente", ""))
            assunto_item = QTableWidgetItem(email_data.get("assunto", ""))
            data_item = QTableWidgetItem(self.ajustar_formato_data(email_data.get("data", "")))
            status_item = QTableWidgetItem(email_data.get("status", "Não Lido"))

            # Define os itens como não editáveis
            remetente_item.setFlags(remetente_item.flags() & ~Qt.ItemIsEditable)
            assunto_item.setFlags(assunto_item.flags() & ~Qt.ItemIsEditable)
            data_item.setFlags(data_item.flags() & ~Qt.ItemIsEditable)
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)

            # Adiciona os itens às células
            self.tabela_emails.setItem(row, 1, remetente_item)
            self.tabela_emails.setItem(row, 2, assunto_item)
            self.tabela_emails.setItem(row, 3, data_item)
            self.tabela_emails.setItem(row, 4, status_item)

            # Adiciona botões de ação na última coluna
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)

            # Botão Arquivar
            btn_arquivar = QPushButton()
            btn_arquivar.setIcon(QIcon("max/assets/icon/circular.png"))
            btn_arquivar.setToolTip("Arquivar")
            btn_arquivar.setCursor(QCursor(Qt.PointingHandCursor))
            btn_arquivar.clicked.connect(lambda _, e_id=email_data["id"]: self.acao_arquivar(e_id))

            # Botão Responder
            btn_responder = QPushButton()
            btn_responder.setIcon(QIcon("max/assets/icon/circular.png"))
            btn_responder.setToolTip("Responder")
            btn_responder.setCursor(QCursor(Qt.PointingHandCursor))
            btn_responder.clicked.connect(lambda _, e_id=email_data["id"]: self.acao_responder(e_id))

            # Botão Eliminar
            btn_eliminar = QPushButton()
            btn_eliminar.setIcon(QIcon("max/assets/icon/circular.png"))
            btn_eliminar.setToolTip("Eliminar")
            btn_eliminar.setCursor(QCursor(Qt.PointingHandCursor))
            btn_eliminar.clicked.connect(lambda _, e_id=email_data["id"]: self.acao_eliminar(e_id))

            # Botão Marcar como Lida
            btn_marcar_lida = QPushButton()
            btn_marcar_lida.setIcon(QIcon("max/assets/icon/circular.png"))
            btn_marcar_lida.setToolTip("Marcar como Lida")
            btn_marcar_lida.setCursor(QCursor(Qt.PointingHandCursor))
            btn_marcar_lida.clicked.connect(lambda _, e_id=email_data["id"]: self.acao_marcar_lida(e_id))

            # Adiciona os botões ao layout
            actions_layout.addWidget(btn_arquivar)
            actions_layout.addWidget(btn_responder)
            actions_layout.addWidget(btn_eliminar)
            actions_layout.addWidget(btn_marcar_lida)

            # Cria o widget que contém os botões e o insere na tabela
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.tabela_emails.setCellWidget(row, 5, actions_widget)

                    
    def abrir_detalhes_email(self, item):
        row = item.row()

        remetente = self.tabela_emails.item(row, 1).text()
        assunto = self.tabela_emails.item(row, 2).text()
        data = self.tabela_emails.item(row, 3).text()

        # Buscar o corpo do e-mail no JSON usando a data como identificador
        try:
            with open(EMAILS_RECEBIDOS_PATH, 'r', encoding='utf-8') as f:
                emails = json.load(f)
                # Localizar o e-mail pela data
                email_body = next(
                    (
                        self.decriptar(base64.b64decode(email["body"].encode("utf-8")), self.fernet)
                        for email in emails if email.get("data") == data
                    ),
                    "Corpo não disponível"
                )

                if isinstance(email_body, bytes):
                    email_body = email_body.decode('utf-8', errors='ignore')
        except Exception as e:
            logging.error(f"Erro ao abrir corpo do e-mail: {e}")
            email_body = "Erro ao carregar o corpo do e-mail."

        # Abrir o modal com os detalhes do e-mail
        dialog = EmailDetalhesDialog(remetente, assunto, data, email_body, self)
        dialog.exec()


    def atualizar_emails(self):
        """Método exposto para sincronizar e-mails ao ser chamado de fora da classe."""
        self.sincronizar_emails()
        
    def notificar_sucesso(self, mensagem):
        QMessageBox.information(self, "Sucesso", mensagem)

    def notificar_erro(self, mensagem):
        QMessageBox.critical(self, "Falha", mensagem)
    # Método público para ser chamado de fora da classe

class EmailDetalhesDialog(QDialog):
    def __init__(self, remetente, assunto, data, body, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalhes do E-mail")
        self.setFixedSize(900, 600)  # Ajuste o tamanho conforme necessário
        self.setWindowIcon(QIcon("max/assets/icon/circular.png"))  # Ícone da janela

        # Estilo do fundo da janela
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(0, 21, 42, 180);  /* Cor de fundo do modal */
                border-radius: 10px;
            }
            QLabel {
                color: #2496be;  /* Cor das labels */
                font-weight: bold;
            }
            QTextEdit {
                color: white;
                background-color: rgba(0, 21, 42, 150);
                border: 1px solid #2496be;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                color: white;
                background-color: #2496be;
                border-radius: 5px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e7ea1;
            }
        """)

        # Layout para os detalhes do e-mail
        layout = QVBoxLayout()

        # Rótulos para as informações do e-mail
        layout.addWidget(QLabel(f"Remetente: {remetente}"))
        layout.addWidget(QLabel(f"Assunto: {assunto}"))
        layout.addWidget(QLabel(f"Data: {data}"))

        # Texto do corpo do e-mail
        body_text = QTextEdit()
        body_text.setText(body)
        body_text.setReadOnly(True)  # Apenas leitura
        layout.addWidget(body_text)

        # Botão para fechar
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.accept)
        layout.addWidget(btn_fechar)

        # Definir layout
        self.setLayout(layout)

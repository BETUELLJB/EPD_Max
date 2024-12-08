from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                               QPushButton, QHBoxLayout, QComboBox, QScrollArea, QMessageBox, QSizePolicy)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont
import google.generativeai as genai
from config.config import BASE_DIR_Log_Main
import threading
import openai
import os
from datetime import datetime
import traceback

class Chat(QWidget):
    resposta_recebida = Signal(str)  # Sinal para atualizar a interface com a resposta do assistente
    sinal_erro_conexao = Signal()  # Sinal para mostrar erro de conexão

    def __init__(self, BASE_DIR_Log_Main=BASE_DIR_Log_Main):
        super().__init__()

        # Configuração das APIs
        openai_key = "SUA_CHAVE_API_OPENAI"
        google_api_key = "AIzaSyD339SNnqvBhRpxCWL9Ln5WVcOQzQptufY"
        openai.api_key = openai_key
        genai.configure(api_key=google_api_key)
        
        if not os.path.exists(BASE_DIR_Log_Main):
            os.makedirs(BASE_DIR_Log_Main)
        self.log_file = os.path.join(BASE_DIR_Log_Main, "Logs_Chat.log")
         
        # Interface do usuário
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: transparent;")  # Fundo azul escuro
       
        # Área do chat com barra de rolagem
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.widget_scroll = QWidget()
        self.layout_chat = QVBoxLayout(self.widget_scroll)
        self.scroll_area.setWidget(self.widget_scroll)
        self.scroll_area.setStyleSheet("background-color: none; border-radius: 8px;")

        self.entrada_texto = QLineEdit()
        self.entrada_texto.setPlaceholderText("Digite sua pergunta...")
        self.entrada_texto.setFont(QFont("Times New Roman", 12))
        self.entrada_texto.setStyleSheet("""
            background-color: #2e2e2e;
            color: white;
            font-size: 14px;
            font-weight: bold;
            border-radius: 8px;
            border: 1px solid #2496be; 
            padding: 10px;

        """)
        self.entrada_texto.returnPressed.connect(self.enviar_pergunta)

        self.botao_enviar = QPushButton("Enviar")
        self.botao_enviar.setFont(QFont("Times New Roman", 12))
        self.botao_enviar.setStyleSheet("""
            background-color: #2e2e2e;
            color: #2496be;
            font-size: 14px;
            font-weight: bold;
            border-radius: 10px;
            border: 1px solid #2496be; 
            padding: 10px;
        """)
        self.botao_enviar.clicked.connect(self.enviar_pergunta)

        # ComboBox para escolher a API
        self.selecao_api = QComboBox()
        self.selecao_api.setStyleSheet("""
            padding: 8px;
            font-size: 12px;
            background-color: #2e2e2e;
            color: white;
            border-radius: 8px;
            border: 1px solid #2496be;
        """)
        self.selecao_api.addItems(["Google Gemini", "OpenAI"])

        layout_entrada = QHBoxLayout()
        layout_entrada.addWidget(self.entrada_texto)
        layout_entrada.addWidget(self.botao_enviar)

        layout.addWidget(self.scroll_area)
        layout.addWidget(self.selecao_api)
        layout.addLayout(layout_entrada)

        self.setLayout(layout)

        # Conectar os sinais
        self.sinal_erro_conexao.connect(self.mostrar_erro_conexao)
        self.resposta_recebida.connect(self.atualizar_chat_assistente)
     
    def enviar_pergunta(self):
        pergunta = self.entrada_texto.text().strip()
        if pergunta:
            self.atualizar_chat_usuario(f"Usuário: {pergunta}")
            self.entrada_texto.clear()
            threading.Thread(target=self.obter_resposta, args=(pergunta,), daemon=True).start()

    @Slot(str)
    def atualizar_chat_usuario(self, mensagem):
        widget_usuario = QLabel(mensagem)
        widget_usuario.setFont(QFont("Times New Roman", 12))
        widget_usuario.setStyleSheet("""
            background-color: #2e2e2e;
            color: white;
            font-size: 14px;
            border-radius: 8px;
            padding: 5px;
            margin: 2px;
        """)
        widget_usuario.setWordWrap(True)
        self.layout_chat.addWidget(widget_usuario)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    @Slot(str)
   
    def atualizar_chat_assistente(self, mensagem):
        try:
            # Widget para a mensagem do assistente
            widget_assistente = QWidget()
            layout_assistente = QHBoxLayout(widget_assistente)

            # Caixa de resposta com QLabel para ajustar automaticamente
            caixa_resposta = QLabel()
            caixa_resposta.setText(mensagem)
            caixa_resposta.setWordWrap(True)  # Permite quebra de linha automática
            caixa_resposta.setFont(QFont("Times New Roman", 12))

            # Estilização para a caixa de resposta
            caixa_resposta.setStyleSheet("""
                QLabel {
                    background-color: #2e2e2e;  /* Fundo cinza escuro */
                    color: white;  /* Texto branco */
                    fonte-size: 14px;
                    padding: 8px;
                    margin: 2px;
                    border-radius: 8px;
                    border: 1px solid #2496be;
                }
            """)

            # Configurando tamanho dinâmico
            caixa_resposta.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            # Adicionando ao layout
            layout_assistente.addWidget(caixa_resposta)
            layout_assistente.setAlignment(Qt.AlignRight)
            self.layout_chat.addWidget(widget_assistente)

            # Scroll para o fim da área de chat
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro: {str(e)}")

    def closeEvent(self, event):
        if self.thread_voz.is_alive():
            self.thread_voz.join(timeout=1)
        event.accept()

    def obter_resposta(self, pergunta):
        try:
            api_escolhida = self.selecao_api.currentText()
            if api_escolhida == "OpenAI":
                resposta = self.consultar_openai(pergunta)
                self.resposta_recebida.emit(resposta)
            elif api_escolhida == "Google Gemini":
                resposta = self.consultar_gemini(pergunta)
                self.resposta_recebida.emit(resposta)
        except Exception:
            self.sinal_erro_conexao.emit()

    def consultar_openai(self, pergunta):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Você é um assistente virtual."}, {"role": "user", "content": pergunta}],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()

    def consultar_gemini(self, pergunta):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(pergunta)
            return response.text.strip()
        except genai.ApiException as e:
            self.log_erro(f"Erro na API Google Gemini: {e}")
            return "Houve um problema ao conectar com o Google Gemini."
        except Exception as e:
            self.log_erro(f"Erro inesperado: {e}")
            return "Ocorreu um erro desconhecido ao acessar o Google Gemini."

    @Slot()
    def mostrar_erro_conexao(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Erro de Conexão")
        msg_box.setText("Não foi possível conectar à Internet. Verifique sua conexão e tente novamente.")
        msg_box.exec()
        
      
    def log_erro(self, mensagem):
        """Registra mensagens de erro no arquivo de log com traceback completo."""
        try:
            
            with open(self.log_file, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - ERROR - {mensagem}\n")
                # Adiciona o traceback completo se houver uma exceção ativa
                log_file.write(traceback.format_exc() + "\n")
        except Exception as e:
           self.log_erro(f"Erro ao registrar log: {e}")    
   
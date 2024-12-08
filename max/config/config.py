from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton, QLabel, QFileDialog, QMessageBox

from datetime import datetime
import traceback
import os

# Clima
cidade_atual = "Chongoene"

BASE_DIR_Calendario = "B:\\Estudos\\Projetos\\Python\\Max\\max\\pages\\Tasks\\calendario"
BASE_DIR_Email      = "B:\\Estudos\\Projetos\\Python\\Max\\max\\pages\\Email\\Gestor_Email"
BASE_DIR_Config     = "B:\\Estudos\\Projetos\\Python\\Max\\max\\config"


BASE_DIR_Log_Main  = "B:\\Estudos\\Projetos\\Python\\Max\\max\\Logs_Main"
LOG_DIR_Email      = "B:\\Estudos\\Projetos\\Python\\Max\\max\\pages\\Email\\Gestor_Email\\Logs"
LOG_DIR_Calendario = "B:\\Estudos\\Projetos\\Python\\Max\\max\\pages\\Tasks\\Logs"

Pastas_Email = {
    "enviados": "enviados",
    "recebidos": "recebidos",
    "rascunhos": "rascunhos",
    "lixeira": "lixeira"
}
Pastas_Calendario = {
    "eventos": "eventos",
    "tarefas": "tarefas"
}

def pastas_calendario(self):
    """Cria a estrutura de pastas se não existir."""
    try:
       
        if not os.path.exists(BASE_DIR_Calendario):
            os.makedirs(BASE_DIR_Calendario)

        for pasta in Pastas_Calendario.values():
            caminho = os.path.join(BASE_DIR_Calendario, pasta)
            os.makedirs(caminho, exist_ok=True)     
    except Exception as e:
       log_erro(f"Erro ao inicializar as pastas de Calendário: {e}")

def pastas_email(self):
    """Cria a estrutura de pastas se não existir."""
    try:
        if not os.path.exists(BASE_DIR_Email):
            os.makedirs(BASE_DIR_Email)  # Cria a pasta principal

        for pasta in Pastas_Email.values():
            caminho = os.path.join(BASE_DIR_Email, pasta)
            os.makedirs(caminho, exist_ok=True)  # Cria cada subpasta
    except Exception as e:
        log_erro(f"Erro ao inicializar as pastas de e-mail: {e}")
        
def log_erro(self, mensagem):
        """Registra mensagens de erro no arquivo de log com traceback completo."""
        try:
            if not os.path.exists(BASE_DIR_Log_Main ):
                os.makedirs(BASE_DIR_Log_Main )
            self.log_file = os.path.join(BASE_DIR_Log_Main, "Logs_Main.log")
            
            with open(self.log_file, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - ERROR - {mensagem}\n")
                # Adiciona o traceback completo se houver uma exceção ativa
                log_file.write(traceback.format_exc() + "\n")
        except Exception as e:
            print(f"Erro ao registrar log: {e}")  

def notificar_sucesso(self, mensagem):
        QMessageBox.information(self, "Sucesso", mensagem)

def notificar_erro(self, mensagem):
        QMessageBox.critical(self, "Erro", mensagem)
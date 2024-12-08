from PySide6.QtCore import QObject, Signal
from config.config import BASE_DIR_Log_Main
import time
import speech_recognition as sr
import pyttsx3
from datetime import datetime
import traceback
import json
import os

class Sylla(QObject):
    fala_detectada = Signal(str)  # Sinal para enviar o texto reconhecido

    def __init__(self, BASE_DIR_Log_Main=BASE_DIR_Log_Main):
        super().__init__()
        # Inicializa pastas e logs
        if not os.path.exists(BASE_DIR_Log_Main):
            os.makedirs(BASE_DIR_Log_Main)
        self.log_file = os.path.join(BASE_DIR_Log_Main, "Logs_Fala.log")
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump([], f)

        self.recognizer = sr.Recognizer()
        self.continuar_escutando = True
        self.engine = pyttsx3.init()
        self.engine_lock = False
        self.configurar_voz()

        # Configurações adicionais
        self.nivel_energia = 300  # Nível mínimo de energia para capturar fala

    def configurar_voz(self):
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)
        for voice in self.engine.getProperty('voices'):
            if "pt" in voice.languages:
                self.engine.setProperty('voice', voice.id)
                break

    def iniciar_reconhecimento(self):
        try:
            with sr.Microphone() as source:
                print("Configurando microfone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.recognizer.energy_threshold = self.nivel_energia
                print(f"Nível de energia ajustado para: {self.recognizer.energy_threshold}")

                while self.continuar_escutando:
                    if not self.engine_lock:
                        try:
                            print("Aguardando fala...")
                            audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=6)
                            print("Processando áudio...")
                            resultado = self.recognizer.recognize_google(audio, language="pt-BR")
                            if resultado:
                                print(f"Você: {resultado}")
                                self.fala_detectada.emit(resultado)
                        except sr.UnknownValueError:
                            print("Google não conseguiu entender o áudio")
                            self.log_erro("Google não conseguiu entender o áudio")
                        except sr.RequestError as e:
                            erro_msg = f"Erro ao se conectar ao Google: {e}"
                            print(erro_msg)
                            self.log_erro(erro_msg)
                        except Exception as e:
                            erro_msg = f"Erro inesperado: {str(e)}"
                            self.log_erro(erro_msg)
                        time.sleep(1)  # Pausa para evitar sobrecarga
        except Exception as e:
            erro_msg = f"Erro ao inicializar o microfone: {str(e)}"
            print(erro_msg)
            self.log_erro(erro_msg)

    def fala(self, texto):
        self.engine_lock = True
        try:
            self.engine.say(texto)
            self.engine.runAndWait()
        except Exception as e:
            erro_msg = f"Erro na síntese de fala: {str(e)}"
            print(erro_msg)
            self.log_erro(erro_msg)
        finally:
            self.engine_lock = False

    def parar_reconhecimento(self):
        self.continuar_escutando = False

    def log_erro(self, mensagem):
        """Registra mensagens de erro no arquivo de log com traceback completo."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - ERROR - {mensagem}\n")
                log_file.write(traceback.format_exc() + "\n")
        except Exception as e:
            print(f"Erro ao registrar log: {e}")

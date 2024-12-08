import pyaudio
import wave
from faster_whisper import WhisperModel
import datetime
import os
import pyttsx3  # Biblioteca para síntese de voz

class AssistenteVirtual:
    def __init__(self, modelo_caminho, taxa_amostragem=16000, duracao_gravacao=5, audio_path="comando.wav"):
        # Inicializa o modelo de reconhecimento de fala e configurações
        try:
            self.model = WhisperModel(modelo_caminho)  # Carrega o modelo no início
            print("Modelo Whisper carregado com sucesso.")
        except Exception as e:
            print(f"Erro ao carregar o modelo Whisper: {e}")
            raise e  # Interrompe a execução se o modelo não carregar
        
        # Configurações de gravação de áudio
        self.taxa_amostragem = taxa_amostragem
        self.duracao_gravacao = duracao_gravacao
        self.audio_format = pyaudio.paInt16
        self.chunk_size = 1024
        self.channels = 1
        self.audio_path = audio_path
        
        # Inicializa o motor de síntese de voz
        self.engine = pyttsx3.init()

    def falar(self, texto):
        """Faz o assistente falar o texto fornecido."""
        self.engine.say(texto)
        self.engine.runAndWait()

    def gravar_audio(self, nome_arquivo=None):
        """Grava o áudio do microfone e salva em um arquivo WAV."""
        if nome_arquivo is None:
            nome_arquivo = self.audio_path  # Usa um nome padrão se não fornecido
        
        p = pyaudio.PyAudio()
        try:
            stream = p.open(format=self.audio_format, channels=self.channels, 
                            rate=self.taxa_amostragem, input=True, 
                            frames_per_buffer=self.chunk_size)
        except Exception as e:
            print(f"Erro ao abrir o stream de áudio: {e}")
            p.terminate()
            return
        
        print("Gravando áudio...")
        frames = []
        try:
            for _ in range(0, int(self.taxa_amostragem / self.chunk_size * self.duracao_gravacao)):
                data = stream.read(self.chunk_size)
                frames.append(data)
        except Exception as e:
            print(f"Erro durante a gravação: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

        # Salvar a gravação como arquivo WAV
        try:
            with wave.open(nome_arquivo, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(p.get_sample_size(self.audio_format))
                wf.setframerate(self.taxa_amostragem)
                wf.writeframes(b''.join(frames))
            print(f"Gravação salva em {nome_arquivo}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo de áudio: {e}")

    def transcrever_audio(self, nome_arquivo=None):
        """Transcreve o áudio usando o modelo Whisper."""
        if nome_arquivo is None:
            nome_arquivo = self.audio_path  # Usa o arquivo padrão

        # Verifica se o arquivo de áudio existe
        if not os.path.exists(nome_arquivo):
            print(f"Arquivo de áudio {nome_arquivo} não encontrado.")
            return ""

        print("Transcrevendo áudio...")
        try:
            segments, _ = self.model.transcribe(nome_arquivo)
            transcricao = ""
            for segment in segments:
                transcricao += f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}\n"
            return transcricao.strip()
        except Exception as e:
            print(f"Erro durante a transcrição: {e}")
            return ""

    def processar_comando(self, comando):
        """Processa o comando transcrito e executa ações."""
        if 'horas' in comando:
            agora = datetime.datetime.now().strftime("%H:%M")
            resposta = f"Agora são {agora}"
            print(resposta)
            self.falar(resposta)
        elif 'sair' in comando:
            print("Encerrando o assistente. Até logo!")
            self.falar("Encerrando o assistente. Até logo!")
            return False
        else:
            resposta = f"Comando não reconhecido: {comando}"
            print(resposta)
            self.falar(resposta)
        return True

    def iniciar(self):
        """Inicia o loop do assistente virtual."""
        ativo = True
        while ativo:
            self.gravar_audio()  # Grava o áudio
            comando = self.transcrever_audio()  # Transcreve o áudio
            if comando:
                print(f"Você disse: {comando}")
                ativo = self.processar_comando(comando)  # Processa o comando
            else:
                print("Nenhum comando detectado.")

# Caminho para o modelo Whisper
caminho_modelo = "B:/Estudos/Projetos/Python/Max/max/model/Systran"

# Executando o assistente
if __name__ == '__main__':
    try:
        assistente = AssistenteVirtual(modelo_caminho=caminho_modelo)
        assistente.iniciar()
    except Exception as e:
        print(f"Erro ao iniciar o assistente virtual: {e}")

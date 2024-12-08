import pyaudio
import wave
from faster_whisper import WhisperModel
import datetime
import os


class AssistenteVirtual:
    def __init__(self, modelo_caminho, taxa_amostragem=16000, duracao_gravacao=5):
        # Inicializa o modelo de reconhecimento de fala e configurações
        self.model = WhisperModel(modelo_caminho, device="cpu", compute_type="int8")  # Carrega o modelo no início
        self.taxa_amostragem = taxa_amostragem
        self.duracao_gravacao = duracao_gravacao
        self.audio_format = pyaudio.paInt16
        self.chunk_size = 1024
        self.channels = 1
        self.audio_path = "comando.wav"

    def gravar_audio(self, nome_arquivo=None):
        """Grava o áudio do microfone e salva em um arquivo WAV."""
        if nome_arquivo is None:
            nome_arquivo = self.audio_path  # Usa um nome padrão se não fornecido
        
        p = pyaudio.PyAudio()
        stream = p.open(format=self.audio_format, channels=self.channels, 
                        rate=self.taxa_amostragem, input=True, 
                        frames_per_buffer=self.chunk_size)

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
        with wave.open(nome_arquivo, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(self.audio_format))
            wf.setframerate(self.taxa_amostragem)
            wf.writeframes(b''.join(frames))

        print(f"Gravação salva em {nome_arquivo}")

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
            print(f"Agora são {agora}")
        elif 'sair' in comando:
            print("Encerrando o assistente. Até logo!")
            return False
        elif 'olá tudo bem' in comando:
            print("Oi estou bem e o senhor?")
            return False
        elif 'bom dia' in comando:
            print("Bom dia senhor! Como estas?")
            return False
        elif 'boa tarde' in comando:
            print("Boa tarde senhor! Como estas?")
            return False
        elif 'boa noite' in comando:
            print("Boa noite senhor! Como estas?")
            return False
        else:
            print(f"Comando não reconhecido: {comando}")
        return True

    def iniciar(self):
        """Inicia o loop do assistente virtual."""
        ativo = True
        while ativo:
            self.gravar_audio()  # Grava o áudio
            comando = self.transcrever_audio()  # Transcreve o áudio
            print(f"Você disse: {comando}")
            ativo = self.processar_comando(comando)  # Processa o comando

# Caminho para o modelo Whisper
caminho_modelo = "B:\\Estudos\\Projetos\\Python\\Max\\max\\model\\models--Systran--faster-whisper-large-v3\\snapshots\\edaa852ec7e145841d8ffdb056a99866b5f0a478"

# Executando o assistente
if __name__ == '__main__':
    assistente = AssistenteVirtual(modelo_caminho=caminho_modelo)
    assistente.iniciar()



import os
from faster_whisper import WhisperModel

# Definir o diretório onde o modelo está armazenado localmente
model_path = "B:\\Estudos\\Projetos\\Python\\Max\\max\\model\\models--Systran--faster-whisper-large-v3\\snapshots\\edaa852ec7e145841d8ffdb056a99866b5f0a478"

# Executar no CPU com quantização INT8
print('Carregando o modelo local...')
model = WhisperModel(model_path, device="cpu", compute_type="int8")

# Transcrever o arquivo de áudio (ajuste o caminho para o áudio armazenado localmente)
audio_path = "B:\\Estudos\\Projetos\\Python\\Max\\max\\assets\\audio\\teste.wav"
print('Transcrendo...')
segments, info = model.transcribe(audio_path, beam_size=5)

# Exibir a linguagem detectada e sua probabilidade
print("Linguagem detectada '%s' com probabilidade %f" % (info.language, info.language_probability))

# Exibir a transcrição de cada segmento de áudio
print('Exibindo os resultados...')
for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

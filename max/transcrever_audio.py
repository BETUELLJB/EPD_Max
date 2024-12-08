import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import soundfile as sf
import librosa
import os
import string

# Função para remover pontuação
def remove_pontuacao(text):
    return text.translate(str.maketrans('', '', string.punctuation))

# Definir dispositivo
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# Caminho do modelo local
model_path = r"B:\\Estudos\\Projetos\\Python\\Max\\max\\model\\whisper"

# Carregar modelo e processador do caminho local
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_path, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_path)

# Pipeline de reconhecimento automático de fala
pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
)

# Verificar se o arquivo de áudio existe
audio_file = r"B:\\Estudos\\Projetos\\Python\\Max\\max\\assets\\audio\\teste.wav"  # Substitua pelo caminho do seu arquivo de áudio local
if not os.path.exists(audio_file):
    raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_file}")

try:
    # Carregar áudio local
    audio_input, sample_rate = sf.read(audio_file)

    # Converter para mono (um único canal), se necessário
    if len(audio_input.shape) > 1:  # Se for estéreo, converte para mono
        audio_input = librosa.to_mono(audio_input.T)

    # Passar o áudio para a pipeline
    result = pipe({"array": audio_input, "sampling_rate": sample_rate})

    # Remover pontuação do texto transcrito
    texto_sem_pontuacao = remove_pontuacao(result["text"])

    # Exibir o texto transcrito sem pontuação
    print("Texto transcrito (sem pontuação):")
    print(texto_sem_pontuacao)

except Exception as e:
    print(f"Erro ao processar o áudio: {e}")

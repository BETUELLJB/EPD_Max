from transformers import AutoModel, AutoTokenizer
import torch
import numpy as np

# Inicializar o modelo e o tokenizer
model = AutoModel.from_pretrained("jinaai/jina-embeddings-v3", trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained("jinaai/jina-embeddings-v3", trust_remote_code=True)

# Lista de comandos
comandos = [
    "Abrir navegador",
    "Mostrar previsão do tempo",
    "Enviar e-mail",
    "Tocar uma música",
    "Definir um lembrete",
    "Pesquisar no Google",
    "Fechar aplicativo opera mini"
]

# Função para obter embeddings
def obter_embeddings(textos):
    tokens = tokenizer(textos, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        embeddings = model(**tokens).last_hidden_state.mean(dim=1)
    return embeddings

# Obter embeddings dos comandos
embeddings_comandos = obter_embeddings(comandos)

# Função para interpretar o comando do usuário
def interpretar_comando(usuario_texto):
    embedding_usuario = obter_embeddings([usuario_texto])[0]
    similaridades = [torch.cosine_similarity(embedding_usuario.unsqueeze(0), emb_com.unsqueeze(0)).item() for emb_com in embeddings_comandos]
    indice_comando = np.argmax(similaridades)
    return comandos[indice_comando]

# Teste com um comando do usuário
usuario_texto = " tudo bem max? peco terminar o aplicativo agora"
comando_predito = interpretar_comando(usuario_texto)
print(f"Comando Interpretado: {comando_predito}")

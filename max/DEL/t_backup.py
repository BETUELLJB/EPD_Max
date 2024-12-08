import json
import os
import sys
from PySide6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit,
    QPushButton, QWidget, QLabel, QDialog, QFormLayout, QMessageBox
)
from PySide6.QtGui import QIcon
from transformers import pipeline, AutoTokenizer

model_name = "deepset/xlm-roberta-large-squad2"
try:
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
    nlp = pipeline("question-answering", model=model_name, tokenizer=tokenizer)

    print("Modelo carregado com sucesso!!!")
except Exception as e:
    print(f"Erro ao carregar o modelo: {e}")
    sys.exit(1)

# Arquivos JSON
arquivo_contextos = 'B:\\Estudos\\Projetos\\Python\\Max\\max\\DEL\\contextos.json'
arquivo_interacoes = 'B:\\Estudos\\Projetos\\Python\\Max\\max\\DEL\\interacoes.json'

class QAModeloApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.verificar_arquivos()

    # Função para verificar e criar arquivos JSON vazios, se não existirem
    def verificar_arquivos(self):
        try:
            if not os.path.exists(arquivo_contextos):
                with open(arquivo_contextos, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=4)

            if not os.path.exists(arquivo_interacoes):
                with open(arquivo_interacoes, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Erro ao verificar/criar arquivos JSON: {e}")

    # Função para salvar um novo contexto no JSON
    def salvar_contexto(self, categoria, contexto):
        try:
            with open(arquivo_contextos, 'r', encoding='utf-8') as f:
                contextos = json.load(f)

            novo_contexto = {
                "categoria": categoria,
                "contexto": contexto
            }

            contextos.append(novo_contexto)

            with open(arquivo_contextos, 'w', encoding='utf-8') as f:
                json.dump(contextos, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Erro ao salvar contexto: {e}")

    # Função para salvar uma nova interação no JSON
    def salvar_interacao(self, categoria, pergunta, resposta, score):
        try:
            with open(arquivo_interacoes, 'r', encoding='utf-8') as f:
                interacoes = json.load(f)

            nova_interacao = {
                "categoria": categoria,
                "pergunta": pergunta,
                "resposta": resposta,
                "score": score
            }

            interacoes.append(nova_interacao)

            with open(arquivo_interacoes, 'w', encoding='utf-8') as f:
                json.dump(interacoes, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Erro ao salvar interação: {e}")

    # Função para consultar uma resposta no JSON
    def consultar_resposta(self, pergunta):
        try:
            with open(arquivo_interacoes, 'r', encoding='utf-8') as f:
                interacoes = json.load(f)

            for interacao in interacoes:
                if interacao['pergunta'].lower() == pergunta.lower():
                    return interacao['resposta'], interacao['score']
        except Exception as e:
            print(f"Erro ao consultar interações: {e}")

        return None, 0

    # Função para buscar a resposta no modelo usando todos os contextos
    def buscar_resposta_no_modelo(self, pergunta):
        try:
            with open(arquivo_contextos, 'r', encoding='utf-8') as f:
                contextos = json.load(f)

            melhor_resposta = None
            melhor_score = 0
            melhor_categoria = None

            for item in contextos:
                contexto = item.get('contexto')
                categoria = item.get('categoria', 'geral')
                if not contexto:
                    continue

                try:
                    resultado = nlp(question=pergunta, context=contexto)
                    score = resultado['score']

                    if score > melhor_score:
                        melhor_resposta = resultado['answer']
                        melhor_score = score
                        melhor_categoria = categoria

                except Exception as e:
                    print(f"Erro ao realizar a pesquisa com o modelo: {e}")

            return melhor_categoria, melhor_resposta, round(melhor_score, 4)
        except Exception as e:
            print(f"Erro ao carregar os contextos: {e}")
            return None, None, 0

    # Função principal para realizar perguntas
    def realizar_pergunta(self, pergunta):
        if not pergunta.strip():
            return "Pergunta inválida!"

        resposta, score = self.consultar_resposta(pergunta)

        if resposta:
            return f"Histórico: '{resposta}', Score: {score}"
        else:
            categoria, resposta, score = self.buscar_resposta_no_modelo(pergunta)
            if resposta:
                self.salvar_interacao(categoria, pergunta, resposta, score)
                return f"Modelo: '{resposta}', Score: {score}"
            else:
                return "Não foi possível encontrar uma resposta."

    def enviar_pergunta(self):
        pergunta = self.campo_pergunta.text().strip()
        resposta = self.realizar_pergunta(pergunta)
        self.area_resposta.setText(resposta)
        self.campo_pergunta.clear()

    def abrir_modal_contexto(self):
        modal = AdicionarContextoModal(self)
        modal.exec()


    def init_ui(self):
        self.setWindowTitle("Agente")
        self.setGeometry(190, 40, 1000, 600)
        self.setWindowIcon(QIcon("max/assets/icon/circular.png"))

        layout_principal = QVBoxLayout()
        layout_input = QHBoxLayout()
        layout_botoes = QHBoxLayout()

        self.area_resposta = QTextEdit()
        self.area_resposta.setReadOnly(True)
        self.campo_pergunta = QLineEdit()
        self.botao_enviar = QPushButton("Enviar")
        self.botao_enviar.clicked.connect(self.enviar_pergunta)

        self.botao_adicionar_contexto = QPushButton("Adicionar Contexto")
        self.botao_adicionar_contexto.clicked.connect(self.abrir_modal_contexto)

        layout_input.addWidget(self.campo_pergunta)
        layout_input.addWidget(self.botao_enviar)
        layout_botoes.addWidget(self.botao_adicionar_contexto)

        layout_principal.addWidget(QLabel("Resposta:"))
        layout_principal.addWidget(self.area_resposta)
        layout_principal.addLayout(layout_input)
        layout_principal.addLayout(layout_botoes)

        self.setLayout(layout_principal)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = QAModeloApp()
    janela.show()
    sys.exit(app.exec())
    
    
# Modal para adicionar contexto
# Modal para adicionar contexto
class AdicionarContextoModal(QDialog):
    def __init__(self, app_instance):
        super().__init__()
        self.app_instance = app_instance  # Instância da classe QAModeloApp
        self.setWindowTitle("Adicionar Contexto")
        self.setGeometry(300, 300, 400, 200)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.campo_categoria = QLineEdit()
        self.campo_categoria.setPlaceholderText("Digite a categoria")
        self.campo_contexto = QTextEdit()
        self.campo_contexto.setPlaceholderText("Digite o contexto")

        botao_salvar = QPushButton("Salvar")
        botao_salvar.clicked.connect(self.salvar_contexto)

        layout.addRow("Categoria:", self.campo_categoria)
        layout.addRow("Contexto:", self.campo_contexto)
        layout.addWidget(botao_salvar)

        self.setLayout(layout)

    def salvar_contexto(self):
        categoria = self.campo_categoria.text().strip()
        contexto = self.campo_contexto.toPlainText().strip()

        if not categoria or not contexto:
            QMessageBox.warning(self, "Erro", "Categoria e Contexto são obrigatórios!")
            return

        # Acessando o método salvar_contexto da instância da classe principal
        self.app_instance.salvar_contexto(categoria, contexto)
        QMessageBox.information(self, "Sucesso", "Contexto salvo com sucesso!")
        self.accept()

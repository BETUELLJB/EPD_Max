from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PySide6.QtGui import QPalette, QBrush, QPixmap, QIcon, QColor, QPainter, QCursor
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEvent,QTimer, QObject, QThread, Signal

from pages.gestor_tarefa.gestor_tarefa import Tarefa
from pages.Email.gestor_email import EmailDashboard
from pages.home import Home
from pages.comando import Comando
from pages.configuracao import Configuracao
from max1 import Sylla
import sys
import subprocess
import pyautogui
import time
import webbrowser
import subprocess
import re


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Assistente Virtual")
        self.setGeometry(190, 40, 1000, 600)

        # Definindo o ícone da aplicação
        self.setWindowIcon(QIcon("max/assets/icon/circular.png"))
        
        
        # Adicione um atributo de temporizador
        self.temporizador_atualizacao = QTimer(self)
        self.temporizador_atualizacao.timeout.connect(self.atualizar_interface)
        self.temporizador_atualizacao.start(180000)  # Exemplo: atualização a cada 1 segundo
        
        # Inicializar a thread de reconhecimento de fala
        self.thread_reconhecimento = QThread()
        self.reconhecimento_fala = Sylla()
        self.reconhecimento_fala.moveToThread(self.thread_reconhecimento)
        self.modo_pesquisa = None  # Variável para armazenar o tipo de pesquisa selecionado

        # Conectar sinais e slots
        self.reconhecimento_fala.fala_detectada.connect(self.processar_fala)
        self.thread_reconhecimento.started.connect(self.reconhecimento_fala.iniciar_reconhecimento)

        # Iniciar a thread de reconhecimento de fala
        self.thread_reconhecimento.start()

        # Definindo o layout principal (horizontal)
        main_layout = QHBoxLayout()

        # Adicionando a parte central
        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_layout)
        main_layout.addWidget(self.central_widget)

        # Adicionando um QLabel na parte central
        self.label_conteudo = QLabel("Conteúdo do Assistente Aqui")
        self.label_conteudo.setAlignment(Qt.AlignCenter)
        self.label_conteudo.setStyleSheet("font-size: 18px; color: white;")
        self.central_layout.addWidget(self.label_conteudo)

        # Adicionando a sidebar
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)
        self.sidebar.setFixedWidth(50)  # Oculta a sidebar inicialmente (mostrando apenas os ícones)
        self.sidebar.setAutoFillBackground(True)
        self.sidebar.setStyleSheet("background-color: rgba(0, 21, 42, 180); margin: 0; padding: 0;")
        main_layout.addWidget(self.sidebar)

        # Adicionando botões à sidebar
        self.botoes = self.criar_botoes_sidebar()

        # Conectar eventos de mouse para a sidebar
        self.sidebar.installEventFilter(self)  # Adiciona um filtro de evento para a sidebar

        # Configurando o widget central
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Definindo o fundo da janela
        self.definir_fundo()

    def resizeEvent(self, event):
        """Evento que redimensiona o fundo ao redimensionar a janela."""
        self.definir_fundo()
        super().resizeEvent(event)

    def atualizar_interface(self):
        """Atualiza a interface do assistente."""
        print("Atualizando interface...")  # Exemplo de log de atualização
        # Atualizações na interface podem ser feitas aqui

    def definir_fundo(self):
        """Define o fundo da janela com uma imagem e opacidade."""
        # Cria a paleta
        palette = QPalette()

        # Carrega e ajusta a imagem ao tamanho da janela
        pixmap = QPixmap("max/assets/img/fundo.png").scaled(
            self.size(),  # Escala a imagem para preencher a janela
            Qt.IgnoreAspectRatio,  # Ignora o aspecto da imagem para cobrir o fundo
            Qt.SmoothTransformation  # Usa uma transformação suave ao redimensionar
        )

        # Cria uma camada de opacidade sobre a imagem
        opacidade = QColor(0, 0, 1, 170)  # Uma cor preta com 170 de opacidade (valor entre 0 e 255)
        overlay_pixmap = QPixmap(self.size())  # Cria um QPixmap do tamanho da janela
        overlay_pixmap.fill(opacidade)  # Preenche a camada com a cor opaca

        # Combina a imagem de fundo com a opacidade
        final_pixmap = pixmap.copy()  # Copia o fundo original
        painter = QPainter(final_pixmap)
        painter.drawPixmap(0, 0, overlay_pixmap)  # Desenha a camada de opacidade sobre o fundo
        painter.end()

        # Define a imagem com opacidade na paleta
        palette.setBrush(QPalette.Window, QBrush(final_pixmap))
        self.setPalette(palette)

    def criar_botoes_sidebar(self):
        """Cria os botões da sidebar com ícones."""    
        botoes_info = [
            ("Home", "max/assets/icon/circular.png", Home),
            ("Email", "max/assets/icon/circular.png", EmailDashboard),
            ("Tarefas", "max/assets/icon/circular.png", Tarefa),
            ("Comandos", "max/assets/icon/circular.png", Comando),
            ("Configurações", "max/assets/icon/circular.png", Configuracao)
        ]

        for nome, icone, janela_class in botoes_info:
            botao = QPushButton(nome)
            botao.setIcon(QIcon(icone))  # Define o ícone do botão
            botao.setIconSize(QSize(24, 24))  # Corrigido para usar QSize corretamente
            botao.setStyleSheet(
                "background: none; "
                "border: none; "  # Remove a borda
                "color: #2496be; "
                "font-size: 16px; "
                "padding: 5px; "
                "text-align: left;"  # Alinhamento do texto à esquerda
            )
            botao.setFocusPolicy(Qt.NoFocus)  # Remove a borda ao focar
            botao.clicked.connect(lambda checked, janela=janela_class: self.exibir_conteudo(janela))  # Conecta o botão
            self.sidebar_layout.addWidget(botao)

        # Espaço entre os botões e a parte central
        self.sidebar_layout.addStretch()

    def exibir_conteudo(self, janela_class):
        """Exibe o conteúdo de uma nova janela na parte central."""
        # Verifica e finaliza o temporizador da janela anterior, se houver
        if self.temporizador_atualizacao.isActive():
            self.temporizador_atualizacao.stop()

        nova_janela = janela_class()  # Instancia a nova janela
        
        # Limpa o layout central
        for i in reversed(range(self.central_layout.count())): 
            widget = self.central_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()  # Remove o widget existente
        
        # Adiciona a nova janela ao layout central
        self.central_layout.addWidget(nova_janela)
        self.temporizador_atualizacao.start()  # Reinicia o temporizador

    def eventFilter(self, source, event):
        """Filtro de evento para controlar a exibição da sidebar."""
        if source == self.sidebar:
            if event.type() == QEvent.Enter:
                self.mostrar_sidebar()
            elif event.type() == QEvent.Leave:
                # Verifique se o mouse ainda está sobre um dos botões
                mouse_pos = QCursor.pos()  # Obtém a posição global do mouse
                if self.sidebar.geometry().contains(mouse_pos):  # Verifica se está dentro da sidebar
                    return False  # Ignora o evento se o mouse ainda estiver sobre a sidebar
                self.ocultar_sidebar()
        return super().eventFilter(source, event)

    def mostrar_sidebar(self):
        """Exibe a sidebar com animação."""
        animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        animation.setDuration(300)  # Duração da animação em milissegundos
        animation.setStartValue(self.sidebar.width())  # Largura inicial
        animation.setEndValue(200)  # Largura final
        self.sidebar.setFixedWidth(170)  
        animation.start()

    def ocultar_sidebar(self):
        """Oculta a sidebar com animação."""
        animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        animation.setDuration(300)  # Duração da animação em milissegundos
        animation.setStartValue(self.sidebar.width())  # Largura inicial
        animation.setEndValue(50)  # Largura final (apenas ícones visíveis)
        animation.start()
        self.sidebar.setFixedWidth(50)  # Defina a largura fixa após iniciar a animação


    def processar_fala(self, texto):
        """Processa o texto de fala detectada e executa comandos na interface."""
        print(f"Texto reconhecido: {texto}")
        texto = texto.lower()
        
        def executar_comando(comandos, acao, *args):
            for comando in comandos:
                if comando in texto:
                    acao(*args)
                    return True
            return False

        # Função auxiliar para exibir mensagem de feedback e abrir janelas
        def abrir_janela(janela, mensagem):
            self.exibir_conteudo(janela)
            self.reconhecimento_fala.fala(mensagem)

        # Função auxiliar para fechar janelas e exibir feedback
        def fechar_janela(janela, mensagem):
            self.fechar_conteudo(janela)
            self.reconhecimento_fala.fala(mensagem)

        # Abrir janelas principais
        comandos_abrir = {
            ("abrir e-mail", "email principal", "dashboard de email"): (EmailDashboard, "Abrindo janela de e-mails."),
            ("abrir tarefas", "tela de tarefas", "ver tarefas"): (Tarefa, "Abrindo janela de tarefas."),
            ("abrir configurações", "configurações", "ajustes"): (Configuracao, "Abrindo janela de configurações.")
        }

        # Fechar janelas principais
        comandos_fechar = {
            "fechar e-mail": (EmailDashboard, "Fechando janela de e-mails.")
        }

        # Executar comandos de abrir janelas principais
        for comandos, (janela, mensagem) in comandos_abrir.items():
            if executar_comando(comandos, abrir_janela, janela, mensagem):
                return

        # Executar comandos de fechar janelas principais
        for comando, (janela, mensagem) in comandos_fechar.items():
            if executar_comando((comando,), fechar_janela, janela, mensagem):
                return

        # Abrir janelas internas do e-mail
        comandos_abrir_internos_email = {
            ("abrir enviados", "enviados", "email enviados"): ("EmailEnviado", "Abrindo janela de e-mails enviados."),
            ("abrir recebidos", "recebidos", "email recebidos"): ("EmailRecebido", "Abrindo janela de e-mails recebidos."),
            ("abrir rascunho", "rascunho", "email rascunhos"): ("EmailRascunho", "Abrindo janela de rascunhos de e-mails."),
            ("abrir lixeira", "lixeira", "email lixeira"): ("Lixeira", "Abrindo janela de lixeira de e-mails."),
            ("abrir configurações de e-mail", "configuração de e-mail", "configuração email"): ("Configuracao", "Abrindo janela de configurações de e-mail.")
        }

        for comandos, (janela_class, mensagem) in comandos_abrir_internos_email.items():
            if any(comando in texto for comando in comandos):
                if not hasattr(self, 'email_dashboard') or not isinstance(self.email_dashboard, EmailDashboard):
                    abrir_janela(EmailDashboard, "Abrindo janela de e-mails.")
                    self.email_dashboard = self.central_layout.itemAt(0).widget()

                if isinstance(self.email_dashboard, EmailDashboard):
                    self.email_dashboard.email_exibir_conteudo(janela_class)
                    self.reconhecimento_fala.fala(mensagem)
                return

        # Fechar janelas internas do e-mail
        comandos_fechar_internos_email = {
            ("fechar enviados", "fechar email enviados"): ("enviados", "Fechando janela de e-mails enviados."),
            ("fechar recebidos", "fechar email recebidos"): ("recebidos", "Fechando janela de e-mails recebidos."),
            ("fechar rascunho", "fechar email rascunhos"): ("rascunho", "Fechando janela de rascunhos de e-mails."),
            ("fechar lixeira", "fechar email lixeira"): ("lixeira", "Fechando janela de lixeira de e-mails."),
            ("fechar configurações de e-mail", "fechar configuração de email"): ("configuracao", "Fechando janela de configurações de e-mail.")
        }

        for comandos, (janela_class, mensagem) in comandos_fechar_internos_email.items():
            if any(comando in texto for comando in comandos):
                if isinstance(self.email_dashboard, EmailDashboard):
                    self.email_dashboard.fechar_janela_interna(janela_class)
                    self.reconhecimento_fala.fala(mensagem)
                else:
                    self.reconhecimento_fala.fala("A janela de e-mails não está aberta.")
                return

        # Comandos para abrir programas do Windows
        comandos_abrir_programas = {
            ("abrir navegador", "navegador"): ("chrome", "Abrindo navegador Chrome."),
            # Outros comandos aqui...
        }
        # Comandos para abrir programas do Windows
        comandos_abrir_programas = {
            ("abrir navegador", "navegador"): ("chrome", "Abrindo navegador Chrome."),
            ("abrir bloco de notas", "notepad", "bloco de notas"): ("notepad", "Abrindo Bloco de Notas."),
            ("abrir calculadora", "calculadora"): ("calc", "Abrindo Calculadora."),
            ("abrir explorador de arquivos", "explorador de arquivos"): ("explorer", "Abrindo Explorador de Arquivos."),
            ("abrir word", "word", "microsoft word"): ("winword", "Abrindo Microsoft Word."),
            ("abrir excel", "excel", "microsoft excel"): ("excel", "Abrindo Microsoft Excel."),
            ("abrir powerpoint", "powerpoint", "microsoft powerpoint"): ("powerpnt", "Abrindo Microsoft PowerPoint."),
            ("abrir paint", "paint", "mspaint"): ("mspaint", "Abrindo Paint."),
            ("abrir prompt de comando", "prompt", "cmd"): ("cmd", "Abrindo Prompt de Comando."),
            ("abrir powershell", "powershell"): ("powershell", "Abrindo PowerShell."),
            ("abrir gerenciador de tarefas", "gestor de tarefas", "task manager"): ("taskmgr", "Abrindo Gerenciador de Tarefas."),
            ("abrir gerenciador de dispositivos", "gestor de dispositivos", "device manager"): ("devmgmt.msc", "Abrindo Gerenciador de Dispositivos."),
            ("abrir visualizador de eventos", "gerenciador de eventos", "event viewer"): ("eventvwr", "Abrindo Visualizador de Eventos."),
            ("abrir gerenciamento de disco", "gestor de disco"): ("diskmgmt.msc", "Abrindo Gerenciamento de Disco."),
            ("abrir configurações", "definições", "configurações do windows"): ("ms-settings:", "Abrindo Configurações do Windows."),
            ("abrir lixeira", "lixeira do windows"): ("explorer.exe shell:RecycleBinFolder", "Abrindo Lixeira do Windows.")
        }

        for comandos, (programa, mensagem) in comandos_abrir_programas.items():
            if executar_comando(comandos, lambda p, m: subprocess.Popen(p), programa, mensagem):
                return

        # Comandos para fechar programas do Windows (por nome do processo)
        comandos_fechar_programas = {
            ("fechar navegador", "fechar chrome"): ("chrome.exe", "Fechando navegador Chrome."),
            ("fechar bloco de notas", "fechar notepad"): ("notepad.exe", "Fechando Bloco de Notas."),
            ("fechar calculadora", "fechar calculadora"): ("Calculator.exe", "Fechando Calculadora."),
            ("fechar explorador de arquivos", "fechar explorador de arquivos"): ("explorer.exe", "Fechando Explorador de Arquivos."),
            ("fechar word", "fechar microsoft word"): ("winword.exe", "Fechando Microsoft Word."),
            ("fechar excel", "fechar microsoft excel"): ("excel.exe", "Fechando Microsoft Excel."),
            ("fechar powerpoint", "fechar microsoft powerpoint"): ("powerpnt.exe", "Fechando Microsoft PowerPoint."),
            ("fechar paint", "fechar mspaint"): ("mspaint.exe", "Fechando Paint."),
            ("fechar prompt de comando", "fechar prompt", "fechar cmd"): ("cmd.exe", "Fechando Prompt de Comando."),
            ("fechar powershell", "fechar terminal powershell"): ("powershell.exe", "Fechando PowerShell."),
            ("fechar gerenciador de tarefas", "fechar gestor de tarefas"): ("taskmgr.exe", "Fechando Gerenciador de Tarefas."),
            ("fechar lixeira", "fechar lixeira do windows"): (None, "Minimizando Lixeira do Windows.")
        }

        for comandos, (processo, mensagem) in comandos_fechar_programas.items():
            if executar_comando(comandos, lambda p, m: subprocess.run(f"taskkill /f /im {p} /t", shell=True), processo, mensagem):
                return

        # Minimizar janelas
        comandos_minimizar_janelas = {
            ("minimizar tudo", "minimizar todas as janelas"): ("Minimizando todas as janelas.")
        }

        for comandos, mensagem in comandos_minimizar_janelas.items():
            if executar_comando(comandos, lambda: self.minimizar_todas_as_janelas()):
                self.reconhecimento_fala.fala(mensagem)
                return

        
    def minimizar_todas_as_janelas(self):
        """Minimiza todas as janelas usando o atalho Win + M."""
        try:
            pyautogui.hotkey("win", "m")
            print("Todas as janelas foram minimizadas.")
        except Exception as e:
            print(f"Erro ao minimizar janelas: {e}")    
                        
    # Função para fechar a janela
    def fechar_conteudo(self, janela_class):
        """Fecha a janela especificada se estiver aberta."""
        for i in reversed(range(self.central_layout.count())): 
            widget = self.central_layout.itemAt(i).widget()
            if isinstance(widget, janela_class):
                widget.deleteLater()  # Remove o widget existente
        
    def closeEvent(self, event):
        """Método para encerrar a thread ao fechar a janela."""
        self.reconhecimento_fala.parar_reconhecimento()
        self.thread_reconhecimento.quit()
        self.thread_reconhecimento.wait()
        super().closeEvent(event)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = MainWindow()
    janela.show()
    sys.exit(app.exec())

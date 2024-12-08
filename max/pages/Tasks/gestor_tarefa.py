from PySide6.QtWidgets import ( QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel,
                                QScrollArea, QGridLayout, QFrame, QSizePolicy,  QDialog, QVBoxLayout, QHBoxLayout, 
                                QLineEdit, QTextEdit, QLabel, QFileDialog, QMessageBox, QCalendarWidget, QDialog,
                                QVBoxLayout, QLabel, QLineEdit, QTextEdit, QDateTimeEdit, QCheckBox, QPushButton,
                                QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QDateTimeEdit,
                                QComboBox, QCheckBox, QSpinBox, QListWidget, QPushButton, QScrollArea, QWidget, QTimeEdit,
                                QCheckBox, QGroupBox, QListWidgetItem)
from config.config import BASE_DIR_Calendario, LOG_DIR_Calendario, pastas_calendario, notificar_erro, notificar_sucesso
from PySide6.QtGui import QIcon, QCursor
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEvent, QDate, QDateTime,QTime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from datetime import datetime
import traceback
import calendar

import uuid
import json
import re
import os


class CalendarioDashboard(QMainWindow):
    
    def __init__(self, BASE_DIR_Calendario=BASE_DIR_Calendario, LOG_DIR_Calendario=LOG_DIR_Calendario):
        super().__init__()

        # Inicializa as pastas ao iniciar o dashboard
        pastas_calendario(self)
        if not os.path.exists(LOG_DIR_Calendario ):
            os.makedirs(LOG_DIR_Calendario )
        
        self.log_file = os.path.join(LOG_DIR_Calendario, "Logs_Tarefa.log")
        
        self.tasks_file = os.path.join(BASE_DIR_Calendario, pastas_calendario["tarefas"], "tasks.json")
       
        
        self.verificar_estrutura_arquivos()
        
        
        self.calendario_recebido_widget = CalendarioAnual()  # Inicializa antes de tarefa_exibir_conteudo ser chamado
        
        # Exemplo de criação de um dia como um QLabel (ou QPushButton)
        dia_label = QLabel("01")
        dia_label.setAlignment(Qt.AlignCenter)
        dia_label.mousePressEvent = lambda event, data="01-01-2024": self.dia_clicado(event, data)
        # Adicione `dia_label` ao layout do calendário
        
        # Variáveis para cada janela interna
        self.janela_recebidos = None
        self.janela_enviados = None
        self.janela_rascunho = None
        self.janela_lixeira = None
        self.janela_configuracao = None

        # Definindo o layout principal (vertical)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove as margens do layout
        main_layout.setSpacing(0)  # Remove o espaçamento entre os widgets

        # Adicionando a navbar
        self.navbar = QWidget()
        self.navbar_layout = QHBoxLayout()
        self.navbar.setLayout(self.navbar_layout)
        self.navbar.setFixedHeight(46)  # Altura fixa da navbar
        self.navbar.setStyleSheet("background-color: rgba(0, 21, 42, 180);")  # Cor de fundo igual ao sidebar
        main_layout.addWidget(self.navbar)

        # Adicionando botão "Compor" à navbar
        self.botao_compor = QPushButton("Compor")
        self.botao_compor.setIcon(QIcon("max/assets/icon/compor.png"))  # Defina o ícone que deseja usar
        self.botao_compor.setIconSize(QSize(24, 24))  # Tamanho do ícone
        self.botao_compor.setStyleSheet(
            "background: #2496be; "
            "border: none; "
            "color: white; "
            "font-size: 14px; "
            "padding: 3px 15px; "
            "border-radius: 5px;"
        )
        self.botao_compor.setFocusPolicy(Qt.NoFocus)
        self.navbar_layout.addWidget(self.botao_compor, alignment=Qt.AlignLeft)
        # self.botao_compor.clicked.connect(self.abrir_compor_calendario)
       
        # Adicionando botão "Compor" à navbar
        self.botao_recarregar = QPushButton("Mes atual")
        self.botao_recarregar.setIcon(QIcon("max/assets/icon/recarregar.png"))  # Defina o ícone que deseja usar
        self.botao_recarregar.setIconSize(QSize(24, 24))  # Tamanho do ícone
        self.botao_recarregar.setStyleSheet(
            "background: #2496be; "
            "border: none; "
            "color: white; "
            "font-size: 14px; "
            "padding: 3px 15px; "
            "border-radius: 5px;"
        )
        self.botao_recarregar.setFocusPolicy(Qt.NoFocus)
        self.navbar_layout.addWidget(self.botao_recarregar, alignment=Qt.AlignLeft)
        self.botao_recarregar.clicked.connect(lambda: self.tarefa_exibir_conteudo(CalendarioMesAtual))
        
        # Adicionando botão "Compor" à navbar
        self.botao_semana = QPushButton("Semana")
        self.botao_semana.setIcon(QIcon("max/assets/icon/semana.png"))  # Defina o ícone que deseja usar
        self.botao_semana.setIconSize(QSize(24, 24))  # Tamanho do ícone
        self.botao_semana.setStyleSheet(
            "background: #2496be; "
            "border: none; "
            "color: white; "
            "font-size: 14px; "
            "padding: 3px 15px; "
            "border-radius: 5px;"
        )
        self.botao_semana.setFocusPolicy(Qt.NoFocus)
        self.navbar_layout.addWidget(self.botao_semana, alignment=Qt.AlignLeft)
        self.botao_semana.clicked.connect(lambda: self.tarefa_exibir_conteudo(DiasSemanaMesAtual))
        
        
        # Adicionando botão "Calendário Anual" à navbar
        self.botao_calendario_anual = QPushButton("Calendário Anual")
        self.botao_calendario_anual.setIcon(QIcon("max/assets/icon/calendario.png"))  # Defina o ícone que deseja usar
        self.botao_calendario_anual.setIconSize(QSize(24, 24))  # Tamanho do ícone
        self.botao_calendario_anual.setStyleSheet(
            "background: #2496be; "
            "border: none; "
            "color: white; "
            "font-size: 14px; "
            "padding: 3px 15px; "
            "border-radius: 5px;"
        )
        self.botao_calendario_anual.setFocusPolicy(Qt.NoFocus)
        self.navbar_layout.addWidget(self.botao_calendario_anual, alignment=Qt.AlignLeft)
        self.botao_calendario_anual.clicked.connect(lambda: self.tarefa_exibir_conteudo(CalendarioAnual))

        

        # Definindo o layout horizontal para a sidebar e parte central
        central_layout = QHBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)  # Remove as margens do layout central
        central_layout.setSpacing(0)  # Remove espaçamento no layout central

        # Adicionando a sidebar
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)
        self.sidebar.setFixedWidth(50)  # Sidebar oculta inicialmente
        self.sidebar.setStyleSheet("background-color: rgba(0, 21, 42, 180); margin: 0; padding: 0;")
        central_layout.addWidget(self.sidebar)

        # Adicionando a parte central
        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout()
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        self.central_widget.setLayout(self.central_layout)
        central_layout.addWidget(self.central_widget)

        # Adicionando botões à sidebar
        self.botoes = self.criar_botoes_sidebar()

        # Exibe a página de "calendarios Recebidos" por padrão
        self.tarefa_exibir_conteudo(CalendarioAnual)
      
        # Conectar eventos de mouse para a sidebar
        self.sidebar.installEventFilter(self)

        # Adicionar o layout central ao layout principal
        main_layout.addLayout(central_layout)

        # Configurando o widget central
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def criar_botoes_sidebar(self):
        """Cria os botões da sidebar com ícones."""    
        botoes_info = [
            ("Recebidos", "max/assets/icon/circular.png",     CalendarioAnual),
            ("Enviados", "max/assets/icon/circular.png",      CalendarioAnual ),
            ("Rascunhos", "max/assets/icon/circular.png",     CalendarioAnual),
            ("Lixeira", "max/assets/icon/circular.png",       CalendarioAnual),
            ("Configurações", "max/assets/icon/circular.png", CalendarioAnual)
        ]

        for nome, icone, janela_class in botoes_info:
            botao = QPushButton(nome)
            botao.setIcon(QIcon(icone))  # Define o ícone do botão
            botao.setIconSize(QSize(24, 24))  # Corrigido para usar QSize corretamente
            botao.setStyleSheet(
                "background: none; "
                "border: none; "
                "color: #2496be; "
                "font-size: 16px; "
                "padding: 5px; "
                "text-align: left;"
            )
            botao.setFocusPolicy(Qt.NoFocus)
            botao.clicked.connect(lambda checked, janela=janela_class: self.tarefa_exibir_conteudo(janela))
            self.sidebar_layout.addWidget(botao)

        # Espaço entre os botões e a parte central
        self.sidebar_layout.addStretch()

    def eventFilter(self, source, event):
        """Filtro de evento para controlar a exibição da sidebar."""
        try:
            if source == self.sidebar:
                if event.type() == QEvent.Enter:
                    # Quando o mouse entra na sidebar, exibe a sidebar
                    self.mostrar_sidebar()
                    return True
                elif event.type() == QEvent.Leave:
                    # Verifique se o mouse ainda está dentro da sidebar
                    mouse_pos = self.mapFromGlobal(QCursor.pos())  # Pega a posição do cursor no espaço da janela
                    if not self.sidebar.rect().contains(mouse_pos):  # Se o mouse está fora da sidebar
                        self.ocultar_sidebar()
                    return True
            return super().eventFilter(source, event)
        except Exception as e:
            self.log_erro(f"Erro no eventFilter: {e}")
            return False

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
 
    def notificar_sucesso(self, mensagem):
        QMessageBox.information(self, "Sucesso", mensagem)

    def notificar_erro(self, mensagem):
        QMessageBox.critical(self, "Erro", mensagem)
                
    def tarefa_exibir_conteudo(self, janela_class):
        """Exibe o conteúdo de uma nova janela na parte central."""
        # Instancia a janela e atribui à variável correspondente
        if janela_class == CalendarioAnual:
            self.janela_calendario_anual = CalendarioAnual()
            nova_janela = self.janela_calendario_anual
        elif janela_class == CalendarioMesAtual:
            self.janela_calendario_mes = CalendarioMesAtual()
            nova_janela = self.janela_calendario_mes
        elif janela_class == DiasSemanaMesAtual:
            self.janela_calendario_semana = DiasSemanaMesAtual()
            nova_janela = self.janela_calendario_semana
        else:
            nova_janela = janela_class()

        # Limpa o layout central antes de adicionar nova janela
        for i in reversed(range(self.central_layout.count())):
            widget = self.central_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        self.central_layout.addWidget(nova_janela)
  
    def verificar_estrutura_arquivos(self):
        """Verifica e cria a estrutura de pastas e o arquivo de tarefas."""
        os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)  # Garante que o diretório de tarefas existe
        
        if not os.path.isfile(self.tasks_file):
            with open(self.tasks_file, 'w') as file:
                json.dump([], file)  # Inicializa o arquivo com uma lista vazia

    def fechar_janela_interna(self, nome_janela):
        """Fecha uma janela interna específica por nome."""
        try:
            if nome_janela == "recebidos" and self.janela_recebidos:
                self.janela_recebidos.close()
                self.janela_recebidos = None
            elif nome_janela == "enviados" and self.janela_enviados:
                self.janela_enviados.close()
                self.janela_enviados = None
            elif nome_janela == "rascunho" and self.janela_rascunho:
                self.janela_rascunho.close()
                self.janela_rascunho = None
            elif nome_janela == "lixeira" and self.janela_lixeira:
                self.janela_lixeira.close()
                self.janela_lixeira = None
            elif nome_janela == "configuracao" and self.janela_configuracao:
                self.janela_configuracao.close()
                self.janela_configuracao = None
            else:
                mensagem = (f"Janela '{nome_janela}' não encontrada ou já está fechada.")
                self.notificar_erro(mensagem)
        except Exception as e:
            self.log_erro(f"Erro ao fechar a janela '{nome_janela}': {e}")
     
    def dia_clicado(self, event, data):
        """Método chamado ao clicar em um dia do calendário."""
        if event.button() == Qt.LeftButton:
            self.parent().abrir_modal_dia(data)
     
    def abrir_modal_dia(self, data):
        """Abre um modal para exibir informações sobre o dia selecionado."""
        modal = QDialog(self)
        modal.setWindowTitle(f"Detalhes do Dia: {data}")
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Informações para o dia {data}"))
        # Adicione outros widgets conforme necessário, como listas de tarefas ou eventos do dia

        modal.setLayout(layout)
        modal.exec()  # Abre o modal de forma modal (bloqueia a janela principal até ser fechado)       

    def log_erro(self, message):
        """Registra mensagens de erro no arquivo de log com traceback completo."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - ERROR - {message}\n")
                # Adiciona o traceback completo se houver uma exceção ativa
                log_file.write(traceback.format_exc() + "\n")
        except Exception as e:
            print(f"Erro ao registrar log: {e}")

class CalendarioAnual(QWidget):
    def __init__(self, LOG_DIR_Calendario=LOG_DIR_Calendario):
        super().__init__()
        
        if not os.path.exists(LOG_DIR_Calendario ):
            os.makedirs(LOG_DIR_Calendario )
        self.log_file = os.path.join(LOG_DIR_Calendario, "Logs_Tarefa.log")
        
        # Inicializa o layout principal com barra de rolagem
        try:
            # Configura área de rolagem e layout principal
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)
            self.main_widget = QWidget()
            self.scroll_area.setWidget(self.main_widget)
            self.scroll_area.setStyleSheet("""
                QScrollBar:vertical {
                background: none;
                width: 12px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #2496be;
                min-height: 20px;
                border-radius: 6px;
            }
            
            """)
            
            # Layout vertical para o título e a área de rolagem
            self.layout = QVBoxLayout(self)
            self.setLayout(self.layout)
            self.layout.addWidget(self.scroll_area)

     
            # Layout em grade para os meses (4x3)
            self.grid_layout = QGridLayout(self.main_widget)
            self.grid_layout.setSpacing(15)  # Espaçamento entre as células da grade

            # Inicializa o calendário e exibe na grade
            self.calendario = calendar.Calendar()
            self.exibir_calendario()
        except Exception as e:
            self.log_erro(f"Erro na inicialização de CalendarioAnual: {e}")

    def exibir_calendario(self):
        """Exibe o calendário do ano atual em uma grade de 4x3."""
        try:
            ano_atual = datetime.now().year
            mes_atual = datetime.now().month  # Obter o mês atual
            dia_atual = datetime.now().day    # Obter o dia atual

            # Loop para adicionar calendários mensais em uma grade 4x3
            for mes in range(1, 13):
                # Título do mês
                mes_label = QLabel(datetime(ano_atual, mes, 1).strftime("%B %Y"))
                mes_label.setAlignment(Qt.AlignCenter)
                mes_label.setStyleSheet("color: #2496be;") 

                # Calendário para o mês atual
                calendario_mes = QCalendarWidget()
                calendario_mes.setDateRange(
                    QDate(ano_atual, mes, 1),
                    QDate(ano_atual, mes, QDate(ano_atual, mes, 1).daysInMonth())
                )
                calendario_mes.setGridVisible(True)
                calendario_mes.setFixedHeight(200)  # Ajuste o tamanho conforme necessário

                # Seleciona o dia atual se for o mês atual
                if mes == mes_atual:
                    calendario_mes.setSelectedDate(QDate(ano_atual, mes, dia_atual))

                # Determinar a posição do mês no layout (4x3)
                row = (mes - 1) // 3
                col = (mes - 1) % 3

                # Adicionar o título e o calendário ao layout de grade
                self.grid_layout.addWidget(mes_label, row * 2, col)      # Linha para o título
                self.grid_layout.addWidget(calendario_mes, row * 2 + 1, col)  # Linha para o calendário
        except Exception as e:
            self.log_erro(f"Erro ao exibir o calendário anual: {e}")
    
    def log_erro(self, message):
        """Registra mensagens de erro no arquivo de log com traceback completo."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - ERROR - {message}\n")
                # Adiciona o traceback completo se houver uma exceção ativa
                log_file.write(traceback.format_exc() + "\n")
        except Exception as e:
            print(f"Erro ao registrar log: {e}")
  
class CalendarioMesAtual(QWidget):
    def __init__(self, log_file=LOG_DIR_Calendario):
        super().__init__()
        
        if not os.path.exists(LOG_DIR_Calendario ):
            os.makedirs(LOG_DIR_Calendario )
        self.log_file = os.path.join(LOG_DIR_Calendario, "Logs_Tarefa.log")
        
        try:
            # Configura o layout principal
            self.layout = QVBoxLayout(self)
            self.setLayout(self.layout)

            # Obtém o mês e o ano atuais
            hoje = datetime.now()
            self.ano_atual = hoje.year
            self.mes_atual = hoje.month
            self.dia_atual = hoje.day

            # Dicionário para tradução dos meses
            self.meses_traduzidos = {
                "January": "Janeiro", "February": "Fevereiro", "March": "Março",
                "April": "Abril", "May": "Maio", "June": "Junho",
                "July": "Julho", "August": "Agosto", "September": "Setembro",
                "October": "Outubro", "November": "Novembro", "December": "Dezembro"
            }

            # Adiciona botões de navegação
            self.adicionar_botoes_navegacao()
            
            # Exibe o título do mês atual e o calendário
            self.exibir_titulo_mes()
            self.exibir_calendario_mes()
        except Exception as e:
            self.log_erro(f"Erro na inicialização do CalendarioMesAtual: {e}")

    def adicionar_botoes_navegacao(self):
        """Adiciona botões para navegar para o mês anterior e próximo."""
        try:
            # Layout para os botões de navegação
            layout_botoes = QHBoxLayout()

            # Botão para o mês anterior
            botao_anterior = QPushButton()
            botao_anterior.setIcon(QIcon.fromTheme("go-previous"))  # Define o ícone (ajustável conforme o sistema)
            botao_anterior.setText("Anterior")
            botao_anterior.clicked.connect(self.mostrar_mes_anterior)
            layout_botoes.addWidget(botao_anterior, alignment=Qt.AlignLeft)

            # Botão para o próximo mês
            botao_proximo = QPushButton()
            botao_proximo.setIcon(QIcon.fromTheme("go-next"))  # Define o ícone (ajustável conforme o sistema)
            botao_proximo.setText("Próximo")
            botao_proximo.clicked.connect(self.mostrar_proximo_mes)
            layout_botoes.addWidget(botao_proximo, alignment=Qt.AlignRight)

            # Adiciona o layout dos botões ao layout principal
            self.layout.addLayout(layout_botoes)
        except Exception as e:
            self.log_erro(f"Erro ao adicionar botões de navegação: {e}")

    def exibir_titulo_mes(self):
        """Exibe o título com o nome do mês e ano atuais."""
        try:
            nome_mes = datetime(self.ano_atual, self.mes_atual, 1).strftime("%B %Y")
            nome_mes_traduzido = self.traduzir_mes(nome_mes)
            self.titulo = QLabel(nome_mes_traduzido)
            self.titulo.setAlignment(Qt.AlignCenter)
            self.titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2496be;")
            self.layout.addWidget(self.titulo)

        except Exception as e:
            self.log_erro(f"Erro ao exibir o título do mês: {e}")

    def traduzir_mes(self, nome_mes):
        """Traduz o nome do mês de inglês para português."""
        try:
            for mes_en, mes_pt in self.meses_traduzidos.items():
                if mes_en in nome_mes:
                    return nome_mes.replace(mes_en, mes_pt)
            return nome_mes
        except Exception as e:
            self.log_erro(f"Erro ao traduzir o mês: {e}")
            return nome_mes

    def exibir_calendario_mes(self):
        """Exibe o calendário do mês atual com o dia atual selecionado e estilo personalizado."""
        try:
            # Cria o widget de calendário
            self.calendario_mes = QCalendarWidget()
            self.calendario_mes.setDateRange(
                QDate(self.ano_atual, self.mes_atual, 1),
                QDate(self.ano_atual, self.mes_atual, QDate(self.ano_atual, self.mes_atual, 1).daysInMonth())
            )
            self.calendario_mes.setGridVisible(True)
            
            # Seleciona o dia atual
            self.calendario_mes.setSelectedDate(QDate(self.ano_atual, self.mes_atual, self.dia_atual))
            
            # Conectar o clique em um dia para abrir um modal
            self.calendario_mes.clicked.connect(self.abrir_modal_dia)
            

            # Aplica estilos para o dia selecionado
            self.calendario_mes.setStyleSheet("""
                /* Estilo do dia selecionado */
                QCalendarWidget QAbstractItemView::item:selected {
                    background-color: #2496be;  /* Fundo do dia selecionado */
                    color: white;               /* Cor do texto do dia selecionado */
                }
                /* Estilo do dia atual */
                QCalendarWidget QAbstractItemView::item {
                    selection-background-color: #2496be; /* Fundo do dia atual quando selecionado */
                    selection-color: white;             /* Cor do texto do dia atual */
                }
            """)
            
            # Adiciona o calendário ao layout
            self.layout.addWidget(self.calendario_mes)

        except Exception as e:
            self.log_erro(f"Erro ao exibir o calendário do mês: {e}")
     
    def mostrar_mes_anterior(self):
        """Atualiza o calendário para exibir o mês anterior."""
        try:
            if self.mes_atual == 1:
                self.mes_atual = 12
                self.ano_atual -= 1
            else:
                self.mes_atual -= 1
            self.atualizar_calendario()
        except Exception as e:
            self.log_erro(f"Erro ao mostrar mês anterior: {e}")

    def mostrar_proximo_mes(self):
        """Atualiza o calendário para exibir o próximo mês."""
        try:
            if self.mes_atual == 12:
                self.mes_atual = 1
                self.ano_atual += 1
            else:
                self.mes_atual += 1
            self.atualizar_calendario()
        except Exception as e:
            self.log_erro(f"Erro ao mostrar próximo mês: {e}")

    def atualizar_calendario(self):
        """Atualiza o título do mês e o calendário para refletir o novo mês/ano."""
        try:
            # Atualizar o título do mês com a tradução
            nome_mes = datetime(self.ano_atual, self.mes_atual, 1).strftime("%B %Y")
            nome_mes_traduzido = self.traduzir_mes(nome_mes)
            self.titulo.setText(nome_mes_traduzido)

            # Atualizar o range de datas no calendário
            self.calendario_mes.setDateRange(
                QDate(self.ano_atual, self.mes_atual, 1),
                QDate(self.ano_atual, self.mes_atual, QDate(self.ano_atual, self.mes_atual, 1).daysInMonth())
            )
        except Exception as e:
            self.log_erro(f"Erro ao atualizar o calendário: {e}")

    def abrir_modal_dia(self, date):
        """Abre um modal quando um dia é clicado no calendário."""
        try:
            modal = QMessageBox(self)
            max1 = 'Max'
            modal.setWindowTitle(f"{max1} Canlendário")
            modal.setText(f"Você clicou no dia {date.toString('dd/MM/yyyy')}. Deseja adicionar um evento ou tarefa?")

           # Configura os botões
            btn_evento = modal.addButton("Evento", QMessageBox.AcceptRole)
            btn_evento.setStyleSheet("color: #2496be; background-color: white; padding: 2px; border-radius: 4px;")

            btn_tarefa = modal.addButton("Tarefa", QMessageBox.RejectRole)
            btn_tarefa.setStyleSheet("color: #2496be; background-color: white; padding: 2px; border-radius: 4px;")

            btn_cancelar = modal.addButton(QMessageBox.Cancel)
            btn_cancelar.setText("Cancelar")  # Define o texto explicitamente se desejar
            btn_cancelar.setStyleSheet("color: #2496be; background-color: white; padding: 2px; border-radius: 4px;")


            # Exibe a caixa de mensagem
            modal.exec()

            # Verifica qual botão foi clicado
            if modal.clickedButton() == btn_evento:
                dialog = ModalEvento()
                dialog.exec()
            elif modal.clickedButton() == btn_tarefa:
                dialog = ModalTarefa()
                dialog.exec()
            else:
                print("Operação cancelada")

        except Exception as e:
            self.log_erro(f"Erro ao abrir modal do dia: {e}")

    def log_erro(self, message):
        """Registra mensagens de erro no arquivo de log com traceback completo."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - ERROR - {message}\n")
                log_file.write(traceback.format_exc() + "\n")
        except Exception as e:
            print(f"Erro ao registrar log: {e}")
  
class DiasSemanaMesAtual(QWidget):
    def __init__(self, LOG_DIR_Calendario=LOG_DIR_Calendario):
        super().__init__()
        if not os.path.exists(LOG_DIR_Calendario ):
            os.makedirs(LOG_DIR_Calendario )
        self.log_file = os.path.join(LOG_DIR_Calendario, "Logs_Tarefa.log")
        
        try:
            self.layout_principal = QVBoxLayout(self)
            self.setLayout(self.layout_principal)
            
            self.ano_atual = datetime.now().year
            self.mes_atual = datetime.now().month
            self.dia_atual = datetime.now().day
            
            # Variável para controlar a semana exibida
            self.inicio_semana = QDate(self.ano_atual, self.mes_atual, self.dia_atual).addDays(-(QDate.currentDate().dayOfWeek() % 7))
            
            self.adicionar_botoes_navegacao()
            self.adicionar_cabecalho_mes()
            self.exibir_dias_semana_com_horarios()    
        except Exception as e:
            self.log_erro(f"Erro ao inicializar DiasSemanaMesAtual: {e}")

    def adicionar_botoes_navegacao(self):
        try:
            # # Definindo a localização para português antes de formatar o nome do mês
            # locale.setlocale(locale.LC_TIME, "pt_BR.utf8")  # Para português do Brasil
            # # locale.setlocale(locale.LC_TIME, "pt_PT.utf8")  # Para português de Portugal
            # # Layout de navegação para evitar duplicação
            self.layout_botoes = QGridLayout()
            botao_anterior = QPushButton("Semana Anterior")
            botao_anterior.clicked.connect(self.mostrar_semana_anterior)
            self.layout_botoes.addWidget(botao_anterior, 0, 0, Qt.AlignLeft)

            botao_proxima = QPushButton("Próxima Semana")
            botao_proxima.clicked.connect(self.mostrar_proxima_semana)
            self.layout_botoes.addWidget(botao_proxima, 0, 1, Qt.AlignRight)

            self.layout_principal.addLayout(self.layout_botoes)
        except Exception as e:
            self.log_erro(f"Erro ao adicionar botões de navegação: {e}")

 
    def adicionar_cabecalho_mes(self):
        try:
            self.meses_em_portugues = {
                "January": "Janeiro", "February": "Fevereiro", "March": "Março", "April": "Abril",
                "May": "Maio", "June": "Junho", "July": "Julho", "August": "Agosto",
                "September": "Setembro", "October": "Outubro", "November": "Novembro", "December": "Dezembro"
            }

            # Obter o nome do mês em inglês
            mes_ano = datetime.now().strftime("%B %Y")
            mes_nome, ano = mes_ano.split()  # Separa o nome do mês e o ano

            # Traduzir o mês para português
            mes_nome_em_portugues = self.meses_em_portugues.get(mes_nome, mes_nome)

            # Configura o cabeçalho do mês traduzido
            self.cabecalho_mes = QLabel(f"{mes_nome_em_portugues} {ano}")
            self.cabecalho_mes.setAlignment(Qt.AlignCenter)
            self.cabecalho_mes.setStyleSheet("font-size: 16px; font-weight: bold; color: #2496be; margin-bottom: 5px;")
            self.layout_principal.addWidget(self.cabecalho_mes)
        except Exception as e:
            self.log_erro(f"Erro ao exibir o cabeçalho do mês: {e}")


    def exibir_dias_semana_com_horarios(self):
        try:
            largura_coluna = 80

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            conteudo_widget = QWidget()
            scroll_area.setWidget(conteudo_widget)
            layout_scroll = QVBoxLayout(conteudo_widget)
            
            layout_grade = QGridLayout()
            layout_grade.setHorizontalSpacing(10)
            layout_grade.setVerticalSpacing(5)
            
            dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
            
            # Obter o nome do mês em inglês e traduzir
            mes_ano = self.inicio_semana.toString("MMMM yyyy")
            mes_nome = mes_ano.split()[0]  # Extrai o nome do mês
            ano = mes_ano.split()[1]       # Extrai o ano
            mes_nome_em_portugues = self.meses_em_portugues.get(mes_nome, mes_nome)

            # Atualiza o cabeçalho de mês em português
            self.cabecalho_mes.setText(f"{mes_nome_em_portugues} {ano}")
            
            # Adiciona cabeçalho de horários vazios na coluna 0 para alinhamento
            layout_grade.addWidget(QLabel(""), 0, 0)
            
            for i in range(7):
                dia_nome = dias_semana[i]
                dia_numero = self.inicio_semana.addDays(i).day()

                # Nome do dia
                label_dia_semana = QLabel(dia_nome)
                label_dia_semana.setAlignment(Qt.AlignCenter)
                label_dia_semana.setStyleSheet("font-weight: bold; color: #2496be; font-size: 10px;")
                label_dia_semana.setFixedWidth(largura_coluna)

                # Número do dia
                label_dia_numero = QLabel(str(dia_numero))
                label_dia_numero.setAlignment(Qt.AlignCenter)
                if dia_numero == self.dia_atual:
                    label_dia_numero.setStyleSheet("background-color: #2496be; color: white; border-radius: 5px; padding: 3px;")
                else:
                    label_dia_numero.setStyleSheet("background-color: #d3d3d3; color: black; border-radius: 5px; padding: 3px;")
                label_dia_numero.setFixedWidth(largura_coluna)

                # Adiciona o nome e o número do dia no layout da grade
                layout_grade.addWidget(label_dia_semana, 0, i + 1)
                layout_grade.addWidget(label_dia_numero, 1, i + 1)

            # Adiciona horários e células de agendamento abaixo do cabeçalho
            for hora in range(24):
                # Coluna da hora
                label_hora = QLabel(f"{hora}:00")
                label_hora.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                label_hora.setStyleSheet("font-size: 10px; color: #2696be;")
                label_hora.setFixedWidth(largura_coluna)
                layout_grade.addWidget(label_hora, hora + 2, 0)  # Linha ajustada para começar após o cabeçalho

                # Adiciona células vazias para cada dia da semana
                for i in range(7):
                    label_horario_dia = QLabel("")
                    label_horario_dia.setFixedSize(largura_coluna, 20)
                    label_horario_dia.setStyleSheet("border: 1px solid #e0e0e0;")
                    label_horario_dia.mouseDoubleClickEvent = self.abrir_modal_evento_tarefa
                    layout_grade.addWidget(label_horario_dia, hora + 2, i + 1)

            layout_scroll.addLayout(layout_grade)
            self.layout_principal.addWidget(scroll_area)
        
        except Exception as e:
            self.log_erro(f"Erro ao exibir os dias da semana e horários: {e}")

    def mostrar_semana_anterior(self):
        self.inicio_semana = self.inicio_semana.addDays(-7)
        self.recarregar_layout()

    def mostrar_proxima_semana(self):
        self.inicio_semana = self.inicio_semana.addDays(7)
        self.recarregar_layout()

    def recarregar_layout(self):
        # Limpa o layout principal antes de recarregar os componentes
        while self.layout_principal.count():
            item = self.layout_principal.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.adicionar_botoes_navegacao()
        self.adicionar_cabecalho_mes()
        self.exibir_dias_semana_com_horarios()

    def abrir_modal_evento_tarefa(self, event):
        try:
            modal = QMessageBox(self)
            modal.setWindowTitle("Novo Item")
            modal.setText("Deseja criar um Evento ou uma Tarefa?")
            modal.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            resposta = modal.exec()

            if resposta == QMessageBox.Ok:
                # Lógica para criar um Evento ou Tarefa
                print("Criar Evento ou Tarefa")
            else:
                print("Operação cancelada")
                
        except Exception as e:
            self.log_erro(f"Erro ao abrir modal de evento/tarefa: {e}")

    def log_erro(self, message):
        """Registra mensagens de erro no arquivo de log com traceback completo."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - ERROR - {message}\n")
                log_file.write(traceback.format_exc() + "\n")
        except Exception as e:
            print(f"Erro ao registrar log: {e}")
 
class ModalEvento(QDialog):
    def __init__(self, LOG_DIR_Calendario=LOG_DIR_Calendario):
        super().__init__()
        if not os.path.exists(LOG_DIR_Calendario):
            os.makedirs(LOG_DIR_Calendario)
        self.log_file = os.path.join(LOG_DIR_Calendario, "Logs_Tarefa.log")
        
        self.setWindowTitle("Adicionar Evento")
        self.setWindowIcon(QIcon("icone_evento.png"))
        self.setMinimumSize(900, 600)

        # Configurar a área de rolagem
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollBar:vertical {
                background: #eaeaea;
                width: 12px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #2496be;
                min-height: 20px;
                border-radius: 6px;
            }
        """)

        # Widget que conterá todos os componentes
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Campo: Título do evento e Período do evento
        titulo_periodo_layout = QHBoxLayout()
        self.titulo_evento = QLineEdit()
        self.titulo_evento.setPlaceholderText("Digite o título do evento")
        titulo_periodo_layout.addWidget(self._create_label(""))
        titulo_periodo_layout.addWidget(self.titulo_evento)

        # Período do evento (com QLabels "Início" e "Fim")
        self.inicio_evento = QDateTimeEdit(QDateTime.currentDateTime())
        self.inicio_evento.setCalendarPopup(True)
        self.fim_evento = QDateTimeEdit(QDateTime.currentDateTime())
        self.fim_evento.setCalendarPopup(True)

        periodo_layout = QVBoxLayout()
        periodo_layout.addWidget(QLabel("Início"))
        periodo_layout.addWidget(self.inicio_evento)
        periodo_layout.addWidget(QLabel("Fim"))
        periodo_layout.addWidget(self.fim_evento)
        titulo_periodo_layout.addLayout(periodo_layout)
        content_layout.addLayout(titulo_periodo_layout)

       # Convidados
        content_layout.addWidget(self._create_label("Convidados"))
        convidados_layout = QHBoxLayout()
        self.convidado_input = QLineEdit()
        self.convidado_input.setPlaceholderText("Nome do convidado")
        convidados_layout.addWidget(self.convidado_input)

        self.btn_adicionar_convidado = QPushButton("Adicionar Convidado")
        self.btn_adicionar_convidado.clicked.connect(self.adicionar_convidado)
        convidados_layout.addWidget(self.btn_adicionar_convidado)
        content_layout.addLayout(convidados_layout)

        self.lista_convidados = QListWidget()
        self.lista_convidados.setFixedHeight(200)  # Define a altura fixa em pixels
        content_layout.addWidget(self.lista_convidados)

        # Emails dos Convidados
        content_layout.addWidget(self._create_label("Emails dos Convidados"))
        email_layout = QHBoxLayout()
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Digite o email")
        email_layout.addWidget(self.email_input)

        self.btn_adicionar_email = QPushButton("Adicionar Email")
        self.btn_adicionar_email.clicked.connect(self.adicionar_email)
        email_layout.addWidget(self.btn_adicionar_email)
        content_layout.addLayout(email_layout)

        self.lista_emails = QListWidget()
        self.lista_emails.setFixedHeight(200)  # Define a altura fixa em pixels
        content_layout.addWidget(self.lista_emails)

        # Área de lembretes
        
        # Configuração da área de lembrete com os novos requisitos
        content_layout.addWidget(self._create_label("Lembretes"))
        self.lembrete_habilitar = QCheckBox("Habilitar Lembrete")
        self.lembrete_habilitar.stateChanged.connect(self.toggle_lembrete_opcoes)
        content_layout.addWidget(self.lembrete_habilitar)

        self.lembrete_opcoes_layout = QVBoxLayout()
        # Campo de frequência do lembrete
        self.lembrete_frequencia = QComboBox()
        self.lembrete_frequencia.addItems(["Seleciona a frequencia ", "Uma vez ao dia", "Todo o dia", "Dias específicos",])
        self.lembrete_frequencia.setEnabled(False)  # Começa desabilitado
        self.lembrete_frequencia.currentIndexChanged.connect(self.atualizar_opcoes_lembrete)
        self.lembrete_opcoes_layout.addWidget(self.lembrete_frequencia)

        # Campo de hora para exibição do lembrete
        self.hora_lembrete = QTimeEdit()
        self.hora_lembrete.setDisplayFormat("HH:mm")
        self.hora_lembrete.setTime(QTime.currentTime())
        self.hora_lembrete.setVisible(False)
        self.lembrete_opcoes_layout.addWidget(QLabel("Hora do Lembrete"))
        self.lembrete_opcoes_layout.addWidget(self.hora_lembrete)

        # Campo de intervalo de tempo (oculto inicialmente)
        self.intervalo_tempo = QSpinBox()
        self.intervalo_tempo.setRange(1, 24)
        self.intervalo_tempo.setVisible(False)
        self.lembrete_opcoes_layout.addWidget(QLabel("Intervalo em horas"))
        self.lembrete_opcoes_layout.addWidget(self.intervalo_tempo)
        
        # Cria o grupo de seleção dos dias da semana
        self.dias_semana_layout = QVBoxLayout()
        self.dias_semana_group = QGroupBox("Selecione os Dias da Semana")
        self.dias_semana_group.setLayout(self.dias_semana_layout)
        self.dias_semana_group.setVisible(False)  # Oculto por padrão

        # Cria checkboxes para cada dia da semana
        self.checkboxes_dias_semana = {}
        for dia in ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]:
            checkbox = QCheckBox(dia)
            self.checkboxes_dias_semana[dia] = checkbox
            self.dias_semana_layout.addWidget(checkbox)

        # Adiciona o grupo de dias da semana ao layout do lembrete
        self.lembrete_opcoes_layout.addWidget(self.dias_semana_group)
        
        # Novas caixas de seleção para "Hora" e "Intervalo" nos dias específicos
        self.especifico_hora_check = QCheckBox("Hora do Lembrete em Dias Específicos")
        self.especifico_intervalo_check = QCheckBox("Intervalo de Tempo em Dias Específicos")
        self.dias_semana_layout.addWidget(self.especifico_hora_check)
        self.dias_semana_layout.addWidget(self.especifico_intervalo_check)

        self.especifico_hora_check.stateChanged.connect(self.toggle_hora_especifica)
        self.especifico_intervalo_check.stateChanged.connect(self.toggle_intervalo_especifico)

        content_layout.addLayout(self.lembrete_opcoes_layout)
        self.toggle_lembrete_opcoes(False)
        
        # Campo: Descrição
        content_layout.addWidget(self._create_label("Descrição"))
        self.descricao_evento = QTextEdit()
        self.descricao_evento.setPlaceholderText("Digite a descrição do evento")
        self.descricao_evento.setFixedHeight(150)
        content_layout.addWidget(self.descricao_evento)

        # Botão: Salvar
        self.btn_salvar = QPushButton("Salvar Evento")
        content_layout.addWidget(self.btn_salvar)
        self.btn_salvar.clicked.connect(self.salvar_evento)

        # Configurar o layout final
        scroll_area.setWidget(content_widget)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        # Aplicar estilos
        self.setStyleSheet("""
            QDialog { background-color: #f4f4f9; border: 1px solid #d1d1d1; border-radius: 8px; }
            QLabel { color: #2c3e50; font-weight: bold; }
            QLineEdit, QTextEdit, QDateTimeEdit, QListWidget {
                background-color: white; border: 1px solid #bdc3c7; border-radius: 4px; padding: 4px;
            }
            QLineEdit::placeholder, QTextEdit::placeholder { color: #a0a0a0; }
            QPushButton {
                background-color: #2496be; color: white; border: none; padding: 8px; border-radius: 8px;
            }
            QPushButton:hover { background-color: #1f7b9a; }
            QPushButton:pressed { background-color: #14576b; }
            QCheckBox { color: #2c3e50; }
        """)

    def _create_label(self, text):
        label = QLabel(text)
        return label

    def toggle_lembrete_opcoes(self, state):
        """Exibe ou oculta campos relacionados ao lembrete baseado no checkbox de habilitação."""
        self.lembrete_opcoes_layout.setEnabled(state)
        self.lembrete_frequencia.setEnabled(state)
        self.lembrete_frequencia.setCurrentIndex(0)  # Restaura a seleção inicial
        self.intervalo_tempo.setVisible(state and self.lembrete_frequencia.currentText() in ["Uma vez ao dia", "Todo o dia"])
        
        if not state:
            self.lembrete_frequencia.setCurrentIndex(0)  # Restaura a seleção inicial
            self.hora_lembrete.setVisible(False)
            self.intervalo_tempo.setVisible(False)
            self.dias_semana_group.setVisible(False)

    # def atualizar_opcoes_lembrete(self):
    #     """Atualiza a visibilidade dos campos com base na opção de frequência do lembrete."""
    #     frequencia = self.lembrete_frequencia.currentText()
        
    #     if frequencia == "Uma vez ao dia":
    #         self.hora_lembrete.setVisible(True)
    #         self.intervalo_tempo.setVisible(False)
    #     elif frequencia == "Todo o dia":
    #         self.hora_lembrete.setVisible(False)
    #         self.intervalo_tempo.setVisible(True)
    #     elif frequencia == "Dias específicos":
    #         self.dias_semana_group.setVisible(True)
    #         self.hora_lembrete.setVisible(True)
    #         self.intervalo_tempo.setVisible(True)
    #         # Apenas um dos campos pode estar selecionado
    #         self.intervalo_tempo.valueChanged.connect(lambda: self.hora_lembrete.setVisible(False))
    #         self.hora_lembrete.timeChanged.connect(lambda: self.intervalo_tempo.setVisible(False))
    #     else:
    #         self.hora_lembrete.setVisible(False)
    #         self.intervalo_tempo.setVisible(False)
    #         self.dias_semana_group.setVisible(False)

    def atualizar_opcoes_lembrete(self):
            """Atualiza campos com base na frequência."""
            frequencia = self.lembrete_frequencia.currentText()
            
            if frequencia == "Uma vez ao dia":
                self.hora_lembrete.setVisible(True)
                self.intervalo_tempo.setVisible(False)
                self.dias_semana_group.setVisible(False)
            elif frequencia == "Todo o dia":
                self.hora_lembrete.setVisible(False)
                self.intervalo_tempo.setVisible(True)
                self.dias_semana_group.setVisible(False)
            elif frequencia == "Dias específicos":
                self.dias_semana_group.setVisible(True)
                self.hora_lembrete.setVisible(False)
                self.intervalo_tempo.setVisible(False)
                self.especifico_hora_check.setChecked(False)
                self.especifico_intervalo_check.setChecked(False)
            else:
                self.hora_lembrete.setVisible(False)
                self.intervalo_tempo.setVisible(False)
                self.dias_semana_group.setVisible(False)

    def toggle_hora_especifica(self, state):
        """Alterna a visibilidade do campo de hora para dias específicos."""
        if state:
            self.especifico_intervalo_check.setChecked(False)
            self.hora_lembrete.setVisible(True)
            self.intervalo_tempo.setVisible(False)
        else:
            self.hora_lembrete.setVisible(False)

    def toggle_intervalo_especifico(self, state):
        """Alterna a visibilidade do campo de intervalo para dias específicos."""
        if state:
            self.especifico_hora_check.setChecked(False)
            self.intervalo_tempo.setVisible(True)
            self.hora_lembrete.setVisible(False)
        else:
            self.intervalo_tempo.setVisible(False)
     
    def remover_convidado(self, item):
        """Remove o convidado selecionado na lista de convidados."""
        self.lista_convidados.takeItem(self.lista_convidados.row(item))

    def remover_email(self, item):
        """Remove o email selecionado na lista de emails."""
        self.lista_emails.takeItem(self.lista_emails.row(item))

    def _adicionar_item_lista(self, lista, texto):
        item_widget = QWidget()
        layout = QHBoxLayout()
        
        # Texto do item
        item_texto = QLabel(f"{lista.count() + 1}. {texto}")
        layout.addWidget(item_texto)

        # Botão de exclusão com ícone 'X'
        btn_remover = QPushButton("X")
        btn_remover.setFixedSize(20, 20)
        btn_remover.setStyleSheet("color white; background: red;")
        btn_remover.clicked.connect(lambda: self._remover_item(lista, item_widget))
        layout.addWidget(btn_remover)

        item_widget.setLayout(layout)
        item = QListWidgetItem(lista)
        item.setSizeHint(item_widget.sizeHint())
        lista.addItem(item)
        lista.setItemWidget(item, item_widget)

    def _remover_item(self, lista, item_widget):
        for i in range(lista.count()):
            if lista.itemWidget(lista.item(i)) == item_widget:
                lista.takeItem(i)
                break

    def adicionar_convidado(self):
        nomes = self.convidado_input.text().strip()
        if not nomes:
            return

        nomes_separados = re.split(r',|;', nomes)
        for nome in nomes_separados:
            nome = nome.strip()
            if len(nome) < 3:
                QMessageBox.warning(self, "Erro de Validação", f"O nome '{nome}' é inválido. Deve conter pelo menos 3 letras.")
                continue
            self._adicionar_item_lista(self.lista_convidados, nome)
        
        self.convidado_input.clear()

    def adicionar_email(self):
        emails = self.email_input.text().strip()
        if not emails:
            return

        emails_separados = re.split(r',|;', emails)
        regex_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        for email in emails_separados:
            email = email.strip()
            if not re.match(regex_email, email):
                QMessageBox.warning(self, "Erro de Validação", f"O email '{email}' é inválido.")
                continue
            self._adicionar_item_lista(self.lista_emails, email)
        
        self.email_input.clear()

    def verificar_frequencia(self):
        """Exibe o campo de intervalo se a frequência for 'Intervalo de horas'."""
        if self.lembrete_frequencia.currentText() == "Intervalo de horas":
            self.intervalo_tempo.setEnabled(True)
        else:
            self.intervalo_tempo.setEnabled(False)

    def formatar_data(self, datetime_obj):
        """Formata a data no padrão desejado, incluindo segundos."""
        dias_semana = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
        
        # Converter QDateTime para datetime
        if isinstance(datetime_obj, QDateTime):
            datetime_obj = datetime_obj.toPython()  # Converte para datetime do Python

        # Obter o índice do dia da semana usando weekday()
        dia_semana = dias_semana[datetime_obj.weekday()]
        
        # Formato: DD-MM-YYYY - Nome do Dia - HH:mm:ss
        return f"{datetime_obj.strftime('%d-%m-%Y')} - {dia_semana} - {datetime_obj.strftime('%H:%M:%S')}"

    
    def salvar_evento(self):
        try:
            """Salva o evento em um arquivo JSON com ID único e configurações de lembrete atualizadas."""
            if not self.validar_dados():
                return

            # Gera um ID único para o evento
            evento_id = str(uuid.uuid4())
            data_criacao = self.formatar_data(datetime.now())
            """Salva o evento em um arquivo JSON com validações de dados e status automático."""
        
            # Formata as datas
            data_inicio = self.inicio_evento.dateTime()
            data_fim = self.fim_evento.dateTime()

            # Verifica se a data de início é anterior à data de fim
            if data_inicio >= data_fim:
                QMessageBox.warning(self, "Erro de Validação", "A data de início deve ser anterior à data de fim.")
                return

            try:
                status = "pendente" if data_fim > data_criacao else "concluído"
            except NotImplementedError:
                print("Erro: Comparação entre datas não implementada.")
                status = "indefinido"

            # Dados principais do evento
            evento_data = {
                "id": evento_id,
                "titulo": self.titulo_evento.text(),
                "descricao": self.descricao_evento.toPlainText(),
                "data_inicio": self.formatar_data(data_inicio),
                "data_fim": self.formatar_data(data_fim),
                "data_criacao": data_criacao,
                "status": status,
                "convidados": [self.lista_convidados.item(i).text().split(". ", 1)[1] for i in range(self.lista_convidados.count())],
                "emails": [self.lista_emails.item(i).text().split(". ", 1)[1] for i in range(self.lista_emails.count())],
                "localizacao": self.localizacao_evento.text(),
                "lembrete": {
                    "habilitado": self.lembrete_habilitar.isChecked(),
                    "frequencia": self.lembrete_frequencia.currentText() if self.lembrete_habilitar.isChecked() else None,
                },
            }

            # Configuração de lembrete se estiver habilitado
            if evento_data["lembrete"]["habilitado"]:
                # Configuração da frequência de lembrete
                frequencia = evento_data["lembrete"]["frequencia"]

                # Ajuste de hora e intervalo de lembrete para "Dias específicos"
                if frequencia == "Dias específicos":
                    dias_selecionados = [
                        dia for dia, checkbox in self.checkboxes_dias_semana.items() if checkbox.isChecked()
                    ]
                    evento_data["lembrete"]["dias_especificos"] = dias_selecionados if dias_selecionados else None

                    if self.hora_lembrete.isVisible():
                        evento_data["lembrete"]["hora_lembrete"] = self.hora_lembrete.time().toString("HH:mm")
                        evento_data["lembrete"]["intervalo_tempo"] = None
                    elif self.intervalo_tempo.isVisible():
                        evento_data["lembrete"]["intervalo_tempo"] = self.intervalo_tempo.value()
                        evento_data["lembrete"]["hora_lembrete"] = None

                # Configuração de outras frequências de lembrete
                else:
                    evento_data["lembrete"]["hora_lembrete"] = (
                        self.hora_lembrete.time().toString("HH:mm") if self.hora_lembrete.isVisible() else None
                    )
                    evento_data["lembrete"]["intervalo_tempo"] = (
                        self.intervalo_tempo.value() if self.intervalo_tempo.isVisible() else None
                    )

            # Caminho do arquivo JSON de eventos
            caminho_arquivo = os.path.join(BASE_DIR_Calendario, pastas_calendario["eventos"], "eventos.json")
            os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)

     
            # Carrega eventos existentes (se houver)
            eventos = []
            if os.path.exists(caminho_arquivo):
                with open(caminho_arquivo, "r", encoding="utf-8") as f:
                    eventos = json.load(f)
            
            # Adiciona o novo evento com ID único
            eventos.append(evento_data)
            
            # Salva todos os eventos no arquivo JSON
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                json.dump(eventos, f, indent=4, ensure_ascii=False)
            
            QMessageBox.information(self, "Sucesso", "Evento salvo com sucesso!")
            self.close()
        except Exception as e:
            self.log_erro(f"Erro ao salvar evento: {e}")
            QMessageBox.critical(self, "Erro", "Ocorreu um erro ao salvar o evento. Verifique os logs para mais detalhes.")

    def validar_dados(self):
        """Valida os dados antes de salvar o evento."""
        # Verificar se o título está preenchido
        if not self.titulo_evento.text().strip():
            QMessageBox.warning(self, "Erro de Validação", "O título do evento é obrigatório.")
            return False

        # Regex para validar o formato de e-mail
        regex_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        # Verificar se a lista de emails é válida
        for i in range(self.lista_emails.count()):
            # Obter o item do QListWidget
            item = self.lista_emails.item(i)
            item_widget = self.lista_emails.itemWidget(item)

            # Obter o texto do QLabel dentro do item_widget
            item_label = item_widget.layout().itemAt(0).widget()
            if isinstance(item_label, QLabel):
                item_text = item_label.text().strip()
            else:
                QMessageBox.warning(self, "Erro de Validação", "Formato do item na lista de emails está incorreto.")
                return False

            # Verificar se o item segue o formato esperado com ". "
            if ". " in item_text:
                email = item_text.split(". ", 1)[1]
            else:
                QMessageBox.warning(self, "Erro de Validação", f"O item '{item_text}' está fora do formato esperado.")
                return False

            # Validar o formato do e-mail
            if not re.match(regex_email, email):
                QMessageBox.warning(self, "Erro de Validação", f"O email '{email}' é inválido.")
                return False

        # Verificar se a data de início é anterior à data de fim
        if self.inicio_evento.dateTime() >= self.fim_evento.dateTime():
            QMessageBox.warning(self, "Erro de Validação", "A data de início deve ser anterior à data de fim.")
            return False

        return True

    def log_erro(self, message):
        """Registra mensagens de erro no arquivo de log com traceback completo."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - ERROR - {message}\n")
                log_file.write(traceback.format_exc() + "\n")
        except Exception as e:
            print(f"Erro ao registrar log: {e}")

class ModalTarefa(QDialog):
    def __init__(self, LOG_DIR_Calendario=LOG_DIR_Calendario):
        super().__init__()
        if not os.path.exists(LOG_DIR_Calendario ):
            os.makedirs(LOG_DIR_Calendario )
        self.log_file = os.path.join(LOG_DIR_Calendario, "Logs_Tarefa.log")
        
        self.setWindowTitle("Adicionar Tarefa")
        self.setMinimumWidth(300)

        # Layout
        layout = QVBoxLayout()

        # Campo: Título da tarefa
        layout.addWidget(QLabel("Título da Tarefa:"))
        self.titulo_tarefa = QLineEdit()
        layout.addWidget(self.titulo_tarefa)

        # Campo: Descrição
        layout.addWidget(QLabel("Descrição:"))
        self.descricao_tarefa = QTextEdit()
        layout.addWidget(self.descricao_tarefa)

        # Campo: Prazo da Tarefa
        layout.addWidget(QLabel("Prazo da Tarefa:"))
        self.prazo_tarefa = QDateTimeEdit(QDateTime.currentDateTime())
        self.prazo_tarefa.setCalendarPopup(True)
        layout.addWidget(self.prazo_tarefa)

        # Campo: Notificação de Lembrete
        self.lembrete_tarefa = QCheckBox("Habilitar lembrete")
        layout.addWidget(self.lembrete_tarefa)

        # Botão: Salvar
        self.btn_salvar = QPushButton("Salvar Tarefa")
        layout.addWidget(self.btn_salvar)

        self.setLayout(layout)
        
    def log_erro(self, message):
        """Registra mensagens de erro no arquivo de log com traceback completo."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - ERROR - {message}\n")
                log_file.write(traceback.format_exc() + "\n")
        except Exception as e:
            print(f"Erro ao registrar log: {e}")
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt

class EmailEnviado(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Tabela para mostrar os e-mails enviados
        self.tabela_emails_enviados = QTableWidget()
        self.tabela_emails_enviados.setColumnCount(4)  # Colunas para Remetente, Assunto, Data, Status
        self.tabela_emails_enviados.setHorizontalHeaderLabels(["Destinatário", "Assunto", "Data", "Status"])
        self.tabela_emails_enviados.horizontalHeader().setStretchLastSection(True)  # A última coluna se ajusta

       # Estilo da tabela
        self.tabela_emails_enviados.setStyleSheet("""
            QTableWidget {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #00152a, stop: 1 #0d3c55
                );
                color: white;                /* Cor do texto */
                border-radius: 7px;
                border: 2px solid #2496be;
            }
            QTableWidget::item {
                background-color: none;   /* Fundo das células */
                border-bottom: 2px solid #2496be;   /* Borda das células */
                border-top: none;   /* Borda das células */
                border-left: none;   /* Borda das células */
                border-right: none;   /* Borda das células */
            }
            QTableWidget::item:selected {
                background-color: #2496be;   /* Fundo das células selecionadas */
                color: black;                /* Cor do texto selecionado */
            }
            QHeaderView::section {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #00152a, stop: 1 #0d3c55
                );  /* Gradiente de azul escuro para azul médio */
                color: #2496be;  /* Azul claro */
                font-size: 14px;             /* Tamanho da fonte */
                padding: 3px; 
                border: 2px solid #2496be;   /* Borda das células */
                border-left: none;
                border-right: none;
                border-top: none;
            }
            /* Estilo da barra de rolagem vertical */
            QScrollBar:vertical {
                background-color: none; /* Fundo da barra de rolagem */
                width: 13px;
                margin: 3px 0px 3px 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #2496be; /* Cor da barra de rolagem */
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
            /* Estilo da barra de rolagem horizontal */
            QScrollBar:horizontal {
                background-color: none; /* Fundo da barra de rolagem */
                height: 15px;
                margin: 0px 3px 0px 3px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background-color: #2496be; /* Cor da barra de rolagem */
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                background: none;
            }
        """)
        self.tabela_emails_enviados.setSelectionBehavior(QTableWidget.SelectRows)  # Selecionar linhas inteiras
        layout.addWidget(self.tabela_emails_enviados)
        self.setLayout(layout)

    def carregar_emails_enviados(self, emails):
        """Carrega e exibe os e-mails enviados na tabela."""
        self.tabela_emails_enviados.setRowCount(len(emails))
        for row, email in enumerate(emails):
            self.tabela_emails_enviados.setItem(row, 0, QTableWidgetItem(email["destinatario"]))
            self.tabela_emails_enviados.setItem(row, 1, QTableWidgetItem(email["assunto"]))
            self.tabela_emails_enviados.setItem(row, 2, QTableWidgetItem(email["data"]))
            self.tabela_emails_enviados.setItem(row, 3, QTableWidgetItem(email["status"]))
            # Definir o alinhamento central para as colunas da tabela
            for col in range(4):
                self.tabela_emails_enviados.item(row, col).setTextAlignment(Qt.AlignCenter)

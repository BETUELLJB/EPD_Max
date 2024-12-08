from config.config import BASE_DIR_Tarefa, LOG_DIR_Tarefa, PASTAS_Tarefa
import os
import json
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout,
    QDialog, QLineEdit, QComboBox, QDateEdit, QMessageBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QDate
import uuid
import traceback


class Tarefa(QWidget):
    def __init__(self, BASE_DIR_Tarefa=BASE_DIR_Tarefa, LOG_DIR_Tarefa=LOG_DIR_Tarefa):
        super().__init__()

        self.tasks_file = os.path.join(BASE_DIR_Tarefa, PASTAS_Tarefa["tarefas"], "tasks.json")
        self.log_file = os.path.join(LOG_DIR_Tarefa, "logs_tarefa.log")

        # Configuração de arquivos
        self._inicializar_arquivos()

        # Layout da página
        layout = QVBoxLayout()
        label = QLabel("Tarefas")
        label.setStyleSheet("font-size: 18px; color: white;")
        layout.addWidget(label)

        add_button = QPushButton("Adicionar Tarefa")
        add_button.clicked.connect(self.open_create_task_dialog)
        layout.addWidget(add_button)

        self.table = QTableWidget(0, 6)  # Agora com 6 colunas
        self.table.setHorizontalHeaderLabels(["Título", "Descrição", "Prioridade", "Data de Vencimento", "Lembrete", "Ações"])
        self.table.cellDoubleClicked.connect(self.open_view_task_dialog)
        # Estilo da tabela
        self.table.setStyleSheet("""
            QTableWidget {
               /* background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #00152a, stop: 1 #0d3c55
                ); */
                background-color: transparent;
                color: white;                /* Cor do texto */
                border-radius: 7px;
                border: 2px solid #2496be;
            }
            QTableWidget::item {
                background-color: none;   /* Fundo das células */
                border-bottom: 1px solid #2496be;   /* Borda das células */
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
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # Selecionar linhas inteiras
    
        layout.addWidget(self.table)

        self.setLayout(layout)
        self._verificar_estrutura_arquivos()  # Verifica e cria diretórios e arquivo de tarefas
        self.load_tasks()
        self.check_reminders()

    def _inicializar_arquivos(self):
        """Configura diretórios e arquivos de log."""
        os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
        os.makedirs(LOG_DIR_Tarefa, exist_ok=True)
        
        # Cria o arquivo JSON vazio se ele não existir
        if not os.path.isfile(self.tasks_file):
            with open(self.tasks_file, 'w') as file:
                json.dump([], file)

    def _verificar_estrutura_arquivos(self):
        """Verifica e cria a estrutura de pastas e o arquivo de tarefas."""
        os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)  # Garante que o diretório de tarefas existe
        
        if not os.path.isfile(self.tasks_file):
            with open(self.tasks_file, 'w') as file:
                json.dump([], file)  # Inicializa o arquivo com uma lista vazia

    def load_tasks(self):
        """Carrega as tarefas do arquivo JSON e exibe na tabela."""
        try:
            with open(self.tasks_file, "r") as file:
                tasks = json.load(file)
                self.table.setRowCount(0)
                for task in tasks:
                    self.add_task_to_table(task)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.log_error(f"Erro ao carregar tarefas: {e}")

    def add_task_to_table(self, task):
        """Adiciona uma tarefa à tabela com botões de ação."""
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        
        # Define os itens de tarefa na tabela
        self.table.setItem(row_position, 0, QTableWidgetItem(task.get("title", "")))
        self.table.setItem(row_position, 1, QTableWidgetItem(task.get("description", "")))
        self.table.setItem(row_position, 2, QTableWidgetItem(task.get("priority", "")))
        self.table.setItem(row_position, 3, QTableWidgetItem(task.get("due_date", "")))
        self.table.setItem(row_position, 4, QTableWidgetItem(task.get("reminder", {}).get("category", "")))
        self.table.item(row_position, 0).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table.item(row_position, 1).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table.item(row_position, 2).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table.item(row_position, 3).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table.item(row_position, 4).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)


        # Botões de ação com ícones
        edit_button = QPushButton()
        edit_button.setIcon(QIcon("icons/edit_icon.png"))  # Caminho do ícone de edição
        edit_button.clicked.connect(lambda _, row=row_position: self.open_edit_task_dialog(row))

        view_button = QPushButton()
        view_button.setIcon(QIcon("icons/view_icon.png"))  # Caminho do ícone de visualização
        view_button.clicked.connect(lambda _, row=row_position: self.open_view_task_dialog(row))

        delete_button = QPushButton()
        delete_button.setIcon(QIcon("icons/delete_icon.png"))  # Caminho do ícone de exclusão
        delete_button.clicked.connect(lambda _, row=row_position: self.delete_task(row))

        # Layout dos botõe
        button_layout = QHBoxLayout()
        button_layout.addWidget(edit_button)
        button_layout.addWidget(view_button)
        button_layout.addWidget(delete_button)

        container_widget = QWidget()
        container_widget.setLayout(button_layout)
        self.table.setCellWidget(row_position, 5, container_widget)  # Define os botões na coluna de ações


    def open_create_task_dialog(self):
        dialog = CreateTaskDialog(self)
        if dialog.exec() == QDialog.Accepted:
            task_data = dialog.get_task_data()
            self.save_task(task_data)
            self.load_tasks()

    def open_edit_task_dialog(self, row):
        try:
            with open(self.tasks_file, "r") as file:
                tasks = json.load(file)
                task = tasks[row]

            dialog = EditTaskDialog(self)
            dialog.load_data(task)
            
            if dialog.exec() == QDialog.Accepted:
                updated_task = dialog.get_task_data()
                self.update_task(updated_task, row)
                self.load_tasks()
        except Exception as e:
            self.log_error(f"Erro ao abrir o diálogo de edição: {e}")


    def open_view_task_dialog(self, row, column):
        try:
            with open(self.tasks_file, "r") as file:
                tasks = json.load(file)
                task = tasks[row]

            dialog = ViewTaskDialog(task, self)
            dialog.exec()
        except Exception as e:
            self.log_error(f"Erro ao abrir o diálogo de visualização: {e}")

    def save_task(self, task_data):
        """Salva uma nova tarefa no arquivo JSON, incluindo um ID único e data de criação."""
        try:
            if not os.path.exists(self.tasks_file):
                tasks = []
            else:
                with open(self.tasks_file, "r") as file:
                    tasks = json.load(file)

            # Gerar ID único e data de criação para a nova tarefa
            task_data["id"] = str(uuid.uuid4())
            task_data["created_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            tasks.append(task_data)
            with open(self.tasks_file, "w") as file:
                json.dump(tasks, file, indent=4)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.log_error(f"Erro ao salvar tarefa: {e}")


    def update_task(self, task_data, row):
        """Atualiza uma tarefa existente com base em seu índice na lista."""
        try:
            with open(self.tasks_file, "r+") as file:
                tasks = json.load(file)

                # Atualiza a tarefa com base no índice fornecido
                tasks[row] = task_data

                file.seek(0)
                file.truncate()
                json.dump(tasks, file, indent=4)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.log_error(f"Erro ao atualizar tarefa: {e}")


    def delete_task(self, row):
        """Exclui uma tarefa do arquivo JSON e atualiza a tabela."""
        try:
            with open(self.tasks_file, "r+") as file:
                tasks = json.load(file)
                del tasks[row]
                file.seek(0)
                file.truncate()
                json.dump(tasks, file, indent=4)
            self.table.removeRow(row)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.log_error(f"Erro ao excluir tarefa: {e}")

    def log_error(self, message):
        """Registra mensagens de erro no arquivo de log com traceback completo."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR - {message}\n")
                # Adiciona o traceback completo se houver uma exceção ativa
                log_file.write(traceback.format_exc() + "\n")
        except Exception as e:
            print(f"Erro ao registrar log: {e}")

    def check_reminders(self):
        """Verifica lembretes e notifica o usuário."""
        try:
            with open(self.tasks_file, "r") as file:
                tasks = json.load(file)

            for task in tasks:
                reminder = task.get("reminder", {})
                reminder_status = reminder.get("reminder_status", "active")
                due_date = QDate.fromString(task["due_date"], "dd-MM-yyyy")
                days_left = QDate.currentDate().daysTo(due_date)

                if reminder_status == "disabled":
                    continue
                if reminder_status == "snoozed_until":
                    snooze_date = datetime.strptime(reminder["snoozed_until"], '%Y-%m-%d').date()
                    if datetime.now().date() < snooze_date:
                        continue

                if reminder["category"] == "Diário" and days_left <= reminder["days_before_due_date"]:
                    self.notify_user(task)
                elif reminder["category"] == "Agressivo" and days_left <= reminder["days_before_due_date"]:
                    last_reminder = reminder.get("last_reminder")
                    if not last_reminder or (datetime.now() - last_reminder).total_seconds() > reminder["frequency_hours"] * 3600:
                        self.notify_user(task)
                        task["reminder"]["last_reminder"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(self.tasks_file, "w") as file:
                json.dump(tasks, file, indent=4)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.log_error(f"Erro ao verificar lembretes: {e}")

    def notify_user(self, task):
        """Notifica o usuário com um lembrete."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Lembrete de Tarefa")
        msg_box.setText(f"Tarefa '{task['title']}' está próxima do vencimento!")

        disable_button = msg_box.addButton("Desativar Lembrete", QMessageBox.RejectRole)
        snooze_button = msg_box.addButton("Suspender", QMessageBox.ActionRole)
        ok_button = msg_box.addButton("OK", QMessageBox.AcceptRole)

        msg_box.exec()

        if msg_box.clickedButton() == disable_button:
            task["reminder"]["reminder_status"] = "disabled"
            self.save_task_data(task)
        elif msg_box.clickedButton() == snooze_button:
            self.snooze_reminder(task)

    def snooze_reminder(self, task):
        """Suspende o lembrete por um período determinado."""
        snooze_msg = QMessageBox(self)
        snooze_msg.setWindowTitle("Suspender Lembrete")
        snooze_msg.setText("Por quantos dias deseja suspender o lembrete?")
        snooze_options = {"1 dia": 1, "3 dias": 3, "7 dias": 7}
        for label in snooze_options.keys():
            snooze_msg.addButton(label, QMessageBox.ActionRole)

        snooze_msg.exec()
        clicked_button_text = snooze_msg.clickedButton().text()
        days = snooze_options.get(clicked_button_text, 1)

        new_date = datetime.now() + timedelta(days=days)
        task["reminder"]["reminder_status"] = "snoozed_until"
        task["reminder"]["snoozed_until"] = new_date.strftime('%Y-%m-%d')
        
        self.save_task_data(task)

    def save_task_data(self, task):
        """Salva dados da tarefa atualizados."""
        try:
            with open(self.tasks_file, "r+") as file:
                tasks = json.load(file)
                for i, t in enumerate(tasks):
                    if t["title"] == task["title"]:
                        tasks[i] = task
                        break
                file.seek(0)
                file.truncate()
                json.dump(tasks, file, indent=4)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.log_error(f"Erro ao salvar dados da tarefa: {e}")


class CreateTaskDialog(QDialog):
    """Modal para criar uma nova tarefa."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nova Tarefa")
        
        # Campos de entrada
        self.title_input = QLineEdit()
        self.description_input = QLineEdit()
        self.priority_input = QComboBox()
        self.priority_input.addItems(["Baixa", "Média", "Alta"])
        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDate(QDate.currentDate())
        
        # Exibição do ID e da Data de Criação
        self.id_label = QLabel(f"ID: {str(uuid.uuid4())}")
        self.created_at_label = QLabel(f"Data de Criação: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        
        # Campos de lembrete
        self.reminder_input = QComboBox()
        self.reminder_input.addItems(["Nenhum", "Diário", "Agressivo"])
        self.days_before_due_input = QLineEdit("1")
        self.frequency_hours_input = QLineEdit("24")
        
        # Botão de salvar
        save_button = QPushButton("Salvar")
        save_button.clicked.connect(self.accept)
        
        # Layout do modal
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Título"))
        layout.addWidget(self.title_input)
        layout.addWidget(QLabel("Descrição"))
        layout.addWidget(self.description_input)
        layout.addWidget(QLabel("Prioridade"))
        layout.addWidget(self.priority_input)
        layout.addWidget(QLabel("Data de Vencimento"))
        layout.addWidget(self.due_date_input)
        layout.addWidget(self.id_label)  # Mostra o ID gerado
        layout.addWidget(self.created_at_label)  # Mostra a data de criação
        layout.addWidget(QLabel("Lembrete"))
        layout.addWidget(self.reminder_input)
        layout.addWidget(QLabel("Dias Antes do Vencimento"))
        layout.addWidget(self.days_before_due_input)
        layout.addWidget(QLabel("Frequência de Lembrete (Horas)"))
        layout.addWidget(self.frequency_hours_input)
        layout.addWidget(save_button)
        
        self.setLayout(layout)

    def get_task_data(self):
        """Retorna os dados da tarefa do modal."""
        return {
            "id": self.id_label.text().split(": ")[1],
            "created_at": self.created_at_label.text().split(": ")[1],
            "title": self.title_input.text(),
            "description": self.description_input.text(),
            "priority": self.priority_input.currentText(),
            "due_date": self.due_date_input.date().toString("dd-MM-yyyy"),
            "reminder": {
                "category": self.reminder_input.currentText(),
                "days_before_due_date": int(self.days_before_due_input.text() or 1),
                "frequency_hours": int(self.frequency_hours_input.text() or 24),
                "reminder_status": "active"
            }
        }


class EditTaskDialog(CreateTaskDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Tarefa")

    def load_data(self, task):
        """Carrega dados de uma tarefa existente."""
        self.title_input.setText(task["title"])
        self.description_input.setText(task["description"])
        self.priority_input.setCurrentText(task["priority"])
        self.due_date_input.setDate(QDate.fromString(task["due_date"], "dd-MM-yyyy"))
        self.reminder_input.setCurrentText(task["reminder"]["category"])
        self.days_before_due_input.setText(str(task["reminder"]["days_before_due_date"]))
        self.frequency_hours_input.setText(str(task["reminder"]["frequency_hours"]))

class ViewTaskDialog(QDialog):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visualizar Tarefa")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Título:"))
        title_label = QLabel(task["title"])
        layout.addWidget(title_label)

        layout.addWidget(QLabel("Descrição:"))
        description_label = QLabel(task["description"])
        layout.addWidget(description_label)

        layout.addWidget(QLabel("Prioridade:"))
        priority_label = QLabel(task["priority"])
        layout.addWidget(priority_label)

        layout.addWidget(QLabel("Data de Vencimento:"))
        due_date_label = QLabel(task["due_date"])
        layout.addWidget(due_date_label)

        layout.addWidget(QLabel("Lembrete:"))
        reminder_label = QLabel(task["reminder"]["category"])
        layout.addWidget(reminder_label)

        self.setLayout(layout)

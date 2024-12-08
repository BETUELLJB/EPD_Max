from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCalendarWidget, QListWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import QDate

class Agenda(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Título
        label = QLabel("Agendas")
        label.setStyleSheet("font-size: 18px; color: white;")
        main_layout.addWidget(label)
        
        # Calendário para selecionar datas
        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet("background-color: #0d3c55; color: white;")
        main_layout.addWidget(self.calendar)
        
        # Filtros para visualização (Dia, Semana, Mês)
        filter_layout = QHBoxLayout()
        day_button = QPushButton("Dia")
        week_button = QPushButton("Semana")
        month_button = QPushButton("Mês")
        
        for button in (day_button, week_button, month_button):
            button.setStyleSheet("background-color: #007acc; color: white;")
            filter_layout.addWidget(button)
        
        main_layout.addLayout(filter_layout)
        
        # Lista para exibir os eventos
        self.event_list = QListWidget()
        self.event_list.setStyleSheet("background-color: #00152a; color: white;")
        main_layout.addWidget(self.event_list)
        
        # Configuração do layout da janela
        self.setLayout(main_layout)
        
        # Conectar os filtros e o calendário a métodos
        self.calendar.selectionChanged.connect(self.update_events)
        day_button.clicked.connect(lambda: self.update_events("day"))
        week_button.clicked.connect(lambda: self.update_events("week"))
        month_button.clicked.connect(lambda: self.update_events("month"))
        
        # Dados de exemplo de eventos
        self.events = {
            QDate.currentDate().toString("yyyy-MM-dd"): ["Evento 1", "Evento 2"],
            QDate.currentDate().addDays(1).toString("yyyy-MM-dd"): ["Evento 3"],
            QDate.currentDate().addDays(7).toString("yyyy-MM-dd"): ["Evento 4"],
        }
        
        # Atualizar eventos iniciais
        self.update_events("day")

    def update_events(self, filter_type="day"):
        """Atualiza a lista de eventos com base no filtro selecionado."""
        self.event_list.clear()
        selected_date = self.calendar.selectedDate()
        
        if filter_type == "day":
            # Exibe eventos do dia selecionado
            events = self.events.get(selected_date.toString("yyyy-MM-dd"), [])
            self.event_list.addItems(events)
        
        elif filter_type == "week":
            # Exibe eventos da semana atual
            start_date = selected_date.addDays(-selected_date.dayOfWeek() + 1)
            for i in range(7):
                day = start_date.addDays(i).toString("yyyy-MM-dd")
                events = self.events.get(day, [])
                if events:
                    self.event_list.addItem(f"Dia {start_date.addDays(i).toString('yyyy-MM-dd')}:")
                    self.event_list.addItems(events)
                    self.event_list.addItem("")  # Espaço entre dias
        
        elif filter_type == "month":
            # Exibe eventos do mês atual
            year = selected_date.year()
            month = selected_date.month()
            for day in range(1, selected_date.daysInMonth() + 1):
                day_date = QDate(year, month, day).toString("yyyy-MM-dd")
                events = self.events.get(day_date, [])
                if events:
                    self.event_list.addItem(f"Dia {day_date}:")
                    self.event_list.addItems(events)
                    self.event_list.addItem("")  # Espaço entre dias

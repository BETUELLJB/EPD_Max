from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QSizePolicy,
    QListWidgetItem
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QTimer
import requests
import feedparser
import webbrowser

class Home(QWidget):
    def __init__(self):
        super().__init__()
        self.api_key = "S2064f304fa63035d64582f37aa73a65a"  # Sua API Key do OpenWeatherMap
        self.inicializar_ui()
        self.atualizar_noticias()
        self.atualizar_clima()

    def inicializar_ui(self):
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(10, 10, 10, 10)

        # Navbar - Informações do Sistema
        navbar = QHBoxLayout()
        estilo_navbar = """
            background-color: #34495E;
            padding: 10px;
            font-size: 14px;
            color: white;
            border-radius: 5px;
        """
        self.lbl_cpu = QLabel("CPU: Obtendo...")
        self.lbl_ram = QLabel("RAM: Obtendo...")
        self.lbl_gpu = QLabel("GPU: Obtendo...")
        self.lbl_bateria = QLabel("Bateria: Obtendo...")

        for lbl in [self.lbl_cpu, self.lbl_ram, self.lbl_gpu, self.lbl_bateria]:
            lbl.setStyleSheet(estilo_navbar)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            navbar.addWidget(lbl)

        # Área Central Placeholder
        lbl_centro = QLabel("Área Central - Funcionalidades futuras")
        lbl_centro.setAlignment(Qt.AlignCenter)
        lbl_centro.setStyleSheet("font-size: 18px; color: #1ABC9C; font-weight: bold;")
        lbl_centro.setFixedHeight(200)

        # Rodapé - Notícias e Clima
        rodape = QHBoxLayout()
        estilo_rodape_caixa = """
            background-color: #1A252F;
            border: 1px solid #1ABC9C;
            border-radius: 10px;
            padding: 10px;
        """

        # Categorias de Notícias
        categorias = ["Notícias Gerais", "Esportes", "Tecnologia"]
        urls_feeds = [
            "https://g1.globo.com/rss/g1/",
            "https://ge.globo.com/rss",
            "https://feeds.feedburner.com/tecmundo"
          
        ]

        self.lista_feeds = []
        self.urls_feeds = urls_feeds

        # Painel de Notícias
        painel_noticias = QHBoxLayout()
        for i, categoria in enumerate(categorias):
            painel_noticia = QVBoxLayout()
            lbl_noticia = QLabel(categoria)
            lbl_noticia.setStyleSheet("font-size: 14px; font-weight: bold; color: lightblue;")

            lista_noticia = QListWidget()
            lista_noticia.setStyleSheet(estilo_rodape_caixa)
            lista_noticia.setMinimumHeight(150)
            lista_noticia.itemDoubleClicked.connect(self.abrir_link_noticia)

            # Armazenar listas e URLs para atualização posterior
            self.lista_feeds.append(lista_noticia)

            painel_noticia.addWidget(lbl_noticia)
            painel_noticia.addWidget(lista_noticia)
            painel_noticias.addLayout(painel_noticia)

        
        # Caixa de Clima
        painel_clima = QVBoxLayout()
        lbl_clima = QLabel("Previsão do Tempo")
        lbl_clima.setStyleSheet("font-size: 14px; font-weight: bold; color: lightblue;")
        self.lbl_clima = QLabel("Obtendo informações...")
        self.lbl_clima.setStyleSheet(estilo_rodape_caixa)
        
        # Configurando o QSizePolicy para o clima
        self.lbl_clima.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.lbl_clima.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        painel_clima.addWidget(lbl_clima)
        painel_clima.addWidget(self.lbl_clima)

        # Adicionar os painéis de notícias e clima ao rodapé
        rodape.addLayout(painel_noticias, stretch=3)
        rodape.addLayout(painel_clima, stretch=1)

        
        # Adicionar componentes ao layout principal
        layout_principal.addLayout(navbar)
        layout_principal.addWidget(lbl_centro)
        layout_principal.addLayout(rodape)

        self.setLayout(layout_principal)
        self.setStyleSheet("background-color: #2C3E50; color: white;")

        # Timer para troca de notícias
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.atualizar_noticias)
        self.timer.start(120000)



    def atualizar_noticias(self):
        """Atualiza as listas de notícias usando feeds RSS por categoria."""
        max_noticias = 5

        for i, url_feed in enumerate(self.urls_feeds):
            lista_noticia = self.lista_feeds[i]
            lista_noticia.clear()
            feed = feedparser.parse(url_feed)

            for entrada in feed.entries[:max_noticias]:
                titulo = entrada.title
                link = entrada.link

                # Busca a imagem no feed RSS
                imagem_url = ""
                if "media_content" in entrada:
                    imagem_url = entrada.media_content[0]['url']
                elif "enclosure" in entrada:
                    imagem_url = entrada.enclosure.get('url', '')

                # Baixa a imagem
                imagem_pixmap = QPixmap()
                if imagem_url:
                    try:
                        resposta_imagem = requests.get(imagem_url)
                        imagem_pixmap.loadFromData(resposta_imagem.content)
                        imagem_pixmap = imagem_pixmap.scaled(64, 64, Qt.KeepAspectRatio)
                    except Exception as e:
                        print(f"Erro ao carregar imagem: {str(e)}")

                # Cria um item com título e ícone (imagem)
                item = QListWidgetItem(QIcon(imagem_pixmap), titulo)
                item.setData(Qt.UserRole, link)

                # Adiciona o item à lista
                lista_noticia.addItem(item)



    def abrir_link_noticia(self, item):
        """Abre o link da notícia no navegador."""
        link = item.data(Qt.UserRole)
        if link:
            webbrowser.open(link)


    def atualizar_clima(self):
        """Obtém e exibe o clima atual baseado na localização."""
        try:
            localizacao = requests.get("https://ipapi.co/json/").json()
            cidade = localizacao.get("city", "xai-xai")
            pais = localizacao.get("country", "Moçambique")

            url_clima = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={self.api_key}&units=metric&lang=pt"
            resposta_clima = requests.get(url_clima).json()

            if resposta_clima.get("cod") == 200:
                temperatura = resposta_clima["main"]["temp"]
                descricao = resposta_clima["weather"][0]["description"]
                self.lbl_clima.setText(f"{cidade}, {pais}: {temperatura}°C, {descricao.capitalize()}")
            else:
                self.lbl_clima.setText("Erro: Não foi possível obter o clima.")
        except Exception as e:
            self.lbl_clima.setText(f"Erro de conexão: {str(e)}")
        QTimer.singleShot(600000, self.atualizar_clima)


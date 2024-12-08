from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QSizePolicy,
    QListWidgetItem,  QGridLayout, QTextEdit, QComboBox
)
from PySide6.QtGui import QIcon, QPixmap, QPalette, QBrush, QFont
from PySide6.QtCore import Qt, QTimer

from config.config import BASE_DIR_Config, cidade_atual, BASE_DIR_Log_Main
import requests
import feedparser
import webbrowser
import platform
import platform
from datetime import datetime, timedelta
import os
import platform
import psutil
from datetime import datetime
import json
from weatherapi.rest import ApiException
from datetime import datetime
import traceback
import json
import os

class Home(QWidget):
    def __init__(self, BASE_DIR_Config=BASE_DIR_Config, BASE_DIR_Log_Main=BASE_DIR_Log_Main, cidade_atual= cidade_atual):
        super().__init__()
        self.api_key_clima_OpenWeatherMap = 'S2064f304fa63035d64582f37aa73a65a'   # API Key do OpenWeatherMap
        self.api_key_clima_WeatherAPI     = '82e69e48b8ee4d02b7494024242211'     # API Key do WeatherAPI
        self.api_key_tomorrowio           =  'toJXAolx4UfTrB2ghISxD6r1eQ9gwMO2'
        self.cidade_atual = cidade_atual
        self.cor_fundo_transparente = 'transparent'
        self.cor_azul_escuro = '#1A252F'
        self.lista_clima = QListWidget()
        
        if not os.path.exists(BASE_DIR_Config):
            os.makedirs(BASE_DIR_Config)
        self.caminho_comandos_json = os.path.join(BASE_DIR_Config, "clima.json")
        
        if not os.path.exists(BASE_DIR_Log_Main ):
            os.makedirs(BASE_DIR_Log_Main )
        self.log_file = os.path.join(BASE_DIR_Log_Main, "Logs_Home.log")
       
        # self.timer_tempo = QTimer(self)
        # self.timer_tempo.timeout.connect(self.atualizar_clima)
        # self.timer_tempo.start(36000)
        
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.atualizar_noticias)
        # self.timer.start(36000)  # Atualiza notícias a cada 1 minuto
        
        self.timer_sistema = QTimer(self)
        self.timer_sistema.timeout.connect(self.atualizar_informacoes_sistema)
        self.timer_sistema.start(5000)  # Atualiza a cada 5 segundos
        
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)

        # Navbar - Informações do Sistema
        navbar = QGridLayout()
   
        # navbar.setSpacing(10)  # Espaçamento entre as caixas
        estilo_navbar = """
            background-color: transparent;
            border: 1px solid #2496be;
            border-radius: 8px;
            padding: 2px;
        """
      
        def criar_caixa(titulo):
            caixa = QTextEdit()
            caixa.setReadOnly(True)
            caixa.setFont(QFont("Times New Roman", 12))
            caixa.setStyleSheet(estilo_navbar)
            
            caixa.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            caixa.setHtml(f"<h3 style='color:#2496be;'>{titulo}</h3>")
            return caixa  
         
        # Caixas NavBar
        self.caixa_cpu = criar_caixa("CPU")
        self.caixa_ram = criar_caixa("RAM")
        self.caixa_gpu = criar_caixa("GPU")
        self.caixa_bateria = criar_caixa("Bateria")
        
        self.caixa_disco = criar_caixa("Disco")
        self.caixa_rede = criar_caixa("Internet")
        self.caixa_m_virtual = criar_caixa("M-Virtual")
        self.caixa_processos = criar_caixa("Processos Ativos")

        # Adicionar caixas navbar ao GridLayout
        navbar.addWidget(self.caixa_cpu,      0, 0)
        navbar.addWidget(self.caixa_ram,      0, 1)
        navbar.addWidget(self.caixa_gpu,      0, 2)
        navbar.addWidget(self.caixa_bateria,  0, 3)
        navbar.addWidget(self.caixa_disco,    1, 0)
        navbar.addWidget(self.caixa_rede,      1, 1)
        navbar.addWidget(self.caixa_m_virtual,1, 2)
        navbar.addWidget(self.caixa_processos,1, 3)

        # Área Central - 9 Caixas
        area_central = QGridLayout()

        # Caixas principais
        self.caixa_disco1 = criar_caixa("Saúde do Disco (pySMART)")
        self.caixa_sistema = criar_caixa("Informações do Sistema (pywin32)")
        self.caixa_cpu1 = criar_caixa("Informações do Processador (pycpuinfo)")
        self.caixa_os = criar_caixa("Sistema Operacional (platform)")
        self.caixa_bateria1 = criar_caixa("Bateria e Energia (psutil + win32com.client)")
        self.caixa_wmi1 = criar_caixa("Detalhes do Sistema (WMI)")

        # Adicionar caixas principais ao GridLayout
        area_central.addWidget(self.caixa_disco1, 0, 0)
        area_central.addWidget(self.caixa_sistema, 0, 1)
        area_central.addWidget(self.caixa_cpu1, 0, 2)
        area_central.addWidget(self.caixa_os, 1, 0)
        area_central.addWidget(self.caixa_bateria1, 1, 1)
        area_central.addWidget(self.caixa_wmi1, 1, 2)

        # Rodapé - Notícias e Clima
        rodape = QHBoxLayout()

        # Categorias de Notícias
        categorias = ["Notícias Gerais", "Esportes", "Tecnologia"]
        urls_feeds = [
            "https://g1.globo.com/rss/g1/",
            "https://rss.uol.com.br/feed/esporte.xml",
            "https://rss.tecmundo.com.br/feed"
        ]

        self.lista_feeds = []
        self.urls_feeds = urls_feeds

        # Painel de Notícias
        painel_noticias = QHBoxLayout()
        for i, categoria in enumerate(categorias):
            caixa_noticia = self.criar_caixa_noticia(categoria, i)
            painel_noticias.addWidget(caixa_noticia)

        # Painel de Clima
        caixa_clima = self.criar_caixa_clima()
        painel_noticias.addWidget(caixa_clima)

        # Adicionar os painéis de notícias e clima ao rodapé
        rodape.addLayout(painel_noticias, stretch=1)

        # Adicionar componentes ao layout principal
        layout_principal.addLayout(navbar)  # Adiciona o navbar organizado no GridLayout
        layout_principal.addLayout(area_central)  # Grid com as 9 caixas
        layout_principal.addLayout(rodape)

        self.setLayout(layout_principal)
        self.setStyleSheet("""
            background-color: transparent;
            border: 1px solid #2496be;
            border-radius: 8px;
            padding: 5px;
            color: white;
        """)
   
    def atualizar_informacoes_sistema(self):
        try:
            # Monitoramento de CPU
            uso_cpu = psutil.cpu_percent(interval=1)
            freq_cpu = psutil.cpu_freq()
            nome_cpu = platform.processor() or "Desconhecido"
            self.caixa_cpu.setPlainText(f"CPU: {uso_cpu}% | {freq_cpu.current:.2f} MHz\nNome: {nome_cpu}")

            # Monitoramento de RAM
            memoria = psutil.virtual_memory()
            self.caixa_ram.setPlainText(
                f"RAM: {memoria.percent}%\n"
                f"Livre: {memoria.available // (1024 ** 2)} MB\n"
                f"Usado: {memoria.used // (1024 ** 2)} MB\n"
                f"Capacidade: {memoria.total // (1024 ** 2)} MB"
            )

            # Monitoramento de GPU
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    self.caixa_gpu.setPlainText(
                        f"GPU: {gpu.name}\nUso: {gpu.load * 100:.1f}%\nMemória: {gpu.memoryUsed:.1f} MB"
                    )
                else:
                    self.caixa_gpu.setPlainText("GPU: Não detectada")
            except ImportError:
                self.caixa_gpu.setPlainText("GPU: GPUtil não disponível")

            # Monitoramento de Bateria
            bateria = psutil.sensors_battery()
            if bateria:
                status_bateria = "Carregando" if bateria.power_plugged else "Descarregando"
                tempo_restante = (
                    bateria.secsleft // 60 if bateria.secsleft != psutil.POWER_TIME_UNLIMITED else "Indeterminado"
                )
                self.caixa_bateria.setPlainText(
                    f"Bateria: {bateria.percent}%\nStatus: {status_bateria}\nTempo restante: {tempo_restante} minutos"
                )
            else:
                self.caixa_bateria.setPlainText("Bateria: Não disponível")

            # Monitoramento de Rede
            conexao = "Wi-Fi" if "wlan" in psutil.net_if_addrs() else "Ethernet"
            status_rede = "Conectado" if any(psutil.net_if_stats().values()) else "Desconectado"
            net_io = psutil.net_io_counters()
            download_speed = net_io.bytes_recv / 1024 / 1024  # MB recebidos
            upload_speed = net_io.bytes_sent / 1024 / 1024    # MB enviados
            self.caixa_rede.setPlainText(
                f"Rede: {conexao}\nStatus: {status_rede}\nDownload: {download_speed:.2f} MB\nUpload: {upload_speed:.2f} MB"
            )

            # Monitoramento de Disco
            lista_particoes = []
            for particao in psutil.disk_partitions():
                try:
                    uso_disco = psutil.disk_usage(particao.mountpoint)
                    lista_particoes.append(
                        f"{particao.device}\nLivre: {uso_disco.free // (1024 ** 3)} GB\n"
                        f"Usado: {uso_disco.used // (1024 ** 3)} GB\nTotal: {uso_disco.total // (1024 ** 3)} GB"
                    )
                except PermissionError:
                    lista_particoes.append(f"{particao.device}: Permissão negada")
            self.caixa_disco.setPlainText("\n\n".join(lista_particoes))

            # Monitoramento de Processos Ativos
            processos_ativos = len(psutil.pids())
            self.caixa_processos.setPlainText(f"Processos Ativos: {processos_ativos}")

            # Monitoramento de Swap (Memória Virtual)
            swap = psutil.swap_memory()
            self.caixa_m_virtual.setPlainText(
                
                f"Swap: {swap.percent}%\nUsado: {swap.used // (1024 ** 2)} MB\nTotal: {swap.total // (1024 ** 2)} MB"
                
            ) 
        except Exception as geral:
            self.log_erro(f"Erro geral ao atualizar informações do sistema: {geral}")

    def criar_caixa_noticia(self, categoria, index):
        """Cria uma caixa de notícia com título e lista de itens."""
        caixa = QWidget()
        caixa_layout = QVBoxLayout(caixa)
        lbl_noticia = QLabel(categoria)
        lbl_noticia.setFont(QFont("Times New Roman", 12))
        lbl_noticia.setStyleSheet("""
            color: #2496be;
            font-weight: bold;
            padding: 5px;
            border:none;
        """)

        lista_noticia = QListWidget()
        lista_noticia.setFont(QFont("Times New Roman", 12))
        lista_noticia.setStyleSheet("""
            background-color: transparent;
            color: white;
            border: none;
        """)
        lista_noticia.setMinimumHeight(200)
        lista_noticia.itemDoubleClicked.connect(self.abrir_link_noticia)

        # Adicionando na lista de feeds
        self.lista_feeds.append(lista_noticia)

        # Verificar se o índice está dentro do limite
        if index < len(self.urls_feeds):
            self.atualizar_fundo_caixa(caixa, index)
        else:
            self.log_erro(f"Índice {index} fora do alcance da lista de URLs de feeds.")

        caixa_layout.addWidget(lbl_noticia)
        caixa_layout.addWidget(lista_noticia)
        return caixa
    
    def atualizar_fundo_caixa(self, caixa, index):
        """Define o fundo da caixa de notícias com a imagem da primeira notícia."""
        url_feed = self.urls_feeds[index]
        feed = feedparser.parse(url_feed)
        
        imagem_url = ""
        if feed.entries:
            entrada = feed.entries[0]
            if "media_content" in entrada:
                imagem_url = entrada.media_content[0]['url']
            elif "enclosure" in entrada:
                imagem_url = entrada.enclosure.get('url', '')

        imagem_pixmap = QPixmap()
        if imagem_url:
            try:
                resposta_imagem = requests.get(imagem_url)
                imagem_pixmap.loadFromData(resposta_imagem.content)
                imagem_pixmap = imagem_pixmap.scaled(300, 200, Qt.KeepAspectRatioByExpanding)
                
                # Definir a imagem como fundo da caixa
                paleta = caixa.palette()
                paleta.setBrush(QPalette.Window, QBrush(imagem_pixmap))
                caixa.setAutoFillBackground(True)
                caixa.setPalette(paleta)
                
            except Exception as e:
               self.log_erro(f"Erro ao carregar imagem de fundo: {str(e)}")
    
    def atualizar_noticias(self):
        """Atualiza as listas de notícias usando feeds RSS por categoria."""
        max_noticias = 5

        for i, url_feed in enumerate(self.urls_feeds):
            if i >= len(self.lista_feeds):
                self.log_erro(f"Erro: índice {i} fora do alcance da lista de feeds.")
                continue

            lista_noticia = self.lista_feeds[i]

            # Verifica se a lista ainda é válida antes de limpar
            if lista_noticia is None or lista_noticia.parent() is None:
                self.log_erro(f"Lista de notícias {i} foi deletada ou não é válida.")
                continue

            # Limpa a lista para atualizar
            lista_noticia.clear()

            # Tratamento de erros ao acessar o feed
            try:
                feed = feedparser.parse(url_feed)
                
                # Verifica se o feed foi processado corretamente
                if feed.bozo:
                    self.log_erro(f"Erro ao processar o feed {url_feed}: {feed.bozo_exception}")
                    lista_noticia.addItem(QListWidgetItem(f"Erro ao acessar feed: {url_feed}"))
                    continue

                # Itera pelas entradas e adiciona na lista
                for entrada in feed.entries[:max_noticias]:
                    titulo = entrada.title
                    link = entrada.link

                    # Tenta obter uma imagem associada (se implementado)
                    imagem_pixmap = self.obter_imagem_pixmap(entrada)

                    # Criação do item com título e link
                    item = QListWidgetItem(QIcon(imagem_pixmap), titulo)
                    item.setData(Qt.UserRole, link)
                    lista_noticia.addItem(item)

                # Adiciona mensagem se não houver notícias
                if lista_noticia.count() == 0:
                    lista_noticia.addItem(QListWidgetItem("Nenhuma notícia encontrada"))

            except Exception as e:
                self.log_erro(f"Erro ao atualizar notícias para {url_feed}: {e}")
                lista_noticia.addItem(QListWidgetItem(f"Erro ao acessar feed: {e}"))
       
    def obter_imagem_pixmap(self, entrada):
        """Obtém um QPixmap de uma entrada do feed."""
        imagem_url = ""
        try:
            if "media_content" in entrada and len(entrada.media_content) > 0:
                imagem_url = entrada.media_content[0].get("url", "")
            elif "enclosures" in entrada and len(entrada.enclosures) > 0:
                imagem_url = entrada.enclosures[0].get("url", "")
            elif "image" in entrada:
                imagem_url = entrada.image.get("url", "")
            elif "media_thumbnail" in entrada:
                imagem_url = entrada.media_thumbnail[0].get("url", "")

            if imagem_url:
                resposta_imagem = requests.get(imagem_url, timeout=5)
                if resposta_imagem.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(resposta_imagem.content)
                    return pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        except Exception as e:
            self.log_erro(f"Erro ao carregar imagem: {str(e)}")
        return QPixmap()

    def abrir_link_noticia(self, item):
        """Abre o link da notícia no navegador."""
        link = item.data(Qt.UserRole)
        if link:
            webbrowser.open(link)
 
    # *********************   Clima ************************************  
    def criar_caixa_clima(self):
        """Cria uma caixa de previsão do tempo similar às caixas de notícias."""
        if not hasattr(self, "lista_clima"):
            self.lista_clima = QListWidget()  # Inicializa apenas se não existir
        caixa_clima = QWidget()
        layout_clima = QVBoxLayout(caixa_clima)
        lbl_titulo = QLabel("Previsão do Tempo")
        lbl_titulo.setFont(QFont("Times New Roman", 12))
        lbl_titulo.setStyleSheet("font-weight: bold; color: #2496be; border:none;")

        self.lista_clima.setFont(QFont("Times New Roman", 12))
        self.lista_clima.setStyleSheet("""
            background-color: transparent;
            border-radius: 8px;
            padding: 5px; 
            border:none;                             
        """)
        self.lista_clima.setMinimumHeight(200)

        layout_clima.addWidget(lbl_titulo)
        layout_clima.addWidget(self.lista_clima)
        return caixa_clima

    def atualizar_clima(self):
    
        caminho_clima = self.caminho_comandos_json  # Caminho para o arquivo clima.json
        cidades = ["Maputo", "Beira", "Nampula", "Chimoio", "Quelimane", "Xai-xai"]  # Adicione todas as cidades desejadas
        cidade_atual = self.cidade_atual  # Informe manualmente a cidade atual (ou receba como entrada)
        apis = [
            {"nome": "OpenWeatherMap", "url": "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric", "key": self.api_key_clima_OpenWeatherMap},
            {"nome": "WeatherAPI", "url": "http://api.weatherapi.com/v1/current.json?key={}&q={}", "key": self.api_key_clima_WeatherAPI},
            {"nome": "Tomorrow.io", "func": self.processar_dados_tomorrowio, "key": self.api_key_tomorrowio},
        ]

        if not self.verificar_conexao():
            dados_offline = self.carregar_dados_clima_validos(caminho_clima)
            if dados_offline:
                self.exibir_dados_clima(dados_offline.get(cidade_atual, {}))
            else:
                self.lista_clima.addItem("Sem conexão e nenhum dado de clima válido para hoje.")
            return

        dados_todas_cidades = {}

        for cidade in cidades:
            for api in apis:
                try:
                    if api["nome"] == "Tomorrow.io":
                        clima_atual = api["func"](cidade, api["key"])
                    else:
                        url = api["url"].format(api["key"], cidade)
                        resposta = requests.get(url, timeout=10)
                        resposta.raise_for_status()
                        dados_clima = resposta.json()

                        if api["nome"] == "WeatherAPI":
                            clima_atual = self.processar_dados_weatherapi(dados_clima)
                        elif api["nome"] == "OpenWeatherMap":
                            clima_atual = self.processar_dados_openweathermap(dados_clima)

                    dados_todas_cidades[cidade] = clima_atual
                    break  # Passa para a próxima cidade ao obter sucesso
                except Exception as e:
                    self.log_erro(f"Erro ao acessar API {api['nome']} para a cidade {cidade}: {e}")
                    continue

        # Salva todos os dados coletados no arquivo JSON
        self.salvar_dados_clima(caminho_clima, dados_todas_cidades)

        # Exibe os dados da cidade atual
        self.exibir_dados_clima(dados_todas_cidades.get(cidade_atual, {}))

    def verificar_conexao(self):
        """Verifica se há conexão com a internet."""
        try:
            requests.get("https://www.google.com", timeout=5)
            return True
        except requests.ConnectionError:
            return False
    
    def salvar_dados_clima(self, caminho, dados):
      
        try:
            # Lê os dados existentes no arquivo, se houver
            try:
                with open(caminho, "r", encoding="utf-8") as arquivo:
                    dados_existentes = json.load(arquivo)
            except FileNotFoundError:
                dados_existentes = {}  # Arquivo não existe ainda

            # Atualiza os dados existentes com os novos
            for cidade, clima in dados.items():
                clima["data_gravacao"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                dados_existentes[cidade] = clima

            # Salva os dados atualizados no arquivo
            with open(caminho, "w", encoding="utf-8") as arquivo:
                json.dump(dados_existentes, arquivo, indent=4, ensure_ascii=False)
        except Exception as e:
            self.log_erro(f"Erro ao salvar dados no arquivo clima: {e}")

    def carregar_dados_clima_validos(self, caminho):
        try:
            # Tenta abrir e carregar os dados do arquivo JSON
            with open(caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)

            # Obtém a data de gravação registrada nos dados
            # data_registro = datetime.strptime(dados.get("data_hora", ""), "%Y-%m-%d %H:%M:%S").date()
            # data_atual = datetime.now().date()

            # Verifica se os dados são do dia atual
            if not dados:
                
                return dados  # Retorna os dados válidos
            else:
                return dados  # Dados são de um dia anterior
        except FileNotFoundError:
            self.log_erro(f"Arquivo {caminho} não encontrado.")
            return None
        except Exception as e:
            self.log_erro(f"Erro ao carregar dados de clima: {e}")
            return None

    def exibir_dados_clima(self, dados):
        """Exibe os dados do clima no widget."""
        self.lista_clima.clear()
        try:
            clima_texto = f"{dados['cidade']}: {dados['temperatura']}°C - {dados['descricao'].capitalize()} (via {dados['api']})"
            self.lista_clima.addItem(clima_texto)
        except KeyError:
            self.lista_clima.addItem("Erro ao exibir dados do clima.")

    def processar_dados_weatherapi(self, dados_clima):
        """Processa os dados da WeatherAPI para o formato padrão."""
        return {
            "id": dados_clima.get("location", {}).get("name", "Desconhecido"),
            "cidade": dados_clima.get("location", {}).get("name", "Desconhecido"),
            "temperatura": dados_clima.get("current", {}).get("temp_c", "N/A"),
            "descricao": dados_clima.get("current", {}).get("condition", {}).get("text", "Desconhecido"),
            "data_hora": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "api": "WeatherAPI",
        }
   
    def processar_dados_openweathermap(self, dados_clima):
        """Processa os dados do OpenWeatherMap para o formato padrão."""
        return {
            "id": dados_clima.get("id"),
            "cidade": dados_clima.get("name"),
            "temperatura": dados_clima["main"]["temp"],
            "descricao": dados_clima["weather"][0]["description"],
            "data_hora": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "api": "OpenWeatherMap",
        }

    def processar_dados_tomorrowio(self, cidade, api_key):
        """Processa os dados da API Tomorrow.io para o formato padrão."""
        try:
            url = f"https://api.tomorrow.io/v4/weather/realtime?location={cidade}&apikey={api_key}"
            headers = {"accept": "application/json"}
            resposta = requests.get(url, headers=headers, timeout=10)
            resposta.raise_for_status()
            dados = resposta.json()

            return {
                "id": dados.get("id", "N/A"),
                "cidade": cidade,
                "temperatura": dados["data"]["values"].get("temperature", "N/A"),
                "descricao": dados["data"]["values"].get("weatherCode", "N/A"),
                "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "api": "Tomorrow.io",
            }
        except Exception as e:
            print(f"Erro ao acessar Tomorrow.io: {e}")
            return None

    def criar_menu_selecao_cidade(self):
        """Cria um menu para seleção de cidades."""
        self.combo_cidades = QComboBox()
        self.combo_cidades.addItems(["Maputo", "Beira", "Nampula", "Chimoio", "Quelimane"])  # Adicione mais cidades
        self.combo_cidades.currentTextChanged.connect(self.atualizar_exibicao_cidade)
        return self.combo_cidades

    def atualizar_exibicao_cidade(self, cidade_selecionada):
        """Atualiza a exibição com os dados da cidade selecionada."""
        caminho_clima = self.caminho_comandos_json
        dados = self.carregar_dados_clima_validos(caminho_clima)
        if dados and cidade_selecionada in dados:
            self.exibir_dados_clima(dados[cidade_selecionada])
        else:
            self.lista_clima.clear()
            self.lista_clima.addItem("Dados da cidade selecionada não disponíveis.")

    def clima_hoje(self, cidade=cidade_atual):
        """Obtém e formata a previsão do clima para a cidade especificada."""
        apis = [
            {
                "nome": "Tomorrow.io",
                "url": f"https://api.tomorrow.io/v4/weather/realtime?location={cidade}&apikey={self.api_key_tomorrowio}",
                "processar": self.processar_dados_tomorrowio,
            },
            {
                "nome": "OpenWeatherMap",
                "url": f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={self.api_key_clima_OpenWeatherMap}&units=metric",
                "processar": self.processar_dados_openweathermap,
            },
            {
                "nome": "WeatherAPI",
                "url": f"http://api.weatherapi.com/v1/current.json?key={self.api_key_clima_WeatherAPI}&q={cidade}",
                "processar": self.processar_dados_weatherapi,
            },
        ]

        for api in apis:
            try:
                resposta = requests.get(api["url"], timeout=10)
                resposta.raise_for_status()
                dados = resposta.json()

                # Processa os dados usando a função correspondente
                dados_processados = api["processar"](dados)
                texto_clima = (
                    f"Clima atual em {cidade}:\n"
                    f"Temperatura: {dados_processados['temperatura']}°C\n"
                    f"Descrição: {dados_processados['descricao']}\n"
                    f"API usada: {api['nome']}\n"
                    f"Atualizado em: {dados_processados['data_hora']}"
                )
                return texto_clima
            except Exception as e:
                self.log_erro(f"Erro ao acessar API {api['nome']} para {cidade}: {e}")
       
    def log_erro(self, mensagem):
            """Registra mensagens de erro no arquivo de log com traceback completo."""
            try:
                
                with open(self.log_file, "a", encoding="utf-8") as log_file:
                    log_file.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - ERROR - {mensagem}\n")
                    # Adiciona o traceback completo se houver uma exceção ativa
                    log_file.write(traceback.format_exc() + "\n")
            except Exception as e:
                self.log_erro(f"Erro ao registrar log: {e}")  
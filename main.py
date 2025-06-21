import os
import requests
from twilio.rest import Client

# ---------------------------- CONSTANTES ------------------------------- #
# Chaves de API e tokens (idealmente, seriam carregados de variáveis de ambiente ou um arquivo de configuração seguro)
VIRTUAL_TWILIO_NUMBER = "your virtual twilio number"  # Seu número Twilio virtual
VERIFIED_NUMBER = "your own phone number verified with Twilio"  # Seu número de telefone verificado no Twilio
STOCK_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")  # Chave da API Alpha Vantage
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")  # Chave da API NewsAPI
TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID")  # SID da conta Twilio
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")  # Token de autenticação Twilio

# Informações da empresa e endpoints das APIs
STOCK_NAME = "TSLA"  # Símbolo da ação (ex: TSLA para Tesla)
COMPANY_NAME = "Tesla Inc"  # Nome completo da empresa
STOCK_ENDPOINT = "https://www.alphavantage.co/query"  # Endpoint da API Alpha Vantage
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"  # Endpoint da API NewsAPI

# Limiar de variação percentual para acionar o alerta de notícias
PERCENTAGE_THRESHOLD = 1  # Porcentagem de variação para considerar como significativa

# ---------------------------- FUNÇÕES DE SERVIÇO ------------------------------- #

def get_stock_data(stock_symbol: str, api_key: str) -> dict:
    """Obtém os dados diários de uma ação da API Alpha Vantage.

    Args:
        stock_symbol (str): O símbolo da ação (e.g., "TSLA").
        api_key (str): A chave da API Alpha Vantage.

    Returns:
        dict: Um dicionário contendo os dados diários da ação.

    Raises:
        requests.exceptions.RequestException: Se a requisição à API falhar.
    """
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": stock_symbol,
        "apikey": api_key,
    }
    response = requests.get(STOCK_ENDPOINT, params=params)
    response.raise_for_status()  # Levanta uma exceção para erros de status HTTP
    return response.json()["Time Series (Daily)"]


def calculate_price_difference(data: dict) -> tuple[float, str]:
    """Calcula a diferença percentual de preço entre o fechamento de ontem e anteontem.

    Args:
        data (dict): Dados diários da ação obtidos da API Alpha Vantage.

    Returns:
        tuple[float, str]: Uma tupla contendo a diferença percentual (arredondada)
                           e um emoji indicando se o preço subiu (🔺) ou desceu (🔻).
    """
    data_list = [value for (key, value) in data.items()] # Converte o dicionário em uma lista de valores
    yesterday_closing_price = float(data_list[0]["4. close"]) # Preço de fechamento de ontem
    day_before_yesterday_closing_price = float(data_list[1]["4. close"]) # Preço de fechamento de anteontem

    difference = yesterday_closing_price - day_before_yesterday_closing_price
    up_down = "🔺" if difference > 0 else "🔻" # Define o emoji de acordo com a variação

    # Calcula a diferença percentual e arredonda
    diff_percent = round((difference / yesterday_closing_price) * 100)
    return diff_percent, up_down


def get_news_articles(company_name: str, api_key: str, num_articles: int = 3) -> list[dict]:
    """Obtém artigos de notícias relacionados a uma empresa da NewsAPI.

    Args:
        company_name (str): O nome da empresa para buscar notícias.
        api_key (str): A chave da API NewsAPI.
        num_articles (int): O número máximo de artigos a serem retornados (padrão: 3).

    Returns:
        list[dict]: Uma lista de dicionários, onde cada dicionário representa um artigo de notícia.

    Raises:
        requests.exceptions.RequestException: Se a requisição à API falhar.
    """
    params = {
        "apiKey": api_key,
        "qInTitle": company_name, # Busca notícias onde o título contém o nome da empresa
        "language": "en", # Opcional: define o idioma para inglês
        "sortBy": "relevancy", # Opcional: ordena por relevância
    }
    response = requests.get(NEWS_ENDPOINT, params=params)
    response.raise_for_status()  # Levanta uma exceção para erros de status HTTP
    articles = response.json()["articles"]
    return articles[:num_articles] # Retorna apenas o número especificado de artigos


def format_news_articles(articles: list[dict], stock_symbol: str, diff_percent: float, up_down_emoji: str) -> list[str]:
    """Formata uma lista de artigos de notícias para envio por SMS.

    Args:
        articles (list[dict]): Uma lista de dicionários de artigos de notícias.
        stock_symbol (str): O símbolo da ação.
        diff_percent (float): A diferença percentual do preço da ação.
        up_down_emoji (str): O emoji indicando a direção da mudança de preço.

    Returns:
        list[str]: Uma lista de strings formatadas, prontas para serem enviadas como mensagens SMS.
    """
    formatted_messages = []
    for article in articles:
        headline = article.get("title", "Título não disponível")
        brief = article.get("description", "Descrição não disponível")
        message = f"{stock_symbol}: {up_down_emoji}{diff_percent}%\nManchete: {headline}. \nResumo: {brief}"
        formatted_messages.append(message)
    return formatted_messages


def send_sms_messages(messages: list[str], account_sid: str, auth_token: str, from_number: str, to_number: str) -> None:
    """Envia múltiplas mensagens SMS usando o serviço Twilio.

    Args:
        messages (list[str]): Uma lista de strings, onde cada string é uma mensagem a ser enviada.
        account_sid (str): SID da conta Twilio.
        auth_token (str): Token de autenticação Twilio.
        from_number (str): Número de telefone Twilio remetente.
        to_number (str): Número de telefone do destinatário.
    """
    client = Client(account_sid, auth_token)
    for message_body in messages:
        try:
            message = client.messages.create(
                body=message_body,
                from_=from_number,
                to=to_number
            )
            print(f"Mensagem SMS enviada com status: {message.status}")
        except Exception as e:
            print(f"Erro ao enviar SMS: {e}")

# ---------------------------- LÓGICA PRINCIPAL ------------------------------- #

if __name__ == "__main__":
    # 1. Obter dados da ação
    try:
        stock_data = get_stock_data(STOCK_NAME, STOCK_API_KEY)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter dados da ação: {e}")
        exit() # Sai do programa se não conseguir obter os dados da ação

    # 2. Calcular a diferença de preço
    diff_percent, up_down = calculate_price_difference(stock_data)

    # 3. Verificar se a variação é significativa e obter notícias
    if abs(diff_percent) > PERCENTAGE_THRESHOLD:
        try:
            articles = get_news_articles(COMPANY_NAME, NEWS_API_KEY)
        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter notícias: {e}")
            articles = [] # Continua mesmo sem notícias, mas com uma lista vazia

        if articles:
            # 4. Formatar artigos para SMS
            formatted_messages = format_news_articles(articles, STOCK_NAME, diff_percent, up_down)

            # 5. Enviar mensagens SMS
            send_sms_messages(formatted_messages, TWILIO_SID, TWILIO_AUTH_TOKEN, VIRTUAL_TWILIO_NUMBER, VERIFIED_NUMBER)
        else:
            print("Nenhum artigo de notícia relevante encontrado.")
    else:
        print(f"Variação de preço de {diff_percent}% não atingiu o limiar de {PERCENTAGE_THRESHOLD}%. Nenhuma notícia será enviada.")



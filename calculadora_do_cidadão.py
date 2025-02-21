from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import pyodbc


def obter_data_inicial():
    hoje = datetime.today()
    if hoje.month == 1:
        mes = 12
        ano = hoje.year - 2
    else:
        mes = hoje.month - 1
        ano = hoje.year - 1
    return f"{mes:02d}{ano}"

def obter_data_final():
    hoje = datetime.today()
    if hoje.month == 1:
        mes = 11
        ano = hoje.year - 1
    elif hoje.month == 2:
        mes = 12
        ano = hoje.year - 1
    else:
        mes = hoje.month - 2
        ano = hoje.year
    return f"{mes:02d}{ano}"
    
def capturar_indice_geral(driver):
    try:
        wait = WebDriverWait(driver, 20)
        ValorIndice = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr:nth-child(6) > .fundoPadraoAClaro3:nth-child(2)"))).text.replace(',', '.')
        ValorPercentual = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr:nth-child(7) > .fundoPadraoAClaro3:nth-child(2)"))).text.replace(',', '.').replace('%', '')
        print("-----------------------------------------------")
        print(f"Valor Indice do IGP-M (FGV): {ValorIndice}")
        print(f"Valor Porcentagem do IGP-M (FGV): {ValorPercentual}")
        return float(ValorIndice), float(ValorPercentual)
    except Exception as e:
        print(f"Erro ao capturar o valor do IGP-M (FGV): {e}")
        return None, None

def capturar_ipca(driver):
    try:
        wait = WebDriverWait(driver, 20)
        ipca_value = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr:nth-child(6) > .fundoPadraoAClaro3:nth-child(2)"))).text.replace(',', '.')
        ipca_porcent = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr:nth-child(7) > .fundoPadraoAClaro3:nth-child(2)"))).text.replace(',', '.').replace('%', '')
        print("-----------------------------------------------")
        print(f"Valor Indice do IPCA (IBGE): {ipca_value}")
        print(f"Valor Porcentagem do IPCA (IBGE): {ipca_porcent}")
        print("-----------------------------------------------")
        return float(ipca_value), float(ipca_porcent)
    except Exception as e:
        print(f"Erro ao capturar o valor do IPCA (IBGE): {e}")
        return None, None

data_inicial_str = obter_data_inicial()
data_final_str = obter_data_final()
# Converter strings para objetos de data
data_inicial_formatada = datetime.strptime(data_inicial_str, "%m%Y")
data_final_formatada = datetime.strptime(data_final_str, "%m%Y")

# Converter objetos de data para o formato YYYY-MM-DD
data_inicial_sql = data_inicial_formatada.strftime("%Y-%m-%d")
data_final_sql = data_final_formatada.strftime("%Y-%m-%d")


# Configurações para rodar o Chrome em modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--disable-gpu") 
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920x1080")  # Simular uma tela completa
chrome_options.add_argument("--disable-dev-shm-usage")  # Para evitar problemas em ambientes com pouca memória
chrome_options.add_argument("--remote-debugging-port=9222")  # Desativar depuração remota

chrome_service = Service(executable_path='C:\\Python312\\chromedriver-win64\\chromedriver.exe')
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

url = "https://www3.bcb.gov.br/CALCIDADAO/publico/corrigirPorIndice.do?method=corrigirPorIndice"

driver.get(url)

data_inicial = driver.find_element(By.NAME, "dataInicial")
data_final = driver.find_element(By.NAME, "dataFinal")

data_inicial.send_keys(data_inicial_str)
data_final.send_keys(data_final_str)

botao_corrigir = driver.find_element(By.CSS_SELECTOR, ".botao:nth-child(2)")
botao_corrigir.click()

indice_geral, percentual_geral = capturar_indice_geral(driver)

driver.get(url)

ipca_option = driver.find_element(By.XPATH, "//select[@id='selIndice']/option[text()='IPCA (IBGE) - a partir de 01/1980']")
ipca_option.click()

data_inicial = driver.find_element(By.NAME, "dataInicial")
data_final = driver.find_element(By.NAME, "dataFinal")

data_inicial.send_keys(data_inicial_str)
data_final.send_keys(data_final_str)

botao_corrigir = driver.find_element(By.CSS_SELECTOR, ".botao:nth-child(2)")
botao_corrigir.click()

ipca_value, ipca_porcent = capturar_ipca(driver)

driver.quit()

try:
    #Desenvolvimento
    conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=SEU_SERVER_AQUI;"
        "Database=SEU_DATA_BASE_AQUI;"
        "UID=SUA_UID_AQUI;"
        "PWD=SUA_SENHA_AQUI;"
    )

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    insert_query = """
    CASO_QUEIRA_FAZER_UM_INSERT_AQUI;
    """
    
    # Inserção para IGP-M (id_tipo = 1)
    cursor.execute(insert_query, (1, indice_geral, percentual_geral, data_inicial_sql, data_final_sql))
    
    # Inserção para IPCA (id_tipo = 2)
    cursor.execute(insert_query, (2, ipca_value, ipca_porcent, data_inicial_sql, data_final_sql))
    
    conn.commit()

    print("Dados inseridos com sucesso!")
except pyodbc.Error as e:
    print(f"Erro na conexão ou inserção no banco de dados: {e}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()

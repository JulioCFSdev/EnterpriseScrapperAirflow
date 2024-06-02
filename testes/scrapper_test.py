from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import threading
import time
import json

class Scrapper():
    def __init__(self):
        self.driver_path = 'C:/Users/Arkade/Desktop/airflow-docker/testes/chromedriver-win64/chromedriver-win64/chromedriver.exe'
        self.driver = self.__init_driver()
        self.screen_wait_time = 2
        self.search_pag_url = "https://br.investing.com/search/?q="
        self.enterprise_news_pag_url = ""
        self.base_enterprise_news_pag_url = ""
        self.news_url_sufix = "-news"
        self.number_pags_news_scrapped = 10
        self.enterprise_news_date = {}
        self.enterprise_name = ""
    
    def __init_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-application-cache')
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--ignore-certificate-error")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("log-level=3")
        caps = webdriver.DesiredCapabilities.CHROME.copy()
        caps['acceptInsecureCerts'] = True
        caps['acceptSslCerts'] = True
        service = Service(executable_path=self.driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    
    def search_url_for_enterprise(self, enterprise_name):
        try:
            self.enterprise_name = enterprise_name
            self.driver.get(self.search_pag_url + enterprise_name)
            search = self.driver.find_elements(By.CSS_SELECTOR, 'div.js-inner-all-results-quotes-wrapper.newResultsContainer.quatesTable a.js-inner-all-results-quote-item')
            if search != []:
                search[0].click()
        except WebDriverException as e:
            print("Ocorreu um erro no WebDriver:", e)
            print("Search company page error from {} param".format(enterprise_name))
            self.close_driver()

    def go_to_entreprise_news(self):
        try:
            news_enterprise_url = self.driver.current_url + self.news_url_sufix
            self.driver.get(news_enterprise_url)
            time.sleep(1)
            self.enterprise_news_pag_url = self.driver.current_url
        except WebDriverException as e:
            print("Ocorreu um erro no WebDriver:", e)
            self.close_driver()

    def go_select_news(self):
        try:
            self.base_enterprise_news_pag_url = self.driver.current_url
            for index_pag in range(1, self.number_pags_news_scrapped + 1):
                self.driver.get(self.base_enterprise_news_pag_url + "/" + str(index_pag))
                self.enterprise_news_pag_url = self.driver.current_url
                news_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-test="article-title-link"]'))
                )
                for index_news in range(len(news_elements)):
                    news_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-test="article-title-link"]'))
                )
                    news_elements[index_news].click()
                    dict_news_text = self.go_scrapp_enterprise_news_info()
                    index_news_in_news_data = ((index_pag - 1)*10) + (index_news + 1)
                    self.enterprise_news_date[f"news_{index_news_in_news_data}"] = dict_news_text
                    self.driver.get(self.enterprise_news_pag_url)
                    time.sleep(1)
                self.save_news_info_in_json()
            self.close_driver()
        except WebDriverException as e:
            print("Ocorreu um erro no WebDriver:", e)
            self.close_driver()

    def go_scrapp_enterprise_news_info(self) -> dict:
        try:
            news_info = {}
            title_element = self.driver.find_element(By.CSS_SELECTOR, "div.mx-0.mt-1 h1")
            news_info["news_title"] = title_element.text
            print(news_info["news_title"])
            
            paragraphs = self.driver.find_elements(By.CSS_SELECTOR, '.article_WYSIWYG__O0uhw p')
            news_info["text"] = [p.text for p in paragraphs if p.text.strip() != '']
            print(news_info["text"])
            return news_info
        except:
            return {}
        
    def save_news_info_in_json(self):
        try:
            json_file_path = f'noticias{self.enterprise_name}.json'
            with open(json_file_path, 'w', encoding='utf-8') as jsonf:
                json.dump(self.enterprise_news_date, jsonf, ensure_ascii=False, indent=4)

        except:
            print("Save failed")
            self.close_driver()

    def close_driver(self):
        self.driver.quit()


json_file_path = 'companies.json'
with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
companies = data["Trending_Tickers"]

# Índice global para controlar qual elemento será impresso
index = 0
index_lock = threading.Lock()

def scrapper_company():
    global index
    while True:
        with index_lock:
            if index >= len(companies):
                break
            company = companies[index]
            index += 1
        scrapper = Scrapper()
        scrapper.search_url_for_enterprise(company)
        scrapper.go_to_entreprise_news()
        scrapper.go_select_news()

# Número de threads que serão criadas
num_threads = 2
threads = []

# Criar e iniciar as threads
for _ in range(num_threads):
    thread = threading.Thread(target=scrapper_company)
    threads.append(thread)
    thread.start()

# Aguardar todas as threads terminarem
for thread in threads:
    thread.join()

print("Todas as empresas foram scrappadas.")

import logging
import sys
import time
from datetime import date, datetime

import yaml
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

jours = ['LUNDI','MARDI','MERCREDI','JEUDI','VENDREDI','SAMEDI','DIMANCHE']

days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

date_today = date.today().strftime("%A")

if days.index(date_today.upper())==0:
    day='DIMANCHE'
else:
    day=jours[days.index(date_today.upper())-1]
    
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try multiple config locations
config_paths = [
    'config.yaml',
    os.path.join(os.path.dirname(__file__), 'config.yaml'),
    os.path.expanduser('~/paristennis/config.yaml')
]

data = {}
for config_path in config_paths:
    if os.path.exists(config_path):
        with open(config_path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            break

if not data:
    logger.warning("No config file found, using defaults")

def paris_tennis(couvert=True, hours=['21h','19h'], numero_court = None,name = "Elisabeth", day=day, profil='1', time_waiting = 8, training=False):
    """Réservation terrain de tennis
    *****************************************************************
    couvert = False : Si le terrain doit être couvert ou non
    hour = '19h' : Liste des heures dans l'ordre de priorité sur lesquelles vous souhaitez jouer
    numero_court = 'N°3' : Le numéro du court que vous souhaitez
    name = 'Atlantique' : Le nom terrain sur lequel vous voulez jouer
    """

    resa_prise = False
    count = 0
    tarif = "COUVERT"

    while resa_prise==False and count<2:
        count+=1
        options = Options()
        options.add_argument("--window-size=1920,1080")
        if not training:
            options.add_argument("--headless")
        options.add_argument("--lang=fr")
        try:
            # Use the correct chromedriver path
            chromedriver_path = os.path.expanduser('~/.wdm/drivers/chromedriver/mac64/140.0.7339.82/chromedriver-mac-x64/chromedriver')
            if os.path.exists(chromedriver_path):
                service = ChromeService(chromedriver_path)
            else:
                service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du driver Chrome: {e}")
            raise
        driver.get("https://tennis.paris.fr")
        wait = WebDriverWait(driver, timeout=15)

        # Handle authentication flow - check if login button opens new window or redirects
        try:
            window_before = driver.window_handles[0]
            driver.find_element(By.ID, 'button_suivi_inscription').click()

            # Wait for either new window or redirect
            time.sleep(2)

            if len(driver.window_handles) > 1:
                # New window opened (old behavior)
                window_after = driver.window_handles[1]
                driver.switch_to.window(window_after)

                sbox = driver.find_element(By.ID, "username-login")
                sbox.send_keys(data[f"email{profil}"])

                sbox = driver.find_element(By.ID, "password-login")
                sbox.send_keys(data[f"password{profil}"])

                sbox.submit()

                driver.switch_to.window(window_before)
            else:
                # Redirected to auth page (new behavior)
                wait.until(ec.presence_of_element_located((By.ID, "username")))

                # Fill login form on auth page
                sbox = driver.find_element(By.ID, "username")
                sbox.send_keys(data[f"email{profil}"])

                sbox = driver.find_element(By.ID, "password")
                sbox.send_keys(data[f"password{profil}"])

                driver.find_element(By.XPATH, "//button[contains(@class, 'btn') or contains(text(), 'Continuer')]").click()

                # Wait for redirect back to tennis site
                wait.until(lambda driver: "tennis.paris.fr" in driver.current_url)

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            # Try to continue anyway - user might already be logged in
            pass

        driver.get("https://tennis.paris.fr/tennis/jsp/site/Portal.jsp?page=recherche&view=recherche_creneau#!")
        wait = WebDriverWait(driver, timeout=15)
        
        if couvert==True:
            driver.find_element(By.ID, "dropdownTerrain").click()
            driver.find_element(By.XPATH, "//label[@for='chckDécouvert']").click()

        try : 
            sbox = driver.find_element(By.CLASS_NAME, "tokens-input-text")
            sbox.send_keys(name)
            time.sleep(1) 
            suggestions = driver.find_elements(By.CLASS_NAME, 'tokens-suggestions-list-element')
            for suggestion in suggestions:
                if name.upper() in suggestion.text.upper():
                    
                    suggestion.click()
                    break
        except StaleElementReferenceException :
            logger.debug('Retry after StaleElementReferenceException')
            sbox = driver.find_element(By.CLASS_NAME, "tokens-input-text")
            sbox.send_keys(name)
            time.sleep(1) 
            suggestions = driver.find_elements(By.CLASS_NAME, 'tokens-suggestions-list-element')
            for suggestion in suggestions:
                if name.upper() in suggestion.text.upper():
                    suggestion.click()
                    break

        driver.find_element(By.ID, "rechercher").click()
        
        try:
            disponibilites = driver.find_elements(By.CLASS_NAME, 'date-item')
            logger.debug(f'disponibilities before : {len(disponibilites)}')
            if disponibilites:
                logger.debug(f"text dispo before : {disponibilites[-1].text}")
        except StaleElementReferenceException as e:
            logger.debug(f'StaleElementReferenceException in initial availability check: {e}')
            disponibilites = driver.find_elements(By.CLASS_NAME, 'date-item')
        if not training:
            while datetime.now().hour != time_waiting:
                logger.info('Waiting for scheduled time...')
                while datetime.now().hour != time_waiting:
                    time.sleep(1)
        # Wait for availability to show up for the target day
        max_attempts = 15
        for attempt in range(max_attempts):
            try:
                date_items = driver.find_elements(By.CLASS_NAME, 'date-item')
                if date_items and day in date_items[-1].text and 'disponibilités' in date_items[-1].text:
                    logger.info('Disponibilité trouvée')
                    break

                logger.debug(f'Tentative {attempt + 1}/{max_attempts} - Rafraîchissement...')
                driver.find_element(By.CLASS_NAME, 'btnRefreshResearch').click()
                wait.until(ec.visibility_of_all_elements_located((By.XPATH, "//div[@class='dispo']")))

            except StaleElementReferenceException as e:
                logger.debug(f'StaleElementReferenceException lors de la tentative {attempt + 1}: {e}')
                time.sleep(1)
                continue

        else:
            logger.warning(f'Aucune disponibilité trouvée après {max_attempts} tentatives')
        start_hour = time.time()
        disponibilites = driver.find_elements(By.CLASS_NAME, 'date-item')

        disponibilites[-1].find_element(By.CLASS_NAME, 'date').click()
        wait.until(ec.visibility_of_all_elements_located((By.XPATH, "//div[@class='panel panel-default']")))

        horaires = driver.find_elements(By.XPATH, "//div[@class='panel panel-default']")
        
        for hour in hours:
            for horaire in reversed(horaires):
                tarif_trouve = False
                if hour in horaire.find_element(By.CLASS_NAME, 'panel-title').text:
                    horaire.find_element(By.CLASS_NAME, 'panel-title').click()
                    wait.until(ec.visibility_of_all_elements_located((By.XPATH, "//div[@class='panel-collapse collapse in']")))
                    courts = horaire.find_elements(By.CLASS_NAME, 'tennis-court')
                    if tarif in courts[0].find_element(By.CLASS_NAME, 'price-description').text:
                            tarif_trouve = True
                    if numero_court!=None and numero_court in horaire.text:
                        courts = horaire.find_elements(By.CLASS_NAME, 'tennis-court')
                        court_trouve = False
                        for court in courts:
                            if numero_court in court.text:
                                logger.debug(f"Court sélectionné: {court.text}")
                                numero_court = court.text[6:9]
                                court.find_element(By.CLASS_NAME, 'btn').click()
                                court_trouve = True
                                break
                        if court_trouve==False:
                            numero_court = courts[0].text[6:9]
                            courts[0].find_element(By.CLASS_NAME, 'btn').click()
                    else:
                        numero_court = courts[0].text[6:9]
                        courts[0].find_element(By.CLASS_NAME, 'btn').click()
                if tarif_trouve:
                    break
            if tarif_trouve:
                break
        
        last_scrap = time.time() - start_hour
        
        logger.info(f"Temps de recherche: {last_scrap:.2f}s")
        logger.info(f"Tarif trouvé: {tarif_trouve}")
        

        if not tarif_trouve:
            logger.warning("Aucun court disponible sur le tarif ou l'horaire demandé")
            driver.quit()
            continue
                    
        logger.info(f"Réservation - Court: {numero_court}, Heure: {hour}")
        
        wait.until(ec.visibility_of_all_elements_located((By.XPATH, "//input[@name='player1']")))
        infos_player1 = driver.find_elements(By.NAME, 'player1')

        infos_player1[0].send_keys(data.get(f'player{profil}_lastname', 'JAUFFRET'))
        infos_player1[1].send_keys(data.get(f'player{profil}_firstname', 'MARTIN'))
        infos_player1[2].send_keys(data.get(f'player{profil}_email', data[f'email{profil}']))


        driver.find_element(By.CLASS_NAME, 'addPlayer').click()
        
        wait.until(ec.visibility_of_all_elements_located((By.XPATH, "//input[@name='player2']")))
        infos_player2 = driver.find_elements(By.NAME, 'player2')

        if training:
            logger.info('Mode training - Test réussi')
            driver.find_element(By.ID, 'precedent').click()
            wait.until(ec.visibility_of_all_elements_located((By.XPATH, "//div[@class='modal-footer']")))
            driver.find_element(By.ID, 'btnCancelBooking').click()
            resa_prise=True
            return "test OK"

        infos_player2[0].send_keys(data.get('player2_lastname', 'DE CHAMBURE'))
        infos_player2[1].send_keys(data.get('player2_firstname', 'CYPRIEN'))
        
        driver.find_element(By.CLASS_NAME, 'addPlayer').submit()
        
        wait.until(ec.visibility_of_all_elements_located((By.XPATH, "//div[@class='price']")))
        driver.find_element(By.CLASS_NAME, "price").click()

        driver.find_element(By.ID, 'submit').click()
        
        resa_prise = True
        
        logger.info("Réservation effectuée avec succès")
            
if __name__=='__main__':
    args = sys.argv
    if len(args)>1:
        if args[1]=='training':
            training=True
    else:
        training=False
    paris_tennis(profil="1",time_waiting=8, training=training)

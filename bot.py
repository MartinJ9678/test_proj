import sys

from datetime import datetime
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

import time
from datetime import date

from selenium.common.exceptions import StaleElementReferenceException

jours = ['LUNDI','MARDI','MERCREDI','JEUDI','VENDREDI','SAMEDI','DIMANCHE']

days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

date_today = date.today().strftime("%A")

if days.index(date_today.upper())==0:
    day='DIMANCHE'
else:
    day=jours[days.index(date_today.upper())-1]
    
with open('/Users/jauffret/code/MartinJ9678/paristennis/config.yaml') as f:
   data = yaml.load(f, Loader=yaml.FullLoader)

def paris_tennis(couvert=True, hours=['20h'], numero_court = None,name = "Elisabeth", day=day, profil='1', time_waiting = 8):
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
        #options.add_argument("--headless")
        options.add_argument("--lang=fr")
        driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
        driver.get("https://tennis.paris.fr")
        wait = WebDriverWait(driver, timeout=15)

        window_before = driver.window_handles[0]
        driver.find_element_by_id('button_suivi_inscription').click()
        window_after = driver.window_handles[1]

        driver.switch_to.window(window_after)

        sbox = driver.find_element_by_id("username-login")
        sbox.send_keys(data[f"email{profil}"])

        sbox = driver.find_element_by_id("password-login")
        sbox.send_keys(data[f"password{profil}"])

        sbox.submit()

        driver.switch_to.window(window_before)

        driver.get("https://tennis.paris.fr/tennis/jsp/site/Portal.jsp?page=recherche&view=recherche_creneau#!")
        wait = WebDriverWait(driver, timeout=15)
        
        if couvert==True:
            driver.find_element_by_id("dropdownTerrain").click()
            driver.find_element_by_xpath("//label[@for='chckDécouvert']").click()

        try : 
            sbox = driver.find_element_by_class_name("tokens-input-text")
            sbox.send_keys(name)
            time.sleep(1) 
            suggestions = driver.find_elements_by_class_name('tokens-suggestions-list-element')
            for suggestion in suggestions:
                if name.upper() in suggestion.text.upper():
                    
                    suggestion.click()
                    break
        except StaleElementReferenceException :
            print('retry')
            sbox = driver.find_element_by_class_name("tokens-input-text")
            sbox.send_keys(name)
            time.sleep(1) 
            suggestions = driver.find_elements_by_class_name('tokens-suggestions-list-element')
            for suggestion in suggestions:
                if name.upper() in suggestion.text.upper():
                    suggestion.click()
                    break

        driver.find_element_by_id("rechercher").click()
        
        disponibilites = driver.find_elements_by_class_name('date-item')
        print(f'disponibilities before : {disponibilites}')
        print(f"text dispo before : {driver.find_elements_by_class_name('date-item')[-1].text}")
        while datetime.now().hour != time_waiting:
            print('I am waiting ...')
            while datetime.now().hour != time_waiting:
                time.sleep(1)
        #import ipdb; ipdb.set_trace()
        system_ok = False
        count_raf = 0
        stopper = 0
        while not system_ok and stopper<15: 
            print(f'{count_raf} try')
            print(f'stopper : {stopper}')
            stopper+=1
            if day in driver.find_elements_by_class_name('date-item')[-1].text and 'disponibilités' in driver.find_elements_by_class_name('date-item')[-1].text:
                system_ok=True
                print('deja ok')
                break
            try :
                stopper2 = 0
                while day not in driver.find_elements_by_class_name('date-item')[-1].text or 'disponibilités' not in driver.find_elements_by_class_name('date-item')[-1].text:
                    stopper2+=1
                    if stopper2>15:
                        break
                    print(f'stopper2 : {stopper2}')
                    print(f'rafraichissement {count_raf+1}')
                    count_raf+=1
                    driver.find_element_by_class_name('btnRefreshResearch').click()
                    wait.until(ec.visibility_of_all_elements_located((By.XPATH, "//div[@class='dispo']")))
                    system_ok = True
            except StaleElementReferenceException: 
                print('first except')
                try :
                    print('second try possible')
                    driver.find_element_by_class_name('btnRefreshResearch').click()
                    wait.until(ec.visibility_of_all_elements_located((By.XPATH, "//div[@class='dispo']")))
                except StaleElementReferenceException :
                    print('second except')
                    time.sleep(1)
        start_hour = time.time()
        # while day not in driver.find_elements_by_class_name('date-item')[-1].text or 'disponibilités' not in driver.find_elements_by_class_name('date-item')[-1].text:
        #     driver.find_element_by_class_name('btnRefreshResearch').click()
        #     wait.until(ec.visibility_of_all_elements_located((By.XPATH, "//div[@class='dispo']")))
            
        disponibilites = driver.find_elements_by_class_name('date-item')
        print(f"disponibilities after : {disponibilites}")
        print(f"text dispo after : {driver.find_elements_by_class_name('date-item')[-1].text}")
        dispo_day = False
        
        #import ipdb; ipdb.set_trace()
        
        for dispo in reversed(disponibilites) : 
            print(dispo.find_element_by_class_name('date').text)
            if dispo.find_elements_by_class_name('dispo')!=[] and day in dispo.find_element_by_class_name('date').text:
                dispo_day = True
                date = dispo.find_element_by_class_name('date').text
                meteo = dispo.find_element_by_tag_name('title').text
                dispo.find_element_by_class_name('date').click()
                wait.until(ec.visibility_of_all_elements_located((By.XPATH, "//div[@class='panel panel-default']")))
                print("date: " + date + "\nmeteo: " + meteo)
                break

        if dispo_day == False:
            for dispo in reversed(disponibilites) :
                if dispo.find_elements_by_class_name('dispo')!=[]:
                    date = dispo.find_element_by_class_name('date').text
                    meteo = dispo.find_element_by_tag_name('title').text
                    dispo.find_element_by_class_name('date').click()
                    wait.until(ec.visibility_of_all_elements_located((By.XPATH, "//div[@class='panel panel-default']")))
                    dispo_day = True
                    print(date, meteo)
                    break
        
        if dispo_day == False:
            driver.quit()
            break

        if dispo_day:

            horaires = driver.find_elements_by_xpath("//div[@class='panel panel-default']")
            
            for hour in hours:
                print(hour)
                for horaire in reversed(horaires):
                    tarif_trouve = False
                    if hour in horaire.find_element_by_class_name('panel-title').text:
                        print('hour trouve')
                        horaire.find_element_by_class_name('panel-title').click()
                        time.sleep(1)
                        courts = horaire.find_elements_by_class_name('tennis-court')
                        print(f'courts selenium : {courts}')
                        for court in courts:
                            court_trouve = False
                            tarif_trouve = False
                            print(f"court infos : {court.find_element_by_class_name('price-description').text}")
                            if tarif in court.find_element_by_class_name('price-description').text:
                                tarif_trouve = True
                                print('tarif trouve')
                                if numero_court!=None:
                                    if numero_court in court.text:
                                        court.find_element_by_class_name('btn').click()
                                        court_trouve = True
                                    if not court_trouve:
                                        numero_court = courts[0].text[6:9]
                                        courts[0].find_element_by_class_name('btn').click()
                                else:
                                    numero_court = courts[0].text[6:9]
                                    courts[0].find_element_by_class_name('btn').click()
                                break
                    if tarif_trouve:
                        break
                if tarif_trouve:
                    break
            
            last_scrap = time.time() - start_hour
            
            print(f"last scrap : {last_scrap}")
            
            print(f"tarif : {tarif_trouve}")
            
            if not tarif_trouve:
                horaires[0].find_element_by_class_name('panel-title').click()
                courts = horaires[0].find_elements_by_class_name('tennis-court')
                if courts==[]:
                    horaires[0].find_element_by_class_name('panel-title').click()
                    courts = horaires[0].find_elements_by_class_name('tennis-court')
                hour = horaires[0].find_element_by_class_name('panel-title').text
                for court in courts:
                    court_trouve = False
                    if tarif in court.find_element_by_class_name('price-description').text:
                        tarif_trouve=True
                        if numero_court!=None:
                            if numero_court in court.text:
                                court.find_element_by_class_name('btn').click()
                                court_trouve = True
                            if not court_trouve:
                                numero_court = courts[0].text[6:9]
                                courts[0].find_element_by_class_name('btn').click()
                        else:
                            numero_court = courts[0].text[6:9]
                            courts[0].find_element_by_class_name('btn').click()
                        break

            if not tarif_trouve:
                print("aucun court dispo sur le tarif ou l'horaire demandé")
                #import ipdb; ipdb.set_trace()
                driver.quit()
                continue
            
                     
            print(f"numero_court: {numero_court}/nhour: {hour}")
                            

            NAME1 = 'JAUFFRET'
            PRENOM1 = 'MARTIN'
            EMAIL1 = 'martinjfrt@hotmail.fr'

            wait.until(ec.visibility_of_all_elements_located((By.XPATH, "//input[@name='player1']")))
            infos_player1 = driver.find_elements_by_name('player1')
            print(infos_player1)

            infos_player1[0].send_keys(NAME1)
            infos_player1[1].send_keys(PRENOM1)
            infos_player1[2].send_keys(EMAIL1)


            driver.find_element_by_class_name('addPlayer').click()
            
            wait.until(ec.visibility_of_all_elements_located((By.XPATH, "//input[@name='player2']")))
            infos_player2 = driver.find_elements_by_name('player2')


            NAME2 = 'DE CHAMBURE'

            PRENOM2 = 'CYPRIEN'

            infos_player2[0].send_keys(NAME2)
            infos_player2[1].send_keys(PRENOM2)
            
            driver.find_element_by_class_name('addPlayer').submit()
            
            wait.until(ec.visibility_of_all_elements_located((By.XPATH, "//div[@class='price']")))
            driver.find_element_by_class_name("price").click()

            driver.find_element_by_id('submit').click()
            
            resa_prise = True
            
if __name__=='__main__':
    paris_tennis(profil="1",time_waiting=8)
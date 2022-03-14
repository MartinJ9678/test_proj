import sys
from bot import paris_tennis

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
            
if __name__=='__main__':
    paris_tennis(hours=['21h','18h'],profil="2",time_waiting=8)
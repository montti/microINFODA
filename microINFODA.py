from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import sys
import os
import requests
import time
import json

AUTHFILE = "auth-infoda.conf"


def getJSESSIONID(sso_link):
	driver = webdriver.Firefox()
	driver.get(sso_link)

	wait = WebDriverWait(driver, 10)
	wait.until(lambda driver: driver.current_url != sso_link)

	cookies = driver.get_cookies()

	JSESSIONID = ""

	for i in cookies:
		if i.get("name") == "JSESSIONID":
			JSESSIONID = i.get("value")
			break

	driver.quit()

	if JSESSIONID == "":
		sys.exit("Lamentable no se pudo extraer la cookie correctamente. ¿Usaste el link correcto?")

	return JSESSIONID

def main():

	if ((not (os.path.exists(AUTHFILE))) or os.stat(AUTHFILE).st_size == 0):
		file = open(AUTHFILE, 'w')
		print("Inserte su link de INFODA. El que se encuentra en alumnos.udec.cl, con el formato http://app4.udec.cl/infoda2/index_sso/?pkudec=[UN MONTON DE CARACTERES]")
		file.write(getJSESSIONID(input()))
		file.close()

	file = open(AUTHFILE, 'r')
	
	JSESSIONID = file.readline()


	cookies = {
		'JSESSIONID': JSESSIONID,
	}

	response = requests.get('http://app4.udec.cl/infoda2/calificaciones', cookies=cookies).json()


	print(json.dumps(response, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()




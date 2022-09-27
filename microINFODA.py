from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import sys
import os
import requests
import time
import json

AUTHFILE = "auth-infoda.conf"

"""
Utilizamos Selenium para extraer la cookie que permite acceder a INFODA. Lo optimo sera utilizar requests, 
evitando los problemas de instalar Selenium con pip y geckodriver manualmente. Lamentablemente no lo he logrado
que funcione. (Hay algún tipo de verificación con JS (?)) 

La cookie parece no expirar, he utilizado la misma en un script de bash por como 3 meses. El link de SSO parece cambiar, pero los links antiguos siguen siendo validos, al igual que las cookies. 
"""

def getJSESSIONID(sso_link):
	driver = webdriver.Firefox()
	driver.get(sso_link)

	# Esperamos el redirect para extraer la JSESSIONID correcta.
	wait = WebDriverWait(driver, 10)
	wait.until(lambda driver: driver.current_url != sso_link)

	cookies = driver.get_cookies()

	JSESSIONID = ""

	# Iteramos por la cookies para encontrar la JSESSIONID

	for i in cookies:
		if i.get("name") == "JSESSIONID":
			JSESSIONID = i.get("value")
			break

	driver.quit()

	if JSESSIONID == "":
		sys.exit("Lamentable no se pudo extraer la cookie correctamente. ¿Usaste el link correcto?")

	return JSESSIONID

def calificaciones(cookies):
	response = requests.get('http://app4.udec.cl/infoda2/calificaciones', cookies=cookies).json()
	#print(json.dumps(response, indent=4, sort_keys=True))

	for i in response:
		print(f'{i["codigoAsignatura"]} - {i["nombreAsignatura"]} | {i["nombre"]}: {i["descripcion"]}')

def avanceAsig(cookies):
	response = requests.get('http://app4.udec.cl/infoda2/curricular/avanceAsig', cookies=cookies)
	file = open(f"avanceAsig-{int(time.time())}.pdf", 'wb')
	file.write(response.content)
	file.close()

def avanceCurr(cookies):
	response = requests.get('http://app4.udec.cl/infoda2/curricular/avanceCurr', cookies=cookies)
	file = open(f"avanceCurr-{int(time.time())}.pdf", 'wb')
	file.write(response.content)
	file.close()

# Los certificados de alumno regular tienen 15 tipos:
#
# 1  Trámites De Asignación Familiar
# 2  Trámites De Postulación A Becas
# 3  Trámites De Pase Escolar
# 4  Trámites De Pensión De Orfandad
# 5  Trámites De Rebaja De Pasajes
# 6  Trámites En Cajas De Compensación
# 7  Trámites En El Cantón De Reclutamiento
# 8  Trámites En Administradoras De Fondos De Pensiones
# 9  Trámites En El Fondo Nacional De Salud FONASA
# 10 Trámites En El Instituto De Normalización Previsional INP
# 11 Trámites En Instituciones De Salud Previsional - ISAPRES
# 12 Trámites En Municipalidades
# 13 Trámites En Instituciones Trabajo Padres
# 14 Trámites De Práctica De Medicina Abierta
# 15 Trámites De Crédito Solidario

def certAlumno(cookies, tipo):
	response = requests.get('http://app4.udec.cl/infoda2/certificado/pdf/' + str(tipo), cookies=cookies)
	file = open(f"certificadoAlumnoRegularTipo{i}-{int(time.time())}.pdf", 'wb')
	file.write(response.content)
	file.close()

def main():

	# Revisamos si ya tenemos la cookie, en el caso que no sea asi la obtenemos y la guardamos.
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

	# Fácilmente podemos obtener todas las notas en formato JSON.
	calificaciones(cookies)

	# Podemos descargar cualquier certificado o archivo pdf, exceptuando las listas de clases. 
	# Estas son generadas en el browser, por lo que hay que parsear el JSON como con las notas. 
	#avanceAsig(cookies)
	#certAlumno(cookies, tipo)

if __name__ == "__main__":
    main()




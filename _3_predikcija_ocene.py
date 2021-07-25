# U ovom programu se na osnovu inputa sa standardnog izlaza o zeljenom filmu vrsi 
# preuzimanje osnovnih informacija sa IMDb sajta, i vrsi se predikcija ocene uz
# pomoc prethodno istreniranog modela linearne regresije. Program ispisuje predikciju
# ocene na standardni izlaz. 

# Uvozim neophodne module i biblioteke.
import pickle
import re
import requests
import numpy as np
import pandas as pd
import imdb
from _1_imdb_scraping import get_mesec, get_oskari, get_druge_nagrade



def get_osnovni_podaci(id_filma):
	"""
	Koristeci metode klase IMDb iz eksternog paketa IMDbpy, funkcija pristupa
	individualnoj stranici datog filma i preuzima i vraca osnovne podatke o filmu. 
	"""
	i = imdb.IMDb()

	try:
		film = i.get_movie(id_filma[2:])
	except imdb._exceptions.IMDbParserError:
		print("Neispravan unos id filma")
		exit(1)	

	try: 
		naslov = film['title']
	except KeyError: 
		naslov = None 

	try: 
		godina = film['year']
	except KeyError: 
		godina = "n/a" 

	try: 
		zanr = film['genres']
	except KeyError: 
		zanr = []
	
	try: 
		rezija = film['directors']
	except KeyError: 
		rezija = [] 
	else:
		rezija = [reziser['name'] for reziser in rezija]
	
	try: 
		uloge = film['cast']
	except KeyError: 
		uloge = []
	else:
		uloge = [uloga['name'] for uloga in uloge[:2]]
		
	osnovni_podaci = {
					"naslov" : naslov, 
					"godina" : godina, 
					"zanr" : zanr,
					"rezija" : rezija,
					"uloge" : uloge
					}

	return osnovni_podaci


def prikaz_filma(naslov, godina, zanr, rezija, uloge):
	"""
	Stampa na standardni izlaz osnovne informacije o datom filmu.
	"""
	prikaz = f"\n\n\n\n Film: {naslov} ({godina})\n"
	prikaz += " ==================================================="
	prikaz += "\n"
	prikaz += f" Zanr: {', '.join(zanr)}\n"
	prikaz += f" Rezija: {', '.join(rezija)}\n"	
	prikaz += f" Glavne uloge: {', '.join(uloge)}\n"
	prikaz += " ===================================================\n"
	print(prikaz)


def nedovoljno_podataka_poruka():
	
	print("Nazalost, nema dovoljno podataka za predikciju ocene filma.")
	exit(1)


def get_dodatni_podaci(id_filma):
	"""
	Koristeci funkcije iz python fajla 'imdb_scraping.py', funkcija pristupa 
	individualnim stranicama datog filma, rezisera i glavnih uloga 
	i preuzima i vraca ostale neophodne podatke. 
	"""
	def broj_meseca(mesec):

		mapa_meseci = {
						"January" : 1, 
						"February" : 2, 
						"March" : 3, 
						"April" : 4, 
						"May" : 5,
						"June" : 6, 
						"July" : 7, 
						"August" : 8, 
						"September" : 9, 
						"October" : 10, 
						"November" : 11, 
						"December" : 12
						}

		broj_meseca = mapa_meseci[mesec]
		return broj_meseca

	mesec_izlaska = get_mesec(id_filma)

	if mesec_izlaska == "NA":
		nedovoljno_podataka_poruka()
	else:
		mesec_izlaska = broj_meseca(mesec_izlaska)

	# Preuzimanje id-eva rezisera i prva dva navedena glumca
	url = f"https://www.imdb.com/title/{id_filma}/"
	response = requests.get(url)
	html = response.text
	m = re.search('Director.+\s.+(nm[0-9]{7,8})[\S\s]+?(?:Star).+\s.+(nm[0-9]{7,8}).+\s.+(nm[0-9]{7,8})', html)
	if not m:
		nedovoljno_podataka_poruka()
	else:
		id_rezisera = m.group(1)
		id_glumca1 = m.group(2)
		id_glumca2 = m.group(3)	

	br_oskara_rezisera = get_oskari(id_rezisera)
	br_dr_nagrada_rezisera = get_druge_nagrade(id_rezisera)
	
	br_oskara_glumca1 = get_oskari(id_glumca1)
	br_dr_nagrada_glumca1 = get_druge_nagrade(id_glumca1)

	br_oskara_glumca2 = get_oskari(id_glumca2)
	br_dr_nagrada_glumca2 = get_druge_nagrade(id_glumca2)

	dodatni_podaci = {
		"mesec_izlaska" : mesec_izlaska,
		"br_oskara_rezisera" : br_oskara_rezisera,
		"br_dr_nagrada_rezisera" : br_dr_nagrada_rezisera,
		"br_oskara_glumca1" : br_oskara_glumca1,
		"br_dr_nagrada_glumca1" : br_dr_nagrada_glumca1,
		"br_oskara_glumca2" : br_oskara_glumca2, 
		"br_dr_nagrada_glumca2" : br_dr_nagrada_glumca2
		}

	return dodatni_podaci



if __name__ == '__main__':

	naslov_filma = input("\nUnesite naslov filma (engl.): ")

	# Uz pomoc metoda klase IMDb iz IMDbpy biblioteke, vrsim pretragu 
	# filmova u IMDb bazi prema naslovu koji se unosi na standardni ulaz. 
	i = imdb.IMDb()

	try:
	    rezultati = i.search_movie(naslov_filma)
	except imdb.IMDbError:
	    print("\nNeuspešno povezivanje. Pokušajte ponovo.")
	    exit(1)


	if len(rezultati) == 0:
		print(f'\nNema rezultata za "{naslov_filma}"')
		exit(1)

	# Posto se program bavi filmovima koji jos uvek nisu izasli, 
	# rezultati pretrazivanja ne treba da prikazuju filmove iz trenutne ili 
	# prethodnih godina. Stoga filtriram rezultate i izdvajam naslove koji 
	# zadovoljavaju uslov da je godina izdanja 2021. ili kasnije.
	validni_rezultati = []
	for naslov in rezultati: 
		poklapanje = re.search("\((\d{4})\)", naslov['long imdb title'])

		if not poklapanje: 
			godina = 3000  # filmovi bez navedene godine su uglavnom filmovi koji jos nisu izasli
		else:
			godina = int(poklapanje.group(1))

		if godina >= 2021:  
			validni_rezultati.append(naslov)

	# Stampam rezultate pretrazivanja na standardni izlaz. 
	if len(validni_rezultati) > 1:
		rez = "rezultata"
	else:
		rez = "rezultat"
	
	r = "\n"
	r += f'{len(validni_rezultati)} {rez} za "{naslov_filma}":\n\n'
	r += " ---------------------------------------------------------------------\n"
	r += "           IMDb Id           Naslov\n"
	r += " ---------------------------------------------------------------------\n"
	for broj, naslov in enumerate(validni_rezultati, start=1):
		r += f"{broj:^10} tt{i.get_imdbID(naslov):<15} {naslov['long imdb title']}\n"

	print(r)

	id_filma = input("\n\nUnesite IMDb id filma: ")

	# Nakon sto se unese Id trazenog filma, uz pomoc prethodno
	# definisanih funkcija, vrsi se preuzimanje svih neophodnih podataka, 
	# ukoliko su oni dostupni, za primenu modela za predikciju. 
	
	info = get_osnovni_podaci(id_filma)

	# Stampam osnovne informacije o filmu pozivanjem funkcije prikaz_filma.
	prikaz_filma(**info)

	# Posto je zanr vec preuzet, iskoristicu ga za dataset. 
	zanr = info["zanr"]
	if not zanr: 
		nedovoljno_podataka_poruka()
	else:
		zanr = ', '.join(info["zanr"])

	# Pozivam funkciju dodatni_podaci radi preuzimanja ostalih podataka. 
	dodatni_podaci = get_dodatni_podaci(id_filma)

	# Centralizujem sve ulazne varijable u jedan recnik. 
	ulazni_podaci = {"zanr" : zanr}
	ulazni_podaci.update(dodatni_podaci)

	# Unosim ulazne varijable u pandas strukturu podataka - dataframe i
	# dodatno sredjujem podatke. 
	df_film = pd.DataFrame(ulazni_podaci, columns=ulazni_podaci.keys(), index=[0])
	df_zanrovi = df_film['zanr'].str.get_dummies(sep=', ')
	df_film = pd.concat([df_film.drop(["zanr"],  axis=1), df_zanrovi], axis=1)


	with open("prediktori_modela.pickle", "rb") as ulaz:
		prediktori_modela = pickle.load(ulaz)

	# features_modela = ['mesec_izlaska', 'br_oskara_rezisera', 'br_dr_nagrada_rezisera', \
	# 		       'br_oskara_glumca1', 'br_dr_nagrada_glumca1', 'br_oskara_glumca2', \
	# 		       'br_dr_nagrada_glumca2', 'Action', 'Adventure', 'Animation', \
	# 		       'Biography', 'Comedy', 'Crime', 'Drama', 'Family', 'Fantasy', 'History', \
	# 		       'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', \
	# 		       'Thriller', 'War', 'Western']

	df_film = df_film.reindex(df_film.columns.union(prediktori_modela, sort=False), axis=1, fill_value=0)


	# Primenjujem model linearne regresije i stampam rezultate na standardni izlaz.

	with open("reg_model.pickle", "rb") as ulaz:
		model = pickle.load(ulaz)

	# Definisem nezavisne varijable
	x = df_film
	predikcija_ocene = model.predict(x)
	predikcija_ocene = round(predikcija_ocene[0], 1)

	print(f" Predikcija ocene: {predikcija_ocene}\n\n\n")

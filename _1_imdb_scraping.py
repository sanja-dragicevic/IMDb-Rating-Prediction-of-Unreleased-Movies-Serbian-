# Ovom skriptom se vrsi preuzimanje podataka sa sajta imdb.com 
# web scraping tehnikom, i to u dve faze.

# Izvrsavanjem ove skripte kao glavnog programa, vrsi se preuzimanje podataka 
# o definisanim filmovima sa IMDb-a i njihovo skladistenje u dataframe i eksportovanje
# u csv fajl.
# U ovoj skripti je dodatno definisano nekoliko funkcija za preuzimanje dodatnih 
# informacija o filmu nad kojim se funkcija poziva, takodje sa IMDb stranice. 

# Kriterijumi za filmove koji su ukljuceni u ovu analizu su:
# - da predstavljaju "feature film", 
# - da je zemlja porekla SAD
# - da su izasli izmedju 2010. i 2020. godine
# - da imaju preko 10.000 glasova


# Uvozim neophodne Python biblioteke i module
import pickle
import re
import requests
import numpy as np
import pandas as pd


class Film:
	"""
	Definisem klasu Film za skladistenje preuzetih informacija o filmovima radi 
	jednostavnijeg upravljanja i daljeg koriscenja datih informacija.
	"""

	def __init__(self, id_filma, zanr, id_rezisera, id_glumca1, id_glumca2, ocena, mesec_izlaska=None, \
				br_oskara_rezisera=0, br_dr_nagrada_rezisera=0, br_oskara_glumca1=0, br_dr_nagrada_glumca1=0, \
				br_oskara_glumca2=0, br_dr_nagrada_glumca2=0):
		self.id_filma = id_filma
		self.zanr = zanr
		self.id_rezisera = id_rezisera
		self.id_glumca1 = id_glumca1
		self.id_glumca2 = id_glumca2
		self.ocena = ocena
		self.mesec_izlaska = mesec_izlaska
		self.br_oskara_rezisera = br_oskara_rezisera
		self.br_dr_nagrada_rezisera = br_dr_nagrada_rezisera
		self.br_oskara_glumca1 = br_oskara_glumca1
		self.br_dr_nagrada_glumca1 = br_dr_nagrada_glumca1
		self.br_oskara_glumca2 = br_oskara_glumca2
		self.br_dr_nagrada_glumca2 = br_dr_nagrada_glumca2

	def kao_recnik(self):
		"""
		Klasni metod koji vrsi skladistenje podataka objekta u recnik. 
		"""
		return {
			"id_filma" : self.id_filma,
			"zanr" : self.zanr,
			"id_rezisera" : self.id_rezisera,
			"id_glumca1" : self.id_glumca1,
			"id_glumca2" : self.id_glumca2,
			"ocena" : self.ocena,
			"mesec_izlaska" : self.mesec_izlaska,
			"br_oskara_rezisera" : self.br_oskara_rezisera,
			"br_dr_nagrada_rezisera" : self.br_dr_nagrada_rezisera,
			"br_oskara_glumca1" : self.br_oskara_glumca1,
			"br_dr_nagrada_glumca1" : self.br_dr_nagrada_glumca1,
			"br_oskara_glumca2" : self.br_oskara_glumca2, 
			"br_dr_nagrada_glumca2" : self.br_dr_nagrada_glumca2
			}


def get_mesec(id_filma):
	"""
	Pristupa individualnoj IMDb stranici filma nad kojim se poziva i preuzima Release Date, 
	odnosno mesec iz datuma jer se taj datum ne prikazuje u rezultatima pretrazivanja.  
	"""
	url = f"https://www.imdb.com/title/{id_filma}"
	response = requests.get(url)
	m = re.search('Release Date\:.+>\s[0-9]+\s([A-Za-z]+)', response.text)
	if not m:
		return "NA"
	else: 
		return m.group(1)


def get_oskari(id_osobe): #pobede ili nominacije
	"""
	Pristupa individualnoj IMDb stranici osobe nad kojom se poziva i preuzima broj osvojenih 
	Oskara ili broj nominacija za Oskara. Obzirom da Oskar predstavlja najprestizniju filmsku 
	nagradu, pretpostavka je da, u pogledu popularnosti filmova kod sire publike, 
	pobeda i nominacija nose jednaku tezinu.
	"""
	url = f"https://www.imdb.com/name/{id_osobe}"
	response = requests.get(url)
	m = re.search('(?:Won|Nominated for)\s.+([0-9])+\s+Oscar', response.text)
	if not m:
		return 0
	else: 
		return int(m.group(1))


def get_druge_nagrade(id_osobe): #pobede 
	"""
	Pristupa individualnoj IMDb stranici osobe nad kojom se poziva i preuzima ukupan 
	broj drugih osvojenih nagrada i priznanja (dakle, iskljucujuci Oskara, ali i druge 
	velike nagrade poput nagrade Zlatnog globusa, Emija itd).  
	"""
	url = f"https://www.imdb.com/name/{id_osobe}"
	response = requests.get(url)
	m = re.search('([0-9]+) wins', response.text)
	if not m:
		return 0
	else: 
		return int(m.group(1))



if __name__ == '__main__':

	# Otvaram listu filmova u koju cu da smestim skrejpovane podatke o svakom pojedinacnom filmu 
	# u vidu instance klase Film. 
	lista_filmova = []

	# Za potrebe skrejpovanja podataka o vise od 2000 naslova ispisanih na desetinu strana sa 
	# po 250 naslova, uvodim promenljivu 'broj_naslova' u koju smestam niz brojeva kroz koji mogu 
	# da iteriram i koristim za poziv ka svakoj pojedinacnoj strani u rezultatima pretrazivanja. 
	broj_naslova = np.arange(1, 2500, 250)

	# Vrsim preuzimanje podataka sa stranica IMDb-a koje pokazuju rezultate pretrazivanja.
	for redni_broj in broj_naslova:

		url = f"https://www.imdb.com/search/title/?title_type=feature&release_date=2010-01-01,2020-12-31&num_votes=10000,&countries=us&sort=num_votes,desc&count=250&start={redni_broj}&ref_=adv_nxt"
		response = requests.get(url)
		html = response.text
		pattern = re.compile('href=\"\/title\/(tt[0-9]{7,8})[\S\s]+?(?:genre)\">\s([A-Za-z\s\-\,]+)[\s\S]+?(?:<strong>([0-9\.]{3})<\/strong>)[\S\s]+?(?:Director.+\s.+(nm[0-9]{7,8}))[\S\s]+?(?:Star.+\s.+(nm[0-9]{7,8}).+\s.+\s.+(nm[0-9]{7,8}))')
		
		for m in pattern.finditer(html):

			id_filma = m.group(1).strip()
			zanr = m.group(2).strip()
			id_rezisera = m.group(4).strip()
			id_glumca1 = m.group(5).strip()
			id_glumca2 = m.group(6).strip()
			ocena = m.group(3).strip()

			# Instanciram objekat klase Film i prosledjujem preuzete podatke.
			film = Film(id_filma, zanr, id_rezisera, id_glumca1, id_glumca2, ocena)
			lista_filmova.append(film)

	print(f"\nPreuzimanje osnovnih podataka je završeno. Preuzeto ukupno {len(lista_filmova)} naslova.")

	# Iteriram kroz listu objekata klase Film i dopunjujem objekte dodatnim informacijama.
	for film in lista_filmova:

		film.mesec_izlaska = get_mesec(film.id_filma)
		film.br_oskara_rezisera = get_oskari(film.id_rezisera)
		film.br_dr_nagrada_rezisera = get_druge_nagrade(film.id_rezisera)
		film.br_oskara_glumca1 = get_oskari(film.id_glumca1)
		film.br_dr_nagrada_glumca1 = get_druge_nagrade(film.id_glumca1)
		film.br_oskara_glumca2 = get_oskari(film.id_glumca2)
		film.br_dr_nagrada_glumca2 = get_druge_nagrade(film.id_glumca2)


	print(f"\nPreuzimanje dodatnih podataka je završeno.")

	# Skladistim informacije iz svakog objekta klase Film u dataframe.
	filmovi_df = pd.DataFrame([film.kao_recnik() for film in lista_filmova])

	# Eksportujem dataframe u csv fajl.
	filmovi_df.to_csv('filmovi.csv')

	with open('filmovi_df.pickle', 'wb') as izlaz:
		pickle.dump(filmovi_df, izlaz)





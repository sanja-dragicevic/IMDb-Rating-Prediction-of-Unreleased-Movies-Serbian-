# U ovoj skripti se vrsi priprema podataka za masinsko ucenje i treniranje regresionog modela. 

#Uvozim neophodne module i biblioteke.
import pickle
import pandas as pd 
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import max_error
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from matplotlib import style
import seaborn as sns



if __name__ == '__main__':

	# ------------------------------------------------------------------------------------------------------
	# I OBRADA PODATAKA
	# ------------------------------------------------------------------------------------------------------

	# with open('filmovi_df.pickle', 'rb') as ulaz:
	# 	df = pickle.load(ulaz)

	# Ucitavam csv fajl u dataframe.
	df = pd.read_csv('filmovi.csv')
	print(df.head())
	
	# Pravim kopiju dataframe-a pre implementiranja promena.
	df_1 = df.copy()

	# Odmah uklanjam kolone koje nisu potrebne radi boljeg pregleda podataka.
	df_1.drop(columns=['Unnamed: 0', 'id_filma', 'id_rezisera', 'id_glumca1', 'id_glumca2'], axis=1, inplace=True)

	# Proveravam postojanje null vrednosti. 
	print(df_1.isnull().sum())

	# Postoji 6 redova/naslova bez inputa za mesec_izlaska. S obzirom da je u pitanju mali broj 
	# u odnosu na ukupan broj opservacija, mogu ukloniti date redove. 

	# Uklanjam redove sa null vrednostima.
	df_1.dropna(axis=0, inplace=True)

	# Uvid u tipove podataka u datasetu
	print(df_1.info())

	# Vidim da imam 2 kolone tipa object. Posto model radi iskljucivo sa numerickim podacima, 
	# potrebno je konvertovati sve kategorijalne varijable u numericke. 

	# U koloni "mesec_izlaska" zamenjujem tekstualne vrednosti meseca u numericke vrednosti.
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

	df_1 = df_1.replace({'mesec_izlaska': mapa_meseci})

	print(df_1.head())

	print(df_1['mesec_izlaska'].value_counts())

	# S obzirom da zanr takodje predstavlja kategorijalnu varijablu, pravim "dummy" kolone za svaki zanr. 
	df_zanrovi = df_1['zanr'].str.get_dummies(sep=', ')
	df_2 = pd.concat([df_1.drop(['zanr'], axis=1), df_zanrovi], axis=1)

	print(df_2.head())

	# ------------------------------------------------------------------------------------------------------
	# II EKSPLORATIVNA ANALIZA PODATAKA
	# ------------------------------------------------------------------------------------------------------

	# Osnovni statistike nad podacima
	pd.set_option('display.precision', 3)
	df_2.describe()

	# Stampam koeficijente korelacije izmedju nezavisnih i zavisne varijable
	korelacije = df_2.corr(method='pearson')
	print(korelacije['ocena'].sort_values(ascending=False))

	# Prikaz odnosa izmedju zavisne varijable i nezavisnih
	odnosi = sns.pairplot(data=df_2, 
					     x_vars=list(df_2.drop(['ocena'], axis=1).columns), 
					     y_vars=['ocena'], 
					     kind='scatter')

	# ------------------------------------------------------------------------------------------------------
	# III TRENIRANJE MODELA LINEARNE REGRESIJE
	# ------------------------------------------------------------------------------------------------------

	# Definisem finalni dataset i izlaznu varijablu
	podaci_1 = df_2.copy()
	target = "ocena"	

	X = podaci_1.drop(columns=[target], axis=1)
	y = podaci_1[target]

	# Sacuvacu feature-e (prediktore) modela u binarni fajl.
	with open('prediktori_modela.pickle', 'wb') as izlaz:
		pickle.dump(list(X.columns), izlaz)

	# Podela podataka na trening i test podatke
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

	# Instanciranje objekat linearne regresije
	model = LinearRegression()

	# Fitovanje podataka u model (treniranje modela)
	model.fit(X_train, y_train)

	tacnost_modela = model.score(X_test, y_test)
			
	# Primena modela nad test podacima
	y_predikcije = model.predict(X_test)

	# Evaluacija performansi modela

	y_stvarne = y_test

	# Kalkulacija srednje apsolutne greske
	mae = mean_absolute_error(y_stvarne, y_predikcije)

	# Kalkulacija srednje kvadratne greske
	mse = mean_squared_error(y_stvarne, y_predikcije)
	rmse = np.sqrt(mse)

	# Kalkulacija maksimalne greske
	max_greska = round(max_error(y_stvarne, y_predikcije), 1)

	# Kalkulacija koeficijenta determinacije
	koef_det = r2_score(y_stvarne, y_predikcije)

	# Stampam koeficijente nezavisnih varijabli
	ocene_vaznosti = model.coef_

	print("Koeficijenti nezavisnih varijabli:")
	for f,o in zip(list(X_train.columns), ocene_vaznosti):
		print(f"Prediktor: {f}, Ocena: {o:.3f}")
	# plot feature importance
	plt.bar([x for x in range(len(ocene_vaznosti))], ocene_vaznosti)
	plt.show()

	# Stampam rezultate ocena performansi modela
	# Definisem objekat sa tekstom izvestaja radi mogucnosti formatiranja

	ocene = {
	        "1" : "Veličina test uzorka",
	        "2" : "Koeficijent determinacije", 
	        "3" : "Srednja apsolutna greška", 
	        "4" : "Srednja kvadratna greška", 
	        "5" : "Maksimalna greška"
	        }

	r = "Izveštaj o performansama modela:"
	r += "\n\n"
	r += " =======================================================\n"
	r += "  Model: Linearna regresija\n"
	r += " _______________________________________________________\n"
	r += f"  {ocene['1']:<25} {len(y_predikcije):>20}\n"
	r += " _______________________________________________________\n"
	r += "  Performanse modela:\n\n"
	r += f"  {ocene['2']:<25} {koef_det:>20.3f}\n"
	r += f"  {ocene['3']:<25} {mae:>20.3f}\n"
	r += f"  {ocene['4']:<25} {mse:>20.3f}\n"
	r += f"  {ocene['5']:<25} {max_greska:>20}\n\n"
	r += " =======================================================\n"
	print(r)


	# Cuvam model u pickle fajlu.
	with open('reg_model.pickle', "wb") as izlaz:
		pickle.dump(model, izlaz) 



#TODO:
#	Uzupełnić "dokumentacje"
#	Dodać komentarze w funkcjach

#Funkcja example
#
#Opis:
#	short description
#
#Argumenty:
#	type	name	description
#
#Printy:
#	function	description
#
#Return:
#	type	decription
#
#Todo:
#	description
#
#Użyte funkcje:
#	name

from PIL import Image			#Moduł do przetwarzania obrazów
import numpy					#Moduł do macierzy
import math						#Moduł do prostych operacji na skalarach
import sys						#Moduł do obsługi funkcji systemowych
import pickle					#Moduł do zrzutu kofiguracji do pliku
import time						#Moduł do obsługi czasu
import hashlib;					#Moduł do obsługi hashowania (md5)
from functools import partial;	#Moduł przydatny przy obsłudza zdarzeń PyQT

#Globalna zmienna konfigurujaca maksymalne wartosci
global zmienne;
zmienne = {"oMax":1023,
			"sMax":31}
			
def cli_progress_test(val, max_val, bar_length=50):
	"""
	Funkcja cli_progress_test

	Opis:
		Funkcja odpowiedzialna za wyświetlanie paska postępu w konsoli

	Argumenty:
		int val			aktualna wartość
		int max_val 	maksymalna wartość
		int bar_length	szerokość paska postępu (domyślnie 50)

	Printy:
		Pasek postępu

	Return:
		Brak

	Todo:
		Brak

	Użyte funkcje:
		round
		format
		sys.stdout.write
		sys.stdout.flush()
	"""
	percent = val/max_val;
	hashes = '#' * int(round(percent * bar_length))
	spaces = ' ' * (bar_length - len(hashes))
	sys.stdout.write("\rPostep: [{0}] {1}%     ".format(hashes + spaces, int(round(percent * 100000))/1000))
	sys.stdout.flush()

def skaluj(D):
	"""
	Funkcja skaluj
	
	Opis:
		Funkcja skalująca macierz poprzez uśrednienie czwórek pikseli
		Zwraca przeskalowaną macierz
	
	Argumenty:
		numpy.matrix D	macierz do przeskalowania
	
	Printy:
		Brak
	
	Return:
		numpy.matrix	przeskalowana macierz
	
	Todo:
		Brak
	
	Użyte funkcje:
		numpy.matrix
		range
		list.append
		numpy.matrix.mean
	"""
	D = numpy.matrix(D)
	D_ = []
	for i in range(int(D.shape[0]/2)):
		D_.append([])
		for j in range(int(D.shape[1]/2)):
			D_[i].append(D[2*i:2*(i+1),2*j:2*(j+1)].mean())
	return numpy.matrix(D_);

def rangeBlocks(A, blockSize):
	"""
	Funkcja rangeBlocks

	Opis:
		Funkcja dzieląca macierz A na podmacierze o podanym rozmiarze
		niezachodzące na siebie
		Zwraca listę dwuwymiarową podmacierzy

	Argumenty:
		numpy.matrix A			macierz do podzielenia
		int          blockSize	rozmiar bloku

	Printy:
		Brak

	Return:
		numpy.matrix list[][]	dwuwymiarowa lista

	Todo:
		Brak

	Użyte funkcje:
		range
		list.append
	"""
	R = [];
	for i in range(int(A.shape[0]/blockSize)):
		R.append([])
		for j in range(int(A.shape[1]/blockSize)):
			R[i].append(A[blockSize*i:blockSize*(i+1),blockSize*j:blockSize*(j+1)])
	return R;

def domainBlocks(A, blockSize, delta, apka):
	"""
	Funkcja domainBlocks

	Opis:
		Funkcja dzieląca macierz A na podmacierze o podanym rozmiarze
		nachodzące na siebie, o pewnym odstępie początków tych macierzy
		Zwraca listę dwuwymiarową podmacierzy

	Argumenty:
		numpy.matrix      A			macierz do podzielenia
		int               blockSize	rozmiar bloku
		int               delta		wartość odstępu
		QtGui.QmainWindow apka		uchwyt do aplikacji

	Printy:
		apka.progress	pasek postepu

	Return:
		numpy.matrix list[][]	dwuwymiarowa lista

	Todo:
		Brak

	Użyte funkcje:
		range
		list.append
		apka.progress
	"""
	D = [];
	for i in range(int((A.shape[0]-2*blockSize)/delta)+1):
		apka.progress(i, (int((A.shape[1]-2*blockSize)/delta)+1));
		D.append([])
		for j in range(int((A.shape[1]-2*blockSize)/delta)+1):
			D[i].append(skaluj(A[delta*i:delta*i+2*blockSize,delta*j:delta*j+2*blockSize]))
	apka.progress(1,1);
	print("")
	return D;

def porownaj(R,D):
	"""
	Funkcja porownaj

	Opis:
		Funkcja porownująca dwie macierze, gdzie jedna jest większa od
		drugiej i poddana jest pewnym przekształceniom.

	Argumenty:
		numpy.matrix      R			macierz wzorcowa
		numpy.matrix      D			macierz do porównania

	Printy:
		apka.progress	pasek postepu

	Return:
		list 	[	
			int s	scale parameter
			int o	luminance offset
			int e	wyliczona różnica (błąd)
			]

	Todo:
		Rozwiązać problem warningów w konsoli

	Użyte funkcje:
		numpy.matrix
		numpy.matrix.mean
		numpy.array
		math.log
		numpy.linalg.norm
	"""
	global zmienne;
	R = numpy.matrix(R);
	D = numpy.matrix(D);
	R_ = R.mean();
	D_ = D.mean();
	try: #Wystepuje problem z nieskonczonoscia
		s = (numpy.array(R-R_)*numpy.array(D-D_)).sum() / (numpy.array(D-D_)*numpy.array(D-D_)).sum()
		if s < -zmienne["sMax"]:
			s=-zmienne["sMax"];
		elif s>zmienne["sMax"]:
			s=zmienne["sMax"];
		o = R_ - s*D_;
		if o > zmienne["oMax"]:
			o=zmienne["oMax"]
		elif o<-zmienne["oMax"]:
			o=-zmienne["oMax"]
		E = math.log(numpy.linalg.norm(R-(s*D+o)))
		return [s, o, E]
	except:
		return [0, 0, 2e15]

def przeksztalcenie(R, typ):
	"""
	Funkcja przeksztalcenie

	Opis:
		Funkca wykonująca przekształcenia afiniczna na podanej macierzy

	Argumenty:
		numpy.matrix R		macierz na której będzie wykonymane 
							przekształcenie
		int          typ	typ przekształcenia (0-7):
							0-3	brak
							4-7	lustrzane odbicie
							0 - brak
							1 - obrót o 90 stopni w prawo
							2 - obrót o 180 stopni w prawo
							3 - obrót o 270 stopni w prawo

	Printy:
		function	description

	Return:
		numpy.matrix	macierz po przekształceniach

	Todo:
		brak

	Użyte funkcje:
		numpy.matrix
		numpy.rot90
		numpy.fliplr
	"""
	R = numpy.matrix(R)
	if(typ == 0):
		return R;
	elif typ == 1:
		return numpy.rot90(R,1);
	elif typ == 2:
		return numpy.rot90(R,2);
	elif typ == 3:
		return numpy.rot90(R,3);
	elif typ == 4:
		return numpy.fliplr(R);
	elif typ == 5:
		return numpy.rot90(numpy.fliplr(R),1);
	elif typ == 6:
		return numpy.rot90(numpy.fliplr(R),2);
	elif typ == 7:
		return numpy.rot90(numpy.fliplr(R),3);

def przesunGora(A, n = 4):
	"""
	Funkcja przesunGora

	Opis:
		Funkcja przesuwająca macierz o n wierszy do góry

	Argumenty:
		numpy.matrix A	macierz do przesunięcia
		int          n	wartość przesunięcia

	Printy:
		brak

	Return:
		numpy.matrix	przesunięta macierz

	Todo:
		brak

	Użyte funkcje:
		numpy.matrix
	"""
	A = numpy.matrix(A)
	B = numpy.matrix(A[0:n,:]);
	A[0:A.shape[0]-n, :] = A[n:A.shape[0], :]
	A[A.shape[0]-n:, :] = B;
	return A;

def przesunLewo(A, n = 4):
	"""
	Funkcja przesunGora

	Opis:
		Funkcja przesuwająca macierz o n kolumn w lewo

	Argumenty:
		numpy.matrix A	macierz do przesunięcia
		int          n	wartość przesunięcia

	Printy:
		brak

	Return:
		numpy.matrix	przesunięta macierz

	Todo:
		brak

	Użyte funkcje:
		numpy.matrix
	"""
	A = numpy.matrix(A)
	B = numpy.matrix(A[:,0:n]);
	A[:, 0:A.shape[1]-n] = A[:,n:A.shape[1]]
	A[:,A.shape[1]-n:] = B;
	return A;

def usun2LSB(R):
	"""
	Funkcja usun2LSB

	Opis:
		Funkcja zerująca dwa najmniej znaczące bity dla każdej komórki
		podanej macierzy

	Argumenty:
		numpy.matrix R	macierz do wyzerowania bitów

	Printy:
		brak

	Return:
		list [
			numpy.matrix R			macierz z wyzerowanymi bitami
			str          wiadomosc	wartosci odczytane z 2 LSB

	Todo:
		brak

	Użyte funkcje:
		numpy.matrix
		format
		range
		int
	"""
	R = numpy.matrix(R)
	wiadomosc = '';
	for i in range(R.shape[0]):
		for j in range(R.shape[1]):
			binary = format(R[i,j], '08b')
			R[i,j] = int("%s00" %(binary[0:6]), 2)
			wiadomosc += binary[6:8];
	return [R, wiadomosc]

def Kompresuj(R, D, delta, apka):
	"""
	Funkcja Kompresuj

	Opis:
		Funkcja przeprowadzająca kompresję fraktalną macierzy z listy
		dwuwymiarowej R o rozmiarze i,j opierając się na
		przekształceniu macierzy z lsty dwuwymiarowej D o rozmiarze x,y
		Zwraca listę z optymalnymi przekszałceniami dla najoptymalniejszej
		macierzy D

	Argumenty:
		numpy.matrix      R[][]	macierz R
		numpy.matrix      D[][]	macierz D
		int               delta	wartość delty(deprecated)
		QtGui.QmainWindow apka	uchwyt do aplikacji

	Printy:
		apka.progress	pasek postepu kompresji
		apk.print		nie wiem na co to komu i po co

	Return:
		list [					i
			list [				j
					list [		wspolrzedne najbardziej podobnej macierzy
						int a	x
						int b	y
					]
					tmp			return funkcji porownaj oraz numer przekszt.

	Todo:
		wyrzucić delte

	Użyte funkcje:
		len
		range
		list.append
		porownaj
		przeksztalcenie
		apka.progress
		apka.print_
	"""
	D_size = (len(D), len(D[0]))
	R_size = (len(R), len(R[0]))
	stat = [[[[-1, -1], [-1, -1, -1]]] * R_size[1] for i in range(R_size[0])]
	for i in range(R_size[0]):
		for j in range(R_size[1]):
			apka.progress(i*R_size[1]+j, R_size[0] * R_size[1]);
			for a in range(D_size[0]):
				for b in range(D_size[1]):
					D_tmp = D[a][b]
					for c in range(8):
						tmp = porownaj(R[i][j], przeksztalcenie(D[a][b], c))
						if(stat[i][j][1][2] == -1 or stat[i][j][1][2] > tmp[2]):#jesli nie ustawiona lub mniejszy blad, to podmien wspolczynnniki
							tmp.append(c)
							if a>128 or a<0 or b<0 or b> 128:
								apka.print_("Zle dobrana delta, nie pomiescimy sie na 7 bitach ze wspolrzednymi");
								return -1;
							stat[i][j] = [[a,b], tmp];
							
	apka.progress(1, 1);
	apka.print_("");
	return stat;
	"""

	Funkcja Dekompresuj

	Opis:
		short description

	Argumenty:
		type	name	description

	Printy:
		function	description

	Return:
		type	decription

	Todo:
		description

	Użyte funkcje:
		name

	def Dekompresuj(size, stat, delta):
		blockSize = int(size[0]/len(stat))
		G = numpy.zeros(shape=size)+127	#Obraz poczatkowy dekompresji
		for a in range(2):			#minimalna liczba petli to 2, wiecej niewiele zmienia
			for counter in range(4):
				cli_progress_test(a*4 + counter, 8);
				if(counter == 0):
					ranges = [range(int(G.shape[0]/2/blockSize)), range(int(G.shape[1]/2/blockSize)), int(G.shape[0]/2), int(G.shape[1]/2)]
				elif(counter == 1):
					ranges = [range(int(G.shape[0]/2/blockSize), int(G.shape[0]/blockSize)), range(int(G.shape[1]/2/blockSize), int(G.shape[1]/blockSize)), 0, 0]
				elif(counter == 2):
					ranges = [range(int(G.shape[0]/2/blockSize)), range(int(G.shape[1]/2/blockSize), int(G.shape[1]/blockSize)), int(G.shape[0]/2), 0]
				elif(counter == 3):
					ranges = [range(int(G.shape[0]/2/blockSize), int(G.shape[0]/blockSize)), range(int(G.shape[1]/2/blockSize)), 0, int(G.shape[1]/2)]
				for i in ranges[0]:
					for j in ranges[1]:
						G[blockSize*i:blockSize*(i+1),blockSize*j:blockSize*(j+1)] = przeksztalcenie(skaluj(G[stat[i][j][0][0]*delta+ranges[2]:stat[i][j][0][0]*delta+ranges[2] + 2*blockSize, stat[i][j][0][1]*delta+ranges[3]:stat[i][j][0][1]*delta+ranges[3]+2*blockSize]), stat[i][j][1][3])*stat[i][j][1][0] + stat[i][j][1][1] #Ta linijka jest troszke nieczytelna :D
		cli_progress_test(1, 1);
		print("");
		return(G);
	"""

def DekompresujPojedynczy(R2, s, o):
	"""
	Funkcja DekompresujPojedynczy

	Opis:
		Dekompresja pojedyńczego bloku

	Argumenty:
		numpy.matrix R2	macierz podlegająca przekształceniu
		int          s	scale parameter
		int          o	luminance offset

	Printy:
		brak

	Return:
		numpy.matrix	przeksztalcona macierz

	Todo:
		brak

	Użyte funkcje:
		numpy.matrix
	"""
	return numpy.matrix(R2 * s + o)

def getWspDCT(M):
	"""
	Funkcja getWspDCT

	Opis:
		funkcja obliczająca współczynniki DCT i zwracająca pierwsze sześć
		w kolejności zig-zag

	Argumenty:
		numpy.matrix M	macierz, której współczynniki będziemy liczyć

	Printy:
		brak

	Return:
		int[]	lista współczynników w kolejności zig-zag (pierwsze sześć)

	Todo:
		brak

	Użyte funkcje:
		numpy.matrix
		numpy.matrix.round
		numpy.multiply
		int
		round
	"""
	T = numpy.matrix([[.3536, .3536, .3536, .3536, .3536, .3536, .3536, .3536],
		[.4904, .4157, .2778, .0975, -.0975, -.2778, -.4157, -.4904],
		[.4619, .1913, -.1913, -.4619, -.4619, -.1913, .1913, .4619],
		[.4157, -.0975, -.4904, -.2778, .2778, .4904, .0975, -.4157],
		[.3536, -.3536, -.3536, .3536, .3536, -.3536, -.3536, .3536],
		[.2778, -.4904, .0975, .4157, -.4157, -.0975, .4904, -.2778],
		[.1913, -.4619, .4619, -.1913, -.1913, .4619, -.4619, .1913],
		[.0975, -.2778, .4157, -.4904, .4904, -.4157, .2778, -.0975]]);

	Q = numpy.matrix([[16, 11, 10, 16, 24, 40, 51, 61],
		[12, 13, 14, 19, 26, 58, 60, 55],
		[14, 13, 16, 24, 40, 57, 69, 56],
		[16, 17, 22, 29, 51, 87, 80, 62],
		[18, 22, 37, 56, 68, 109, 103, 77],
		[24, 35, 55, 64, 81, 104, 113, 92],
		[49, 64, 78, 87, 103, 121, 120, 101],
		[72, 92, 95, 98, 112, 100, 103, 99]]);

	Q_10 = numpy.matrix([[80, 60, 50, 80, 120, 200, 255, 255],
		[55, 60, 70, 95, 130, 255, 255, 255],
		[70, 65, 80, 120, 200, 255, 255, 255],
		[70, 85, 110, 145, 255, 255, 255, 255],
		[90, 110, 185, 255, 255, 255, 255, 255],
		[120, 175, 255, 255, 255, 255, 255, 255],
		[245, 255, 255, 255, 255, 255, 255, 255],
		[255, 255, 255, 255, 255, 255, 255, 255]]);

	D = T*(M-128)*T.H;
	C = (numpy.matrix(D)/Q).round()
	quant = 1;
	R = (numpy.multiply(C, Q)).round()
	#N = (T.H*R*T).round()+128
	return [int(round(C[0,0])/quant), int(round(C[0,1])/quant), int(round(C[1,0])/quant), int(round(C[2,0])/quant), int(round(C[1,1])/quant), int(round(C[0,2])/quant)];

def dekodujDCT(M):
	"""
	Funkcja dekodujDCT

	Opis:
		Funkcja dekodująca DCT na podstawie pierwszych 6 współczynników

	Argumenty:
		int[]	lista współczynników w kolejności zig-zag

	Printy:
		brak

	Return:
		numpy.matrix	zdekodowana ze współczynników DCT macierz

	Todo:
		brak

	Użyte funkcje:
		numpy.matrix
		numpy.multiply
		numpy.matrix.round
	"""
	T = numpy.matrix([[.3536, .3536, .3536, .3536, .3536, .3536, .3536, .3536],
		[.4904, .4157, .2778, .0975, -.0975, -.2778, -.4157, -.4904],
		[.4619, .1913, -.1913, -.4619, -.4619, -.1913, .1913, .4619],
		[.4157, -.0975, -.4904, -.2778, .2778, .4904, .0975, -.4157],
		[.3536, -.3536, -.3536, .3536, .3536, -.3536, -.3536, .3536],
		[.2778, -.4904, .0975, .4157, -.4157, -.0975, .4904, -.2778],
		[.1913, -.4619, .4619, -.1913, -.1913, .4619, -.4619, .1913],
		[.0975, -.2778, .4157, -.4904, .4904, -.4157, .2778, -.0975]]);

	Q = numpy.matrix([[16, 11, 10, 16, 24, 40, 51, 61],
		[12, 13, 14, 19, 26, 58, 60, 55],
		[14, 13, 16, 24, 40, 57, 69, 56],
		[16, 17, 22, 29, 51, 87, 80, 62],
		[18, 22, 37, 56, 68, 109, 103, 77],
		[24, 35, 55, 64, 81, 104, 113, 92],
		[49, 64, 78, 87, 103, 121, 120, 101],
		[72, 92, 95, 98, 112, 100, 103, 99]]);
	quant = 1
	R = numpy.matrix(Q)*0;
	R[0,0] = M[0]*quant;
	R[0,1] = M[1]*quant;
	R[1,0] = M[2]*quant;
	R[2,0] = M[3]*quant;
	R[1,1] = M[4]*quant;
	R[0,2] = M[5]*quant;
	R = (numpy.multiply(R, Q)).round()
	N = (T.H*R*T).round()+128
	return N;

def policzWspolczynnikiDCT(ile):
	"""
	Funkcja policzWspolczynnikiDCT

	Opis:
		Funkcja obliczająca ile bitów z puli (int ile) należy poświęcić,
		na który z sześciu współczynników DCT

	Argumenty:
		int ile		pula bitów do wykorzystania

	Printy:
		brak

	Return:
		int[]	lista definiująca ile bitów przypada na jaki wspołczynnik

	Todo:
		brak

	Użyte funkcje:
		math.floor
	"""
	ret = [math.floor(ile/7), math.floor(ile/7), math.floor(ile/7), math.floor(ile/7), math.floor(ile/7), math.floor(ile/7)]
	ile -= math.floor(ile/7)*6;
	for i in [0, 5, 1, 2, 0, 4, 0, 5, 1, 2, 4, 0, 5, 1, 2, 4, 0, 5, 1, 2, 4, 0, 5, 1, 2, 4]:
		if ile>0:
			ret[i] += 1
		else:
			break;
		ile -= 1;
	return ret

def kodujWspDCT(wsp, apka):
	"""
	Funkcja kodujWspDCT

	Opis:
		Funkcja kodująca wsp DCT na podaną liczbę bitów

	Argumenty:
		int               wsp[]	lista współczynników do zakodowania
		QtGui.QmainWindow apka	uchwyt do aplikacji, potrzebny do odczytania
								głównej konfiguracji


	Printy:
		brak

	Return:
		str		bitowa reprezentacja podanych współczynników

	Todo:
		1. usunąć komentarze, być może uzależnić Huffmana
			od jakiegoś parametru
		2. Zastanowić się czy potrzebny jest uchwyt apka

	Użyte funkcje:
		intTobin
	"""
	"""
	#Wspolczynniki DCT metodą Huffmana
	ret = '';
	
	if abs(wsp[3]) > 31 or abs(wsp[4]) > 31 or abs(wsp[5]):
		ret = '1';
	else:
		ret = '0';

	for i in range(len(wsp)):
		if (ret[0:1] == '0' and i <3) or (ret[0:1] == '1' and i>2):
			ret = '%s%s' %(ret, format(wsp[i], '+07b'))
		else:
			ret = '%s%s' %(ret, format(wsp[i], '+06b'))
		#	if abs(wsp[i])>=32:
		#		print([y, wsp, ret]);
		#		print("error");
		#		sys.exit();
	ret = ret.replace('+','0').replace('-', '1');
	if(len(ret) > 32):
		print(wsp)
	return ret;""""""
	ret = Huffman(wsp[0])
	for i in range(1, len(wsp)):
		ret += Huffman(wsp[i] - wsp[i-1])
		#ret += Huffman(wsp[i])
	if(len(ret)>40):
		print(wsp);
	ret += '0000000000000000000000000000'
	return ret[0:40];"""
	maks = policzWspolczynnikiDCT(apka.config["profile"][apka.config["profil"]]["bity"]["DCT1"]);
	ret = '';
	ret += intTobin(wsp[0], maks[0])#format(, '+0%ib' %maks[0]).replace('+','0').replace('-','1');
	ret += intTobin(wsp[1], maks[1])#format(wsp[1], '+0%ib' %maks[1]).replace('+','0').replace('-','1');
	ret += intTobin(wsp[2], maks[2])#format(wsp[2], '+0%ib' %maks[2]).replace('+','0').replace('-','1');
	ret += intTobin(wsp[3], maks[3])#format(wsp[3], '+0%ib' %maks[3]).replace('+','0').replace('-','1');
	ret += intTobin(wsp[4], maks[4])#format(wsp[4], '+0%ib' %maks[4]).replace('+','0').replace('-','1');
	ret += intTobin(wsp[5], maks[5])#format(wsp[5], '+0%ib' %maks[5]).replace('+','0').replace('-','1');
	#if(len(ret)>40):
	#	print(wsp);
	#print(wsp)
	#print(binariaToDec(ret, [[8, 1], [7,1], [7,1], [5,1], [6,1], [7,1]]));
	#sys.exit()
	return ret[0:apka.config["profile"][apka.config["profil"]]["bity"]["DCT1"]];

def dekodujWspDCT(wsp, ile, apka):
	"""
	Funkcja dekodujWspDCT

	Opis:
		funkca dekodująca współczynniki DCT i zwracajaca ich listę
		zwykła konwersja liczb do postaci binarnej

	Argumenty:
		int wsp[]	współczynniki do zakodowania
		int	ile[]	zastosowanie w Huffmanie
		QtGui.QmainWindow apka	uchwyt do aplikacji

	Printy:
		brak

	Return:
		str		postać binarna

	Todo:
		1. usunąć komentarze, być może uzależnić Huffmana
			od jakiegoś parametru
		2. Zastanowić się czy potrzebny jest uchwyt apka
		3. Zastanowić się po co był argument ile

	Użyte funkcje:
		policzWspolczynnikiDCT
		binariaToDec
	"""
	"""
	#Wspolczynniki DCT metodą Huffmana
	ret = []
	wsp += '0'*ile*2
	for i in range(ile):
		if wsp[0:2] == '00':
			wsp=wsp[2:]
			dodaj = 0
			ile = 0;
		if wsp[0:3] == '010':
			wsp=wsp[3:]
			dodaj = 1
			ile = 1;
		if wsp[0:3] == '011':
			wsp=wsp[3:]
			dodaj = 3
			ile = 2;
		if wsp[0:3] == '100':
			wsp=wsp[3:]
			dodaj = 7
			ile = 3;
		if wsp[0:3] == '101':
			wsp=wsp[3:]
			dodaj = 15
			ile = 4;
		if wsp[0:3] == '110':
			wsp=wsp[3:]
			dodaj = 31
			ile = 5;
		if wsp[0:4] == '1110':
			wsp=wsp[4:]
			dodaj = 63
			ile = 6;
		if wsp[0:5] == '11110':
			wsp=wsp[5:]
			dodaj = 127
			ile = 7;
		if wsp[0:6] == '111110':
			wsp=wsp[6:]
			dodaj = 255
			ile = 8;
		if wsp[0:7] == '1111110':
			wsp=wsp[7:]
			dodaj = 511
			ile = 9;
		if wsp[0:8] == '11111110':
			wsp=wsp[8:]
			dodaj = 1023
			ile = 10;
		if wsp[0:9] == '111111110':
			wsp=wsp[9:]
			dodaj = 2047
			ile = 11;
			
		
		if ile == 0:
			liczba = 0
		else:
			liczba = int(wsp[1:1+ile], 2);
			if(wsp[0:1] == '0'):
				liczba = -liczba + dodaj;
			else:
				liczba = -dodaj + liczba
		wsp = wsp[1+ile:]
		if(i == 0):
			ret.append(liczba)
		else:
			ret.append(liczba + ret[i-1])
	return ret"""
	maks = policzWspolczynnikiDCT(apka.config["profile"][apka.config["profil"]]["bity"]["DCT2"]);
	return binariaToDec(wsp, [[maks[0], 1], [maks[1],1], [maks[2],1], [maks[3],1], [maks[4],1], [maks[5],1]])

def kodujDCTJPEG(R, apka):
	"""
	Funkcja kodujDCTJPEG

	Opis:
		Kodowanie dwuwymiarowej tablicy o elementach numpy.matrix
		i zapisanie w dwuwymiarowej tablicy o elementch str zawierająca
		zakodowane do postaci binarnej współczynniki DCT

	Argumenty:
		numpy.matrix      R[][]	dwuwymiarowa tablica macierzy
		QtGui.QmainWindow apka	uchwyt do aplikacji

	Printy:
		brak

	Return:
		str[][]		dwuwymiarowa tablica zakodowanych do postaci binarnej
					współczynniów DCT

	Todo:
		1. Poprawić opis

	Użyte funkcje:
		len
		range
		cli_progress_test
		getWspDCT
		kodujWspDCT
	"""
	R_size = (len(R), len(R[0]))
	wsp = [[None] * R_size[1] for i in range(R_size[0])]
	for i in range(R_size[0]):
		for j in range(R_size[1]):
			apka.progress(i*len(R) + j, len(R)*len(R));
			wsp[i][j] = kodujWspDCT(getWspDCT(R[i][j]), apka);
	apka.progress(1, 1);
	print("");
	return wsp;

def getMapping(R, Size, password = None):
	"""
	Funkcja getMapping

	Opis:
		obliczenie rozkładu mapowania na podstawie bloku lub hasła,
		zwrócenie dwuwymiarowej listy o rozmiarze Size,Size
		ze współrzędnymi, na które mapować

	Argumenty:
		numpy.matrix R			blok/lista-hasło
		int          Size		rozmiar bloku, na jaki chcemy mapować
		str          password	hasło

	Printy:
		brak

	Return:
		list[][]	dwuwymiarowa lista o rozmiarze Size,Size
					ze współrzędnymi, na które mapować

	Todo:
		brak

	Użyte funkcje:
		numpy.array
		numpy.array.reshape
		range
		list.append
		str.join
		format
		sum
		int
		math.pow
		len
		pow
		math.floor
	"""
	if(password):
		K=[]#password[0:10];
		for i in password:
			K.append(ord(i));
	else:
		R = numpy.array(R).reshape(-1)
		K = R[0:10];
	B1 = K[4:7];
	M=[];

	for i in range(Size[0]):
		M.append([])
		for j in range(Size[1]):
			M[i].append([i,j]);
	X = ''.join([format(znak, '08b') for znak in B1 ])

	X_01 = sum([int(X[i])*math.pow(2, i) for i in range(len(X))])/pow(2, 24)
	Z = ''.join([format(znak, '02x') for znak in K ])
	X_02 = sum([int(Z[i], 16) for i in range(12, 18)])/96

	X_ = (X_01 + X_02) % 1
	X=[]

	for i in range(0, Size[0]):
		for j in range(0, Size[1]):
			X__=[]
			X_ = 3.9999*X_*(1-X_)
			X__.append(math.floor(X_*Size[0]))
			X_ = 3.9999*X_*(1-X_)
			X__.append(math.floor(X_*Size[1]))
			tmp = M[i][j]
			M[i][j] = M[X__[0]][X__[1]]
			M[X__[0]][X__[1]] = tmp;
	return M;

def Huffman(liczba):
	"""
	Funkcja Huffman

	Opis:
		Kodowanie huffmana z prawdopodobieństwami obliczonymi dla DCT JPG

	Argumenty:
		int liczba	liczba do zakodowania

	Printy:
		brak

	Return:
		str		zakodowana liczba w postaci binarnej

	Todo:
		brak

	Użyte funkcje:
		abs
		format
	"""
	try:
		absLiczba = abs(liczba);
	
		if liczba/absLiczba < 0:
			znak = '1'
		else:
			znak = '0'
	except:
		znak = '0'
	if liczba == 0:
		return '00'
	elif absLiczba <= 1:
		return '010%s%s' %(znak, format(1 - absLiczba, '01b'))
	elif absLiczba <= 3:
		return '011%s%s' %(znak, format(3 - absLiczba, '02b'))
	elif absLiczba <= 7:
		return '100%s%s' %(znak, format(7 - absLiczba, '03b'))
	elif absLiczba <= 15:
		return '101%s%s' %(znak, format(15 - absLiczba, '04b'))
	elif absLiczba <= 31:
		return '110%s%s' %(znak, format(31 - absLiczba, '05b'))
	elif absLiczba <= 63:
		return '1110%s%s' %(znak, format(63 - absLiczba, '06b'))
	elif absLiczba <= 127:
		return '11110%s%s' %(znak, format(127 - absLiczba, '07b'))
	elif absLiczba <= 255:
		return '111110%s%s' %(znak, format(255 - absLiczba, '08b'))
	elif absLiczba <= 511:
		return '1111110%s%s' %(znak, format(511 - absLiczba, '09b'))
	elif absLiczba <= 1023:
		return '11111110%s%s' %(znak, format(1023 - absLiczba, '010b'))
	elif absLiczba <= 2047:
		return '111111110%s%s' %(znak, format(2047 - absLiczba, '011b'))
	else:
		return false;

def md5Bloku(Blok):
	"""
	Funkcja md5Bloku

	Opis:
		Obliczenie md5 macierzy

	Argumenty:
		numpy.matrix Blok	macierz, której md5 obliczamy

	Printy:
		brak

	Return:
		str		md5 macierzy

	Todo:
		brak

	Użyte funkcje:
		numpy.array
		numpy.array.reshape
		hashlib.md5
		hashlib.md5.hexdigest
		format
		int
	"""
	Blok = numpy.array(Blok).reshape(-1)
	ret = hashlib.md5(Blok).hexdigest()
	ret = format(int(ret, 16), 'b')[0:16];
	return ret;

def zapiszWiadomosc(R, wiadomosc):
	"""
	Funkcja zapiszWiadomosc

	Opis:
		Funkcja zapisująca wiadomość na 2LSB macierzy

	Argumenty:
		numpy.matrix R			macierz, w której zapisujemy
		str          wiadomosc	wiadomosc, którą zapisujemy.
								wymagany format binarny

	Printy:
		brak

	Return:
		numpy.matrix	macierz z zapisaną wiadomością

	Todo:
		brak

	Użyte funkcje:
		numpy.matrix
		range
		len
		format
		int
	"""
	R = numpy.matrix(R)
	for i in range(R.shape[0]):
		for j in range(R.shape[1]):
			if (i*R.shape[1] + j)*2 >= len(wiadomosc):
				break;
			R[i,j] = int(format(R[i,j], '08b')[0:6] + wiadomosc[(i*R.shape[1] +j)*2 : (i*R.shape[1] +j)*2+2 ], 2)
	return R;

def sprawdzmd5Bloku(Blok):
	"""
	Funkcja sprawdzmd5Bloku

	Opis:
		Funkcja sprawdzająca, czy hash macierzy się zgadza. Hash jest 
		zapisany w macierzy

	Argumenty:
		numpy.matrix Blok	blok, którego poprawność chcemy sprawdzić

	Printy:
		brak

	Return:
		list[
			int	informacje o poprawności "1"-dobrze, "-1"-źle
			str	blok z wyczyszczonymi 2 LSB
			str	wiadomość zapisana na 2 LSB
			]

	Todo:
		brak

	Użyte funkcje:
		usun2LSB
		zapiszWiadomosc
		md5Bloku
	"""
	tmp = usun2LSB(Blok);
	Blok = zapiszWiadomosc(tmp[0], tmp[1][0:112] + '0'*16)
	if md5Bloku(Blok) == tmp[1][112: 128]:
		return [1, tmp[0], tmp[1]]
	else:
		return [-1, tmp[0], tmp[1]]

def binariaToDec(binary, ile, znak = 1):
	"""
	Funkcja binariaToDec

	Opis:
		Konwersja str do listy int'ów

	Argumenty:
		str binary	tekst do zdekodowania
		int ile[]	lista dwuwymiarowa zawierajaca informacje o pożadanych
					int'ach. Pierwszy wymiar oznacza liczbę, drugi wymiar 
					to lista dwuelementowa, gdzie pierwszy element oznacza
					ilość bitów, które konwertujemy, a drugi czy oczekujemy 
					znaku. Kolejność pierwszego wymiaru jest ważna
		int znak	deprecated

		Przykład:
			binariaToDec('11000101101101010011', [[10, 0], [10, 1]]

	Printy:
		brak

	Return:
		int[]	lista int'ów odczytanych z danego ciągu binarnego

	Todo:
		wywalić argument znak

	Użyte funkcje:
		range
		len
		list.append
	"""
	ret = []
	for i in range(len(ile)):
		if ile[i][1]:
			if binary[0:1] == '1':
				binary = '-' + binary[1:];
			else:
				binary = '+' + binary[1:];
		ret.append(int(binary[0:ile[i][0]], 2))
		binary = binary[ile[i][0]:]
	return ret

def intTobin(liczba, bity, znak=1):
	"""
	Funkcja intTobin

	Opis:
		Konwersja integera na postać binarną (str)
		Ograniczeniem jest długość liczby binarnej

	Argumenty:
		int     liczba	liczba do przekonwertowania
		int	    bity	długość liczby binarnej
		boolean znak	informacja czy rezerwować jeden bit na znak

	Printy:
		brak

	Return:
		str		integer w postaci binarnej

	Todo:
		brak

	Użyte funkcje:
		int
		abs
		str.replace
		format
	"""
	liczba = int(liczba)
	if(znak):
		if abs(liczba) > 2**(bity-1)-1:
			liczba /= abs(liczba)
			liczba *= 2**(bity-1)-1
		ret = format(int(liczba), '+0%ib' %bity)
		return ret.replace('+','0').replace('-', '1');
	else:
		if abs(liczba) > 2**(bity)-1:
			liczba /= abs(liczba)
			liczba *= 2**(bity)-1
		return format(int(liczba), '0%ib' %bity)

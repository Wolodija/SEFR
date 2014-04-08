#!/usr/bin/python3.2
from PIL import Image
import numpy
import math
import sys
import pickle
import time
def cli_progress_test(val, max_val, bar_length=50):
	percent = val/max_val;
	hashes = '#' * int(round(percent * bar_length))
	spaces = ' ' * (bar_length - len(hashes))
	sys.stdout.write("\rPostep: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100000))/1000))
	sys.stdout.flush()
#Funkcja usredniajaca czworki pikseli
def skaluj(D):
	D_ = []
	for i in range(int(D.shape[0]/2)):
		D_.append([])
		for j in range(int(D.shape[1]/2)):
			D_[i].append(D[2*i:2*(i+1),2*j:2*(j+1)].mean())
	return numpy.matrix(D_);

#Funkcja zwracajaca wszystkie rangeBlocki
def rangeBlocks(A, blockSize):
	R = [];
	for i in range(int(A.shape[0]/blockSize)):
		R.append([])
		for j in range(int(A.shape[1]/blockSize)):
			R[i].append(A[blockSize*i:blockSize*(i+1),blockSize*j:blockSize*(j+1)])
	return R;

#Funkcja zwracajaca wszystkie domainBlocki
def domainBlocks(A, blockSize, delta):
	D = [];
	for i in range(int((A.shape[0]-2*blockSize)/delta)+1):
		D.append([])
		for j in range(int((A.shape[1]-2*blockSize)/delta)+1):
			D[i].append(skaluj(A[delta*i:delta*i+2*blockSize,delta*j:delta*j+2*blockSize]))
	return D;

#Funkcja porownojaca rangeBlock i DomainBlock
def porownaj(R,D):
	R_ = R.mean();
	D_ = D.mean();
	s = (numpy.array(R-R_)*numpy.array(D-D_)).sum() / (numpy.array(D-D_)*numpy.array(D-D_)).sum()
	o = R_ - s*D_;
	E = numpy.linalg.norm(R*(s*D+o))
	return [s, o, E]

def przeksztalcenie(R, typ):
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
	print("pusto")


im= Image.open('lena.pgm'); 				#Odczytanie obrazu
A = numpy.matrix(im.getdata()).reshape(im.size)		#Konwersja do macierzy o rozmiarze obrazu
blockSize = int(sys.argv[1]);
delta = int(sys.argv[2]);
print("Tworzenie rangeBloków");
R = rangeBlocks(A, blockSize);
print("Tworzenie domainBloków");
D = domainBlocks(A, blockSize, delta);
print("Kompresja obrazka")

stat = []						#Tutaj ida wspolczynnniki kompresji
for i in range(len(R)):
	stat.append([]);
	#print(i)
	for j in range(len(R[i])):
		cli_progress_test(i*len(R)+j, len(R)*len(R));
		stat[i].append([[-1, -1], [-1, -1, -1]])#Wartosc poczatkowa spolczynnikow
		for a in range(len(D)):
			for b in range(len(D)):
				D_tmp = D[a][b]
				for c in range(8):
					tmp = porownaj(R[i][j], przeksztalcenie(D[a][b], c))
					if(stat[i][j][1][2] == -1 or stat[i][j][1][2] > tmp[2]):#jesli nie ustawiona lub mniejszy blad, to podmien wspolczynnniki
						tmp.append(c)
						stat[i][j] = [[a,b], tmp];
cli_progress_test(1, 1);
print("\nDekopmresja obrazka");

G = numpy.zeros(shape=im.size)+127	#Obraz poczatkowy dekompresji
for a in range(2):			#minimalna liczba petli to 2, wiecej niewiele zmienia
	for i in range(int(G.shape[0]/blockSize)):
		for j in range(int(G.shape[0]/blockSize)):
			G[blockSize*i:blockSize*(i+1),blockSize*j:blockSize*(j+1)] = przeksztalcenie(skaluj(G[delta*stat[i][j][0][0]:delta*stat[i][j][0][0] + 2*blockSize, delta*stat[i][j][0][1]:delta*stat[i][j][0][1]+2*blockSize]), stat[i][j][1][3])*stat[i][j][1][0] + stat[i][j][1][1] #Ta linijka jest troszke nieczytelna :D
print("Wyswietlenie obrazka")
#print(G)
Image.fromarray(numpy.uint8(numpy.matrix(G))).show()	#Wyswietlanie obrazka, nie wiem jak dziala na windowsie
#print(A.shape)
#im = Image.new('L', [16, 16], 0)
#A = [[255,255,255],[255,255,255], [255,255,255]]
#im = Image.fromarray(numpy.uint8(numpy.matrix(A)))
#im.show()

f = open('%i_%i_%i.pydump' %(time.time(), blockSize, delta), 'wb');
pickle.dump(stat, f);
f.close();

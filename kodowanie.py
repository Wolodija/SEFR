#!/usr/bin/python3.2

print("Trwa importowanie bibliotek");
from Funkcje import *;

print("Biblioteki zaimportowano");

im= Image.open('lena.pgm'); 									#Odczytanie obrazu
A = usun2LSB(numpy.matrix(im.getdata()).reshape(im.size))[0]	#Zamiana obrazu na macierz, zerujac 2 najmniej znaczace bity
Image.fromarray(numpy.uint8(numpy.matrix(A))).show()			#Wyswietlanie obrazka, nie wiem jak dziala na windowsie

blockSize = 8;													#Rozmiar BlockSize
delta = 128;														#Wartosc Delty
print("Tworzenie rangeBloków");
R = rangeBlocks(A, blockSize);									#Tworzenie rangeBlokow
print("Tworzenie domainBloków");	
		
D = domainBlocks(A, blockSize, delta);							#Tworzenie Domain Blokow
print("Kompresja obrazka")

#range(int((A.shape[0]-2*blockSize)/delta)+1)
stat = Kompresuj(R, D, delta);
"""stat = [[[[-1, -1], [-1, -1, -1]]] * len(R) for i in range(len(R))]
for counter in range(4):
	if(counter == 0):
		ranges = [range(0, int(len(R)/2)), range(0, int(len(R)/2)), range(int(len(D)/2), len(D)), range(int(len(D)/2), len(D)), -int(len(D)/2), -int(len(D)/2)]
	elif(counter == 1):
		ranges = [range(int(len(R)/2), len(R)), range(int(len(R)/2), len(R)), range(0, int(len(D)/2)), range(0, int(len(D)/2)), 0, 0]
	elif(counter == 2):
		ranges = [range(0, int(len(R)/2)), range(int(len(R)/2), len(R)), range(int(len(D)/2), len(D)), range(0, int(len(D)/2)), -int(len(D)/2), 0]
	elif(counter == 3):
		ranges = [range(int(len(R)/2), len(R)), range(0, int(len(R)/2)), range(0, int(len(D)/2)), range(int(len(D)/2), len(D)), 0, -int(len(D)/2)]
	for i in ranges[0]:
		for j in ranges[1]:
			cli_progress_test(i*len(R)+j + int(counter/2)*len(R)*len(R), 2*len(R)*len(R));
			for a in ranges[2]:
				for b in ranges[3]:
					D_tmp = D[a][b]
					for c in range(8):
						tmp = porownaj(R[i][j], przeksztalcenie(D[a][b], c))
						if(stat[i][j][1][2] == -1 or stat[i][j][1][2] > tmp[2]):#jesli nie ustawiona lub mniejszy blad, to podmien wspolczynnniki
							tmp.append(c)
							stat[i][j] = [[(a+ranges[4])*delta,(b+ranges[5])*delta], tmp];
cli_progress_test(1, 1);"""

print("Tworzenie dodatkowych rangeBloków")
B = rangeBlocks(przesunGora(A), 8);
B_wsp = kodujDCTJPEG(B);

C = rangeBlocks(przesunLewo(A), 8);
C_wsp = kodujDCTJPEG(C);
Maper = [124, 112, 18, 199, 255, 10, 123, 32, 96, 111]
#Tablice mapowania 4 wpisy w każdym wpis [i][j] w którym są współrzędne punktu na który mapujemy
A_map = [getMapping(Maper, int(len(R)/2)), getMapping(Maper, int(len(R)/2)), getMapping(Maper, int(len(R)/2)), getMapping(Maper, int(len(R)/2))]
B_map = [getMapping(Maper, int(len(B)/2)), getMapping(Maper, int(len(B)/2)), getMapping(Maper, int(len(B)/2)), getMapping(Maper, int(len(B)/2))]
C_map = [getMapping(Maper, int(len(C)/2)), getMapping(Maper, int(len(C)/2)), getMapping(Maper, int(len(C)/2)), getMapping(Maper, int(len(C)/2))]

wsp = [[None] * len(R) for i in range(len(R))]

#print("Dekompresja obrazka");
#G = Dekompresuj(im.size, stat);
print("Wyswietlenie obrazka")
binwsp=[]
binary = []
#Zamiana współczynników kodowania fraktalnego na binaria
for i in range(len(stat)):
	binwsp.append([])
	binary.append([])
	for j in range(len(stat)):
		binwsp[i].append('')
		binary[i].append(None)
		binwsp[i][j] += (format(stat[i][j][0][0], '0%ib' %(7)))
		binwsp[i][j] += (format(stat[i][j][0][1], '0%ib' %(7)))
		binwsp[i][j] += (format(int(((stat[i][j][1][0]) + 16)*4), '07b'))
		binwsp[i][j] += (format(int(((stat[i][j][1][1]) + 2048)/32), '08b'))
		binwsp[i][j] += (format(stat[i][j][1][3], '03b'))
		if(len(binwsp[i][j]) > 32):
			print("Za duzo bitow dla kodowania fraktalnego")
			print(stat[i][j]);
			sys.exit();

#Najgorsza część, ustalenie co w którym bloku będzie zapisane
for counter in range(0, 4):
	#Ranges, to będą współczynniki przydatne prz pętlach
	if counter == 0:
		ranges = [[0, 0], [3,2,1]]
	elif counter == 1:
		ranges = [[int(len(stat)/2), 0], [2, 3, 0]]
	elif counter == 2:
		ranges = [[0, int(len(stat)/2)], [1, 0, 3]]
	elif counter == 3:
		ranges = [[int(len(stat)/2), int(len(stat)/2)], [0, 1, 2]]
	#Mapowanie współczynników
	for i in range(int(len(stat)/2)):
		for j in range(int(len(stat)/2)):
			x = A_map[ranges[1][0]][i][j][0] + ranges[0][0]
			y = A_map[ranges[1][0]][i][j][1] + ranges[0][1]
			binary[x][y] = binwsp[i + ranges[0][0]][j + ranges[0][1]]
			if(len(binary[x][y])) > 32:
				print("a");
				sys.exit()

	#Mapowanie bloków B
	for i in range(int(len(stat)/2)):
		for j in range(int(len(stat)/2)):
			x = B_map[ranges[1][1]][i][j][0] + ranges[0][0]
			y = B_map[ranges[1][1]][i][j][1] + ranges[0][1]
			if binary[x][y] == None:
				print("Cos sie zjebalo");
				print([x, y])
				print([i, j])
				sys.exit();
			binary[x][y] += B_wsp[i + ranges[0][0]][j + ranges[0][1]]
			if(len(binary[x][y])) > 72:
				print("b");
				sys.exit()


	#Mapowanie bloków C
	for i in range(int(len(stat)/2)):
		for j in range(int(len(stat)/2)):
			x = C_map[ranges[1][2]][i][j][0] + ranges[0][0]
			y = C_map[ranges[1][2]][i][j][1] + ranges[0][1]
			binary[x][y] += C_wsp[i + ranges[0][0]][j + ranges[0][1]]
			if(len(binary[x][y])) > 112:
				print("c");
				sys.exit()

print("Zapisywanie danych w obrazku :)")
for i in range(len(binary)):
	for j in range(len(binary)):
		R[i][j] = zapiszWiadomosc(R[i][j], binary[i][j])
		R[i][j] = zapiszWiadomosc(R[i][j], binary[i][j] + md5Bloku(R[i][j]))

"""
for i in range(len(stat)):
	for j in range(len(stat)):
		stat[i][j][0][0] = int(binary[i][j][0:7], 2);
		stat[i][j][0][1] = int(binary[i][j][7:14], 2);
		stat[i][j][1][0] = int(binary[i][j][14:21], 2)/8 - 8;
		stat[i][j][1][1] = int(binary[i][j][21:29], 2)*8 - 1024;
		stat[i][j][1][3] = int(binary[i][j][29:32], 2);
"""
A_map = [getMapping(Maper, int(len(R)/2)), getMapping(Maper, int(len(R)/2)), getMapping(Maper, int(len(R)/2)), getMapping(Maper, int(len(R)/2))]
B_map = [getMapping(Maper, int(len(B)/2)), getMapping(Maper, int(len(B)/2)), getMapping(Maper, int(len(B)/2)), getMapping(Maper, int(len(B)/2))]
C_map = [getMapping(Maper, int(len(C)/2)), getMapping(Maper, int(len(C)/2)), getMapping(Maper, int(len(C)/2)), getMapping(Maper, int(len(C)/2))]

H = numpy.matrix(im.getdata()).reshape(im.size)
for i in range(len(R)):
	for j in range(len(R)):
		H[blockSize*i:blockSize*(i+1),blockSize*j:blockSize*(j+1)] = R[i][j]
#G = Dekompresuj(im.size, stat);
#print(G)
H = Image.fromarray(numpy.uint8(numpy.matrix(H)))	#Wyswietlanie obrazka, nie wiem jak dziala na windowsie
H.show()
H.save("lenaWatermarked.pgm")
#print(A.shape)
#im = Image.new('L', [16, 16], 0)
#A = [[255,255,255],[255,255,255], [255,255,255]]
#im = Image.fromarray(numpy.uint8(numpy.matrix(A)))
#im.show()

#f = open('%i_%i_%i.pydump' %(time.time(), blockSize, delta), 'wb');
#pickle.dump(stat, f);
#f.close();



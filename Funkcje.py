from PIL import Image
import numpy
import math
import sys
import pickle
import time
import hashlib;

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
	s = int((s + 16)*4)/4 - 16
	o = R_ - s*D_;
	o = int((o + 2048)/16) * 16 - 2048
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

#Funkcja przesuwajaca obraz o n px w gore
def przesunGora(A, n = 4):
	A = numpy.matrix(A)
	B = numpy.matrix(A[0:n,:]);
	A[0:len(A)-n, :] = A[n:len(A), :]
	A[len(A)-n:, :] = B;
	return A;
	
#Funkcja przesuwajaca obraz o n px w lewo
def przesunLewo(A, n = 4):
	A = numpy.matrix(A)
	B = numpy.matrix(A[:,0:n]);
	A[:, 0:len(A)-n] = A[:,n:len(A)]
	A[:,len(A)-n:] = B;
	return A;
	
def usun2LSB(R):
	R = numpy.matrix(R)
	wiadomosc = '';
	for i in range(R.shape[0]):
		for j in range(R.shape[1]):
			binary = format(R[i,j], '08b')
			R[i,j] = int("%s00" %(binary[0:6]), 2)
			wiadomosc += binary[6:8];
	return [R, wiadomosc]

def Kompresuj(R, D, delta):
	stat = [[[[-1, -1], [-1, -1, -1]]] * len(R) for i in range(len(R))]
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
	cli_progress_test(1, 1);
	print("");
	return stat;

def Dekompresuj(size, stat):
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
					G[blockSize*i:blockSize*(i+1),blockSize*j:blockSize*(j+1)] = przeksztalcenie(skaluj(G[stat[i][j][0][0]+ranges[2]:stat[i][j][0][0]+ranges[2] + 2*blockSize, stat[i][j][0][1]+ranges[3]:stat[i][j][0][1]+ranges[3]+2*blockSize]), stat[i][j][1][3])*stat[i][j][1][0] + stat[i][j][1][1] #Ta linijka jest troszke nieczytelna :D
	cli_progress_test(1, 1);
	print("");
	return(G);

def getWspDCT(M):
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


def kodujWspDCT(wsp):
	ret = '';
	"""
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
	return ret;"""
	ret = Huffman(wsp[0])
	for i in range(1, len(wsp)):
		ret += Huffman(wsp[i] - wsp[i-1])
		#ret += Huffman(wsp[i])
	ret += '0000000000000000000000000000'
	return ret[0:40];
	
def kodujDCTJPEG(R):
	wsp = [[None] * len(R) for i in range(len(R))]
	for i in range(len(R)):
		for j in range(len(R)):
			cli_progress_test(i*len(R) + j, len(R)*len(R));
			wsp[i][j] = kodujWspDCT(getWspDCT(R[i][j]));
	cli_progress_test(1, 1);
	print("");
	return wsp;

def getMapping(R, Size, password = None):
	if(password):
		K=password[0:10];
	else:
		R = numpy.array(R).reshape(-1)
		K = R[0:10];
	B1 = K[4:7];
	M=[];

	for i in range(Size):
		M.append([])
		for j in range(Size):
			M[i].append([i,j]);
	X = ''.join([format(znak, '08b') for znak in B1 ])

	X_01 = sum([int(X[i])*math.pow(2, i) for i in range(len(X))])/pow(2, 24)
	Z = ''.join([format(znak, '02x') for znak in K ])
	X_02 = sum([int(Z[i], 16) for i in range(12, 18)])/96

	X_ = (X_01 + X_02) % 1
	X=[]

	for i in range(0, Size):
		for j in range(0, Size):
			X__=[]
			X_ = 3.9999*X_*(1-X_)
			X__.append(math.floor(X_*Size))
			X_ = 3.9999*X_*(1-X_)
			X__.append(math.floor(X_*Size))
			tmp = M[i][j]
			M[i][j] = M[X__[0]][X__[1]]
			M[X__[0]][X__[1]] = tmp;
	return M;

def Huffman(liczba):
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
	Blok = numpy.array(Blok).reshape(-1)
	ret = hashlib.md5(Blok).hexdigest()
	ret = format(int(ret, 16), 'b')[0:16];
	return ret;

def zapiszWiadomosc(R, wiadomosc):
	R = numpy.matrix(R)
	for i in range(R.shape[0]):
		for j in range(R.shape[1]):
			if (i*R.shape[1] + j)*2 >= len(wiadomosc):
				break;
			R[i,j] = int(format(R[i,j], '08b')[0:6] + wiadomosc[(i*R.shape[1] +j)*2 : (i*R.shape[1] +j)*2+2 ], 2)
	return R;

def sprawdzmd5Bloku(Blok):
	tmp = usun2LSB(Blok);
	Blok = zapiszWiadomosc(tmp[0], tmp[1][0:112] + '0'*16)
	if md5Bloku(Blok) == tmp[1][112: 128]:
		return 1
	else:
		return 0

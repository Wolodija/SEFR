"""
gui.py
"""

from PyQt4 import QtGui, QtCore
from Funkcje import *;

class SEFR_GUI(QtGui.QMainWindow):
	"""
	Klasa do obsługi aplikacji graficznej
	"""
	def __init__(self):
		"""
		Konstruktor
		"""
		super(SEFR_GUI, self).__init__()
		self.getConfig()
		self.initUI()
		if(len(sys.argv) >= 3 and sys.argv[3] == 'znak'):
			self.plikOtworz = sys.argv[1]
			self.plikZapisz = sys.argv[2]
			self.dodajZnakWodny()
			sys.exit()
		elif(len(sys.argv) >= 3 and sys.argv[3] == 'recover'):
			self.plikOtworz = sys.argv[1]
			self.plikZapisz = sys.argv[2]
			self.check()
			sys.exit()
		
	def initUI(self):
		"""
		Inicjalizator
		"""
		#Menubar - wyjście z aplikacji
		exitAction = QtGui.QAction(QtGui.QIcon('exit-icon.png'), '&Wyjście', self)        
		exitAction.setShortcut('Ctrl+Q')
		exitAction.setStatusTip('Wyjście')
		exitAction.triggered.connect(self.zamykamy)
		
		#Menubar - otwarcie pliku
		openAction = QtGui.QAction(QtGui.QIcon('open-icon.png'), '&Otwórz plik...', self)        
		openAction.setShortcut('Ctrl+O')
		openAction.setStatusTip('Otwórz')
		openAction.triggered.connect(self.openDialog)
		
		#Menubar - zapisanie pliku
		saveAction = QtGui.QAction(QtGui.QIcon('save-icon.png'), '&Zapisz plik...', self)        
		saveAction.setShortcut('Ctrl+S')
		saveAction.setStatusTip('Zapisz')
		saveAction.triggered.connect(self.saveDialog)
		
		#Menubar - Konfiguracja
		confAction = QtGui.QAction(QtGui.QIcon('conf-icon.png'), '&Ustawienia', self)        
		confAction.setShortcut('Ctrl+U')
		confAction.setStatusTip('Ustawienia')
		confAction.triggered.connect(self.confDialog)
		
		#Menubar - Watermark
		waterAction = QtGui.QAction(QtGui.QIcon('watermark-icon.png'), '&Dodaj znak wodny', self)        
		waterAction.setShortcut('Ctrl+D')
		waterAction.setStatusTip('Znak wodny')
		waterAction.triggered.connect(self.dodajZnakWodny)
		
		#Menubar - Watermark checking
		checkAction = QtGui.QAction(QtGui.QIcon('check-icon.png'), 'S&prawdź znak wodny', self)        
		checkAction.setShortcut('Ctrl+P')
		checkAction.setStatusTip('Znak wodny')
		checkAction.triggered.connect(self.check)
		
		#Pomoc - Konfiguracja
		helpAction = QtGui.QAction(QtGui.QIcon(''), 'Po&moc', self)        
		helpAction.setShortcut('Ctrl+M')
		helpAction.setStatusTip('Ustawienia')
		helpAction.triggered.connect(self.helpDialog)
		
		#Menubar
		menubar = self.menuBar()
		
		#Menubar - plik
		fileMenu = menubar.addMenu('&Plik')
		fileMenu.addAction(openAction)
		fileMenu.addAction(saveAction)
		fileMenu.addAction(exitAction)
		
		#Menubar - pomoc
		actionMenu = menubar.addMenu('&Akcja')  
		actionMenu.addAction(waterAction)
		actionMenu.addAction(checkAction)
		actionMenu.addAction(confAction)
		
		#Menubar - pomoc
		helpMenu = menubar.addMenu('P&omoc') 
		helpMenu.addAction(helpAction) 
		
		#Toolbar
		toolbar = self.addToolBar('Toolbar')
		
		#Toolbar - dodanie akcji
		toolbar.addAction(openAction)
		toolbar.addAction(saveAction)
		toolbar.addAction(waterAction)
		toolbar.addAction(checkAction)
		toolbar.addAction(confAction)
		toolbar.addAction(exitAction)
		
		#Progress bar
		self.postep = QtGui.QProgressBar(self);
		self.postep.setMinimum(0)
		self.postep.setMaximum(100)
		self.postep.show()
		self.postep.move(50, 250)
		self.postep.resize(400, 20);
		self.postep.hide();
		
		#Label 1
		label1 = QtGui.QLabel('Witaj w aplikacji do tworzenie i dodawania\n\
znaków wodnych do obrazka,\n\
a także weryfikowania ich poprawności \n\
i ew. odzyskiwania danych ze znaku wodnego\n\n\
1. Wybierz co chcesz zrobić\n\
2. Wskaż plik do przetworzenia,\n\
    a następnie po zakończonej operacji, miejsce przeznaczenia', self);
		label1.move(20, 80)
		label1.adjustSize()
		
		#labelInfo
		self.labelInfo = QtGui.QLabel('', self);
		self.labelInfo.move(50, 230);
		self.labelInfo.adjustSize();
		self.labelInfo.hide();
		
		#Geometria okna
		self.setGeometry(300, 300, 500, 300)
		self.setWindowTitle('SEFR - Self Embedding Fractal Recovery')
		self.setWindowIcon(QtGui.QIcon('icon.png'))  
		
		#Wyświetlenie wszystkiego
		self.show()
		self.statusBar().showMessage('Gotowe')
		
	#Pobranie nazwy pliku do zapisu
	def saveDialog(self):
		"""
		Pobierz plik do zapisu
		"""
		
		self.plikZapisz = QtGui.QFileDialog.getSaveFileName(self, 'Zapisz plik', 
				'.', 'Obrazy(PGM) (*.pgm)')
#		print(self.plikZapisz)
				
	#Pobranie nazwy pliku do odczytu  
	def openDialog(self):
		"""
		Pobierz plik do odczytu
		"""
		self.plikOtworz = QtGui.QFileDialog.getOpenFileName(self, 'Otwórz plik', 
				'lena.pgm', 'Obrazy(PGM) (*.pgm)')
				
	def confDialog(self):
		"""
		Okno konfiguracyjne
		"""
		conf = QtGui.QMainWindow(self)
		self.conf2 = QtGui.QWidget(conf)
		
		#ComboBox:wybór konfiguracji
		comboBox = QtGui.QComboBox(self)
		for i in range(len(self.config["profile"])):
			comboBox.insertItem(i, self.config["profile"][i]["nazwa"])
		comboBox.currentIndexChanged.connect(self.zmienConfig)
		
		
		#labele
		fraktalLbls={"podpis" : QtGui.QLabel('Kodowanie fraktalne'),
					"x" : QtGui.QLabel('Szerokość'), 
					"y" : QtGui.QLabel('Wysokość'), 
					"s" : QtGui.QLabel('Scale'), 
					"o" : QtGui.QLabel('Luminance offset'), 
					"p" : QtGui.QLabel('Przekształcenie')}
		dctLbl = QtGui.QLabel("Długość DCT");
		hashLbl = QtGui.QLabel("Długość hasha");
		passLbl = QtGui.QLabel("Hasło");
		
		#Slidery
		try:
			self.fraktalSldrs
			self.fraktalSpnbs
			self.fraktalSuma
			self.fraktalPrzk
		except:
			self.fraktalSldrs = {"x" : QtGui.QSlider(QtCore.Qt.Horizontal, self),
								"y" : QtGui.QSlider(QtCore.Qt.Horizontal, self),
								"s" : QtGui.QSlider(QtCore.Qt.Horizontal, self),
								"o" : QtGui.QSlider(QtCore.Qt.Horizontal, self)#,
								#"p" : QtGui.QSlider(QtCore.Qt.Horizontal, self)
								}
								
			self.fraktalSpnbs = {"x" : QtGui.QSpinBox(self),
								"y" : QtGui.QSpinBox(self),
								"s" : QtGui.QSpinBox(self),
								"o" : QtGui.QSpinBox(self)#,
								#"p" : QtGui.QSpinBox(self)
								}
			
			self.fraktalSuma = QtGui.QLineEdit('0', self)
			self.fraktalSuma.setDisabled(1)
			self.fraktalPrzk = QtGui.QLineEdit('3', self)
			self.fraktalPrzk.setDisabled(1)
			self.haslo = QtGui.QLineEdit('Domyslne haslo', self)
			self.haslo.textChanged.connect(self.hasloZmienione)
			
			for sldr in self.fraktalSldrs:
				self.fraktalSldrs[sldr].setFocusPolicy(QtCore.Qt.NoFocus)
				self.fraktalSldrs[sldr].setTickInterval(1)
				self.fraktalSldrs[sldr].setMinimum(1)
				self.fraktalSldrs[sldr].setMaximum(20)
				self.fraktalSldrs[sldr].setSingleStep(1)
				self.fraktalSldrs[sldr].setValue(3)
				self.fraktalSldrs[sldr].setGeometry(30, 40, 100, 30)
				self.fraktalSldrs[sldr].valueChanged.connect(partial(self.fractalChanged, self.fraktalSldrs[sldr], sldr))
			sldr = None
				
			for spnb in self.fraktalSpnbs:
				self.fraktalSpnbs[spnb].setMinimum(1)
				self.fraktalSpnbs[spnb].setMaximum(20)
				self.fraktalSpnbs[spnb].setSingleStep(1)
				self.fraktalSpnbs[spnb].setValue(3)
				self.fraktalSpnbs[spnb].valueChanged.connect(partial(self.fractalChanged, self.fraktalSpnbs[spnb], spnb))
			spnb = None
			
		
		#siatka
		grid = QtGui.QGridLayout(self.conf2)
		grid.setSpacing(10)
		
		grid.addWidget(comboBox, 1,0);
		
		grid.addWidget(passLbl, 3,0)
		grid.addWidget(self.haslo, 3,1)
		
		grid.addWidget(fraktalLbls["podpis"], 4,0)
		grid.addWidget(self.fraktalSuma, 4,1)
		grid.addWidget(fraktalLbls["x"], 5,0)
		grid.addWidget(self.fraktalSldrs["x"], 5,1)
		grid.addWidget(self.fraktalSpnbs["x"], 5,2)
		grid.addWidget(fraktalLbls["y"], 6,0)
		grid.addWidget(self.fraktalSldrs["y"], 6,1)
		grid.addWidget(self.fraktalSpnbs["y"], 6,2)
		grid.addWidget(fraktalLbls["s"], 7,0)
		grid.addWidget(self.fraktalSldrs["s"], 7,1)
		grid.addWidget(self.fraktalSpnbs["s"], 7,2)
		grid.addWidget(fraktalLbls["o"], 8,0)
		grid.addWidget(self.fraktalSldrs["o"], 8,1)
		grid.addWidget(self.fraktalSpnbs["o"], 8,2)
		grid.addWidget(fraktalLbls["p"], 9,0)
		grid.addWidget(self.fraktalPrzk, 9,1)
		
		#Slidery
		try:
			self.dctSldr
			self.dctSpnb
			self.hashSldr
			self.hashSpnb
		except:
			self.dctSldr = QtGui.QSlider(QtCore.Qt.Horizontal, self);
			self.hashSldr = QtGui.QSlider(QtCore.Qt.Horizontal, self);
								
			self.dctSpnb = QtGui.QSpinBox(self);
			self.hashSpnb = QtGui.QSpinBox(self);
								
			self.dctSldr.setFocusPolicy(QtCore.Qt.NoFocus)
			self.dctSldr.setTickInterval(1)
			self.dctSldr.setMinimum(1)
			self.dctSldr.setMaximum(50)
			self.dctSldr.setSingleStep(1)
			self.dctSldr.setValue(3)
			self.dctSldr.setGeometry(30, 40, 100, 30)
			self.dctSldr.valueChanged.connect(self.dctChanged)
								
			self.hashSldr.setFocusPolicy(QtCore.Qt.NoFocus)
			self.hashSldr.setTickInterval(1)
			self.hashSldr.setMinimum(1)
			self.hashSldr.setMaximum(50)
			self.hashSldr.setSingleStep(1)
			self.hashSldr.setValue(3)
			self.hashSldr.setGeometry(30, 40, 100, 30)
			self.hashSldr.valueChanged.connect(self.hashChanged)
			
			self.dctSpnb.setMinimum(1)
			self.dctSpnb.setMaximum(50)
			self.dctSpnb.setSingleStep(1)
			self.dctSpnb.setValue(3)
			self.dctSpnb.valueChanged.connect(self.dctChanged)
			
			self.hashSpnb.setMinimum(1)
			self.hashSpnb.setMaximum(50)
			self.hashSpnb.setSingleStep(1)
			self.hashSpnb.setValue(3)
			self.hashSpnb.valueChanged.connect(self.hashChanged)
			
		grid.addWidget(dctLbl, 10,0)
		grid.addWidget(self.dctSldr, 10,1)
		grid.addWidget(self.dctSpnb, 10,2)
		grid.addWidget(hashLbl, 11,0)
		self.hashSldr.setDisabled(1)
		self.hashSpnb.setDisabled(1)
		grid.addWidget(self.hashSldr, 11,1)
		grid.addWidget(self.hashSpnb, 11,2)
		
		
		self.bitSumPodpis = QtGui.QLabel('Suma bitów');
		self.bitSum = QtGui.QLineEdit('%i' %(self.przeliczBity()), self)
		self.bitSum.setDisabled(1)
		
		self.infolab = QtGui.QLabel('');
		
		grid.addWidget(self.bitSumPodpis, 12,0)
		grid.addWidget(self.bitSum, 12,1)
		grid.addWidget(self.infolab, 13,1)
		
		self.zmienConfig(0)
		self.conf2.resize(400, 400)
		
		conf.resize(400, 400)
		conf.move(300, 300)
		conf.setWindowTitle('Ustawienia')
		conf.show()

	def helpDialog(self):
		"""
		Okno konfiguracyjne
		"""
		pomoc = QtGui.QMainWindow(self)
		self.pomoc = QtGui.QWidget(pomoc)
		label = QtGui.QLabel('SEFR - Self-embedding fragile watermarking\nbased on DCT and fast fractal coding\n\
Aplikacja ma posłużyć do dodawania znaków wodnych \ndo obrazów (jak na razie tylko PGM)\n\
oraz odzyskiwania pierwotnej ich formy\npo jakimkolwiek uszkodzeniu\n\n\
Autorzy: Dominik Rosiek i Piotr Ścibor');
		
		#siatka
		grid = QtGui.QGridLayout(self.pomoc)
		grid.setSpacing(10)
		
		grid.addWidget(label, 1,0);
		self.pomoc.resize(360, 200)
		
		pomoc.resize(360, 200)
		pomoc.move(300, 300)
		pomoc.setWindowTitle('Pomoc')
		pomoc.show()

	def getConfig(self):
		"""
		Załaduj konfiguracje z pliku
		"""
		try:
			self.config = pickle.load(open("config.cfg", "rb"))
			dalej = 1
		except:
			dalej = 0;
		
		if not dalej:
			config = {"profile":[{"nazwa":"default", "bity":{
				"fraktal":{"suma": 32,
							"x":7,
							"y":7,
							"s":7,
							"o":8},
				"DCT1":40,
				"DCT2":40,
				"hash":16,},
				"haslo" : "Domysle haslo"}],
				"profil":0}
			pickle.dump(config, open("config.cfg", "wb"))
			self.getConfig()
			
	def zamykamy(self):
		"""
		Zamknij apke, zapisz konfiguracje
		"""
		pickle.dump(self.config, open("config.cfg", "wb"))
		QtGui.qApp.quit()
			
	def closeEvent(self, event):
		"""
		uchwyt do zamkniecia (takie kombinowanie)
		"""
		self.zamykamy()
		
	def fractalChanged(self, obiekt, name):
		"""
		zmien wspolczynnik fraktalny
		"""
		self.fraktalSldrs[name].setValue(obiekt.value())
		self.fraktalSpnbs[name].setValue(obiekt.value())
		self.config["profile"][self.config["profil"]]["bity"]["fraktal"][name] = self.fraktalSpnbs[name].value()
		self.fractalPrzelicz()
		
	def dctChanged(self, value):
		"""
		zmien wspolczynnik dct
		"""
		self.config["profile"][self.config["profil"]]["bity"]["DCT1"] = value
		self.config["profile"][self.config["profil"]]["bity"]["DCT2"] = value
		self.dctSldr.setValue(value)
		self.dctSpnb.setValue(value)
		self.bitSum.setText(str(self.przeliczBity()))
		
	def hashChanged(self, value):
		"""
		zmien wartosc hasha
		"""
		self.config["profile"][self.config["profil"]]["bity"]["hash"] = value
		self.hashSldr.setValue(value)
		self.hashSpnb.setValue(value)
		self.bitSum.setText(str(self.przeliczBity()))
		
	def hasloZmienione(self, value):
		"""
		zmien wartosc hasha
		"""
		self.config["profile"][self.config["profil"]]["haslo"] = value
		
	def fractalPrzelicz(self):
		"""
		przelicz sume bitow na kodowanie fraktalne
		"""
		self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] = 3 						\
							+ self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["x"]	\
							+ self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["y"]	\
							+ self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["s"]	\
							+ self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["o"]
		tmp = int(self.fraktalPrzk.text())
		for spnb in self.fraktalSpnbs:
			tmp += self.fraktalSpnbs[spnb].value()
		self.fraktalSuma.setText(str(tmp))
		self.bitSum.setText(str(self.przeliczBity()))
		
	def zmienConfig(self, identyfikator):
		"""
		zmien konfiguracje
		"""
		self.config["profil"] = identyfikator;
		for spnb in self.fraktalSpnbs:
			self.fraktalSpnbs[spnb].setValue(self.config["profile"][identyfikator]["bity"]["fraktal"][spnb])
			self.fraktalSldrs[spnb].setValue(self.config["profile"][identyfikator]["bity"]["fraktal"][spnb])
		self.dctSldr.setValue(self.config["profile"][identyfikator]["bity"]["DCT1"])
		self.hashSldr.setValue(self.config["profile"][identyfikator]["bity"]["hash"])
		self.dctSpnb.setValue(self.config["profile"][identyfikator]["bity"]["DCT1"])
		self.hashSpnb.setValue(self.config["profile"][identyfikator]["bity"]["hash"])
		self.haslo.setText(self.config["profile"][identyfikator]["haslo"])
		self.bitSum.setText(str(self.przeliczBity()))
	
	def print_(self, tekst):
		"""
		print (konsola + gui)
		"""
		#print(tekst)
		self.labelInfo.setText(tekst)
		self.labelInfo.adjustSize()
		self.labelInfo.show()
		
	def progress(self, val, max_val, bar_length=50):
		"""
		pasek ladowania (konsola + gui)
		"""
		#return 0;
		percent = val/max_val;
		hashes = '#' * int(round(percent * bar_length))
		spaces = ' ' * (bar_length - len(hashes))
		#sys.stdout.write("\rPostep: [{0}] {1}%     ".format(hashes + spaces, int(round(percent * 100000))/1000))
		#sys.stdout.flush()
		self.postep.setValue(percent*100);
		self.postep.show()
	
	def przeliczBity(self):
		"""
		Przelicz wszystkie bity
		"""
		try:
			if not (self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] 
				+ self.config["profile"][self.config["profil"]]["bity"]["DCT1"] 
				+ self.config["profile"][self.config["profil"]]["bity"]["DCT2"] 
				+ self.config["profile"][self.config["profil"]]["bity"]["hash"] == 128):
					self.infolab.setText("Suma bitów ma wynosić 128")
					self.infolab.adjustSize()
			else:
				self.infolab.setText("");
				self.infolab.adjustSize()
		except:
			None
		return self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] \
			+ self.config["profile"][self.config["profil"]]["bity"]["DCT1"] \
			+ self.config["profile"][self.config["profil"]]["bity"]["DCT2"] \
			+ self.config["profile"][self.config["profil"]]["bity"]["hash"];
	#Dodawanie znaku wodnego
	def dodajZnakWodny(self):
		"""
		dodawanie znaku wodnego
		TODO: Komentarze
		"""
		if self.przeliczBity() > 128:
			self.print_("Za dużo bitów. Obecnie: %i, wymagane 128 Zmień ustawienia" %(self.przeliczBity()));
			return -1;
		try:
			if self.plikOtworz == "":
				self.openDialog();
			nazwa = self.plikOtworz;
		except:
			self.openDialog();
			nazwa = self.plikOtworz;
			if nazwa == "":
				self.print_("Nie wybrano pliku");
				return -1;
		
		try:
			im = Image.open(nazwa); 	#Odczytanie obrazu
		except IOError:
			self.print_("Wygląda na to że plik nie jest obrazkiem")
			return -1
		if not (im.mode == 'L'):
			self.print_("Inne rodzaje obrazu niż skala szarości, nie są jeszcze obsługiwane")
			return -1
		if im.size[0] % 8 or im.size[1] % 8:		
			self.print_("Obrazy o wymiarach niepodzielnych przez 8 nie są obsługiwane")
			return -1
		A = usun2LSB(numpy.matrix(im.getdata()).reshape((im.size[1], im.size[0])))[0]	#Zamiana obrazu na macierz, zerujac 2 najmniej znaczace bity
		#Image.fromarray(numpy.uint8(numpy.matrix(A))).show()			#Wyswietlanie obrazka, nie wiem jak dziala na windowsie

		blockSize = 8;
		self.print_("Kompresja obrazka o rozmiarze " + str(A.shape))

		#Wartosc Delty; Delta jest tak obliczona, żeby numer bloku zmieścił się na 7 bitach

		if(im.size[0] > im.size[1]):
			delta = int(im.size[0]/(2**self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["x"]));
		else:
			delta = int(im.size[1]/(2**self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["y"]));
		#delta = 200;
		self.print_("Delta: " + str(delta));
		self.print_("Tworzenie rangeBloków");
		R = numpy.array(rangeBlocks(A, blockSize));									#Tworzenie rangeBlokow
		self.print_("Tworzenie domainBloków w czterech ćwiartkach");	

		#Tworzenie domain blokow w czterech cwiartkach
		D = [domainBlocks(A[0:int(A.shape[0]/2), 0:int(A.shape[1]/2)], blockSize, delta, self),
					domainBlocks(A[int(A.shape[0]/2):, 0:int(A.shape[1]/2)], blockSize, delta, self),
					domainBlocks(A[0:int(A.shape[0]/2), int(A.shape[1]/2):], blockSize, delta, self),
					domainBlocks(A[int(A.shape[0]/2):, int(A.shape[1]/2):], blockSize, delta, self)]
		#D = domainBlocks(A, blockSize, delta);							#Tworzenie Domain Blokow
		self.print_("Kompresja obrazka")

		#range(int((A.shape[0]-2*blockSize)/delta)+1)

		stat = numpy.array([[[[-1, -1], [-1, -1, -1]]] * len(R[i]) for i in range(len(R))])
		self.print_("Pierwsza cwiartka")
		stat[0:int(len(R)/2), 0:int(len(R[0])/2)] = Kompresuj(R[0:int(len(R)/2), 0:int(len(R[0])/2)], D[3], delta, self);
		self.print_("Druga cwiartka")
		stat[int(len(R)/2): , 0:int(len(R[0])/2)] = Kompresuj(R[int(len(R)/2): , 0:int(len(R[0])/2)], D[2], delta, self);
		self.print_("Trzecia cwiartka")
		stat[0:int(len(R)/2), int(len(R[0])/2): ] = Kompresuj(R[0:int(len(R)/2), int(len(R[0])/2): ], D[1], delta, self);
		self.print_("Czwarta cwiartka")
		stat[int(len(R)/2): , int(len(R[0])/2): ] = Kompresuj(R[int(len(R)/2): , int(len(R[0])/2): ], D[0], delta, self);
#		print(stat);
		R_size = (len(R), len(R[0]))

		self.print_("Tworzenie dodatkowych rangeBloków")
		B = rangeBlocks(przesunGora(A), 8);
		B_wsp = kodujDCTJPEG(B, self);

		C = rangeBlocks(przesunLewo(A), 8);
		C_wsp = kodujDCTJPEG(C, self);

		Maper = [124, 112, 18, 199, 255, 10, 123, 32, 96, 111, 67, 56, 43, 22, 34, 89, 102, 123, 11, 2, 5, 7, 192, 123, 253]
		#Tablice mapowania 4 wpisy w każdym wpis [i][j] w którym są współrzędne punktu na który mapujemy
		#I tak np. R[0][0] mapujemy na A_map[0][0][0]
		A_map = [getMapping(Maper[0:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[1:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[2:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[3:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30)]
				
		B_map = [getMapping(Maper[4:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[5:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[6:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[7:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30)]
				
		C_map = [getMapping(Maper[8:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[9:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[10:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[11:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30)]
		self.print_("Zamiana wspolczynnikow na wartosci binarne")
		wsp = [[None] * R_size[1] for i in range(R_size[0])]
		binwsp = [[''] * R_size[1] for i in range(R_size[0])]
		binary = [[None] * R_size[1] for i in range(R_size[0])]
		
		#self.print_("Dekompresja obrazka");
		#G = Dekompresuj(im.size, stat);
		#self.print_("Wyswietlenie obrazka")
		#Zamiana współczynników kodowania fraktalnego na binaria
		for i in range(R_size[0]):
			for j in range(R_size[1]):
				binwsp[i][j] += intTobin(stat[i][j][0][0], self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["x"], 0)#(format(stat[i][j][0][0], '0%ib' %(7)))
				binwsp[i][j] += intTobin(stat[i][j][0][1], self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["y"], 0)#(format(stat[i][j][0][0], '0%ib' %(7)))
				binwsp[i][j] += intTobin(stat[i][j][1][0]/zmienne["sMax"]*2**(self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["s"] - 1), self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["s"], 1)#(format(stat[i][j][0][0], '0%ib' %(7)))
				binwsp[i][j] += intTobin(stat[i][j][1][1]/zmienne["oMax"]*2**(self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["o"] - 1), self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["o"], 1)#(format(stat[i][j][0][0], '0%ib' %(7)))
				binwsp[i][j] += intTobin(stat[i][j][1][3], 3, 0)#(format(stat[i][j][0][0], '0%ib' %(7)))
				
				"""if(len(binwsp[i][j]) > 32):
					self.print_("Za duzo bitow dla kodowania fraktalnego")
					binwsp[i][j] = binwsp[i][j][0:32];
					#self.print_(str(stat[i][j]));
					#sys.exit();"""

		#self.print_(B_wsp);
		#sys.exit()
		"""
		W binwsp mamy zapisane wartości binarne współczynników kompresji fraktalnej odpowiadające analogicznie: binwsp[0][0] = R[0][0]
		Informacje o R[0][0] zapisujemy w A_map[0][0][0] tzn [0][0] dla 0 ćwiartki numerując od lewej górnej zgodnie ze wskazówkami zegara
		"""
		#Najgorsza część, ustalenie co w którym bloku będzie zapisane
		for counter in range(0, 4):
			#Ranges, to będą współczynniki przydatne prz pętlach
			if counter == 0:
				ranges = [[0, 0], [3,2,1], []] #Tutaj mapujemy na blok 0
			elif counter == 1:
				ranges = [[int(R_size[0]/2), 0], [2, 3, 0], []] #Tutaj mapujemy na blok 1
			elif counter == 2:
				ranges = [[0, int(R_size[1]/2)], [1, 0, 3], []] #Tutaj mapujemy na blok 2
			elif counter == 3:
				ranges = [[int(R_size[0]/2), int(R_size[1]/2)], [0, 1, 2], []] #Tutaj mapujemy na blok 3
			#Mapowanie współczynników
			#Krótki opis dla mnie :)
			#Musimy wiedzieć o ile przesunąć i i j żebyśmy mapowali z odpowiedniego kwadrata :D
			#damy to sobie jako ranges[2][0-2][0-1]
			for i in range(3):
				if(ranges[1][i]) == 0:
					ranges[2].append([0, 0])
				if(ranges[1][i]) == 1:
					ranges[2].append([int(R_size[0]/2), 0])
				if(ranges[1][i]) == 2:
					ranges[2].append([0, int(R_size[1]/2)])
				if(ranges[1][i]) == 3:
					ranges[2].append([int(R_size[0]/2), int(R_size[1]/2)])
			#x,y to wspolrzedne na ktore mapujemy, i,j to wspolrzedne z ktorych mapujemy
			for i in range(int(R_size[0]/2)):
				for j in range(int(R_size[1]/2)):
					a = i + ranges[2][0][0]
					b = j + ranges[2][0][1]
					x = A_map[ranges[1][0]][i][j][0] + ranges[0][0]
					y = A_map[ranges[1][0]][i][j][1] + ranges[0][1]
					
					binary[x][y] = binwsp[a][b]
					if(len(binary[x][y])) > self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"]:
						self.print_("a");
						sys.exit()
			#sys.exit();
			#Mapowanie bloków B
			for i in range(int(R_size[0]/2)):
				for j in range(int(R_size[1]/2)):
					a = i + ranges[2][1][0]
					b = j + ranges[2][1][1]
					x = B_map[ranges[1][1]][i][j][0] + ranges[0][0]
					y = B_map[ranges[1][1]][i][j][1] + ranges[0][1]
					if binary[x][y] == None:
						self.print_(str([x, y]))
						self.print_(str([i, j]))
						sys.exit();
					binary[x][y] += B_wsp[a][b]
					if(len(binary[x][y])) > self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] + self.config["profile"][self.config["profil"]]["bity"]["DCT1"]:
						self.print_("b");
						sys.exit()


			#Mapowanie bloków C
			for i in range(int(R_size[0]/2)):
				for j in range(int(R_size[1]/2)):
					x = C_map[ranges[1][2]][i][j][0] + ranges[0][0]
					y = C_map[ranges[1][2]][i][j][1] + ranges[0][1]
					binary[x][y] += C_wsp[i + ranges[2][2][0]][j + ranges[2][2][1]]
					if(len(binary[x][y])) > self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] + self.config["profile"][self.config["profil"]]["bity"]["DCT1"] + self.config["profile"][self.config["profil"]]["bity"]["DCT2"]:
						self.print_("c");
						sys.exit()

		self.print_("Zapisywanie danych w obrazku :)")
		for i in range(R_size[0]):
			for j in range(R_size[1]):
				R[i][j] = zapiszWiadomosc(R[i][j], binary[i][j])
				R[i][j] = zapiszWiadomosc(R[i][j], binary[i][j] + md5Bloku(R[i][j]))

		H = numpy.matrix(im.getdata()).reshape((im.size[1], im.size[0]))
		for i in range(R_size[0]):
			for j in range(R_size[1]):
				H[blockSize*i:blockSize*(i+1),blockSize*j:blockSize*(j+1)] = R[i][j]
				
		H = Image.fromarray(numpy.uint8(numpy.matrix(H)))	#Wyswietlanie obrazka, nie wiem jak dziala na windowsie
		H.show()
		
		try:
			if self.plikZapisz == "":
				self.saveDialog();
			nazwa = self.plikZapisz;
		except:
			self.saveDialog();
			nazwa = self.plikZapisz;
			if nazwa == "":
				nazwa = "Watermarked.pgm"
		H.save(nazwa)
		self.print_("Zapisano jako `%s`" %(nazwa))
		
		self.plikOtworz = "";
		self.plikZapisz = "";
	
	def check(self):
		"""
		sprawdzanie znaku wodnego
		TODO: Komentarze
		"""
		
		self.statystyki = {
			"hash" : {
				"dobrze" : 0,
				"zle" : 0,
			},
			"fraktal" : {
				"dobrze" : 0,
				"zle" : 0,
				"nieznany" : 0
			},
			"dct1" : {
				"dobrze" : 0,
				"zle" : 0,
				"nieznany" : 0
			},
			"dct2" : {
				"dobrze" : 0,
				"zle" : 0,
				"nieznany" : 0
			},
		}
		
		if self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] \
			+ self.config["profile"][self.config["profil"]]["bity"]["DCT1"] \
			+ self.config["profile"][self.config["profil"]]["bity"]["DCT2"] \
			+ self.config["profile"][self.config["profil"]]["bity"]["hash"] > 128:
			self.print_("Za dużo bitów. Zmień ustawienia");
			return -1;
		try:
			if self.plikOtworz == "":
				self.openDialog();
			nazwa = self.plikOtworz;
		except:
			self.openDialog();
			nazwa = self.plikOtworz;
			if nazwa == "":
				self.print_("Nie wybrano pliku");
				return -1;
		try:
			im = Image.open(nazwa); 	#Odczytanie obrazu
		except IOError:
			self.print_("Wygląda na to że plik nie jest obrazkiem")
			return -1
		if not (im.mode == 'L'):
			self.print_("Inne rodzaje obrazu niż skala szarości, nie są jeszcze obsługiwane")
			return -1
		if im.size[0] % 8 or im.size[1] % 8:		
			self.print_("Obrazy o wymiarach niepodzielnych przez 8 nie są obsługiwane")
			return -1

		blockSize = 8
		#delta = 128;
		if(im.size[0] > im.size[1]):
			delta = int(im.size[0]/(2**self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["x"]));
		else:
			delta = int(im.size[1]/(2**self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["y"]));
			
		A = numpy.matrix(im.getdata()).reshape((im.size[1], im.size[0]));
		A2 = usun2LSB(A)[0];
		B_ = rangeBlocks(przesunGora(A2.reshape([im.size[1], im.size[0]])), 8);
		B_wsp = kodujDCTJPEG(B_, self);
		C_ = rangeBlocks(przesunLewo(A2.reshape([im.size[1], im.size[0]])), 8)
		C_wsp = kodujDCTJPEG(C_, self);
		self.print_("Tworzenie rangeBloków 8x8");
		R = rangeBlocks(A, 8);
		self.print_("Tworzenie rangeBloków 4x4");
		S = rangeBlocks(A, 4);
		w=[3, 1, 1, 1]
		R_size = (len(R), len(R[0]))
		binary = [[[None]] * R_size[1] for i in range(R_size[0])]
		A = [[[None]] * R_size[1] for i in range(R_size[0])]
		B = [[[None]] * R_size[1] for i in range(R_size[0])]
		C = [[[None]] * R_size[1] for i in range(R_size[0])]
		mk = [[[None]] * R_size[1] for i in range(R_size[0])]
		tamp1 = [[[None]] * 2*R_size[1] for i in range(2*R_size[0])]
		tamp2 = [[[None]] * 2*R_size[1] for i in range(2*R_size[0])]
		tamp3 = [[[None]] * 2*R_size[1] for i in range(2*R_size[0])]
		tamp4 = [[[None]] * 2*R_size[1] for i in range(2*R_size[0])]
		t = [[[None]] * 2*R_size[1] for i in range(2*R_size[0])]

		#Level1
			
		for i in range(R_size[0]):
			for j in range(R_size[1]):
				tmp = sprawdzmd5Bloku(R[i][j]);
				R[i][j] = tmp[1]
				binary[i][j] = tmp[2];
				mk[i][j] = tmp[0]
				tamp1[2*i][2*j] = mk[i][j]
				tamp1[2*i][2*j+1] = mk[i][j]
				tamp1[2*i+1][2*j] = mk[i][j]
				tamp1[2*i+1][2*j+1] = mk[i][j]
				if mk[i][j] == -1:
					self.statystyki["hash"]["zle"] += 1
					#self.print_("invalid hash");
				else:
					self.statystyki["hash"]["dobrze"] += 1

		#Level2

		Maper = [124, 112, 18, 199, 255, 10, 123, 32, 96, 111, 67, 56, 43, 22, 34, 89, 102, 123, 11, 2, 5, 7, 192, 123, 253]
		
		#Tablice mapowania 4 wpisy w każdym wpis [i][j] w którym są współrzędne punktu na który mapujemy
		#I tak np. R[0][0] mapujemy na A_map[0][0][0]
		A_map = [getMapping(Maper[0:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[1:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[2:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[3:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30)]
				
		B_map = [getMapping(Maper[4:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[5:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[6:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[7:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30)]
				
		C_map = [getMapping(Maper[8:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[9:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[10:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30), 
				getMapping(Maper[11:], [int(R_size[0]/2), int(R_size[1]/2)], str(self.config["profile"][self.config["profil"]]["haslo"]) * 30)]

		for counter in range(0, 4):
			#Ranges, to będą współczynniki przydatne prz pętlach
			if counter == 0:
				ranges = [[0, 0], [3,2,1], []] #Tutaj mapujemy na blok 0
			elif counter == 1:
				ranges = [[int(R_size[0]/2), 0], [2, 3, 0], []] #Tutaj mapujemy na blok 1
			elif counter == 2:
				ranges = [[0, int(R_size[1]/2)], [1, 0, 3], []] #Tutaj mapujemy na blok 2
			elif counter == 3:
				ranges = [[int(R_size[0]/2), int(R_size[1]/2)], [0, 1, 2], []] #Tutaj mapujemy na blok 3
			#Mapowanie współczynników
			#Krótki opis dla mnie :)
			#Musimy wiedzieć o ile przesunąć i i j żebyśmy mapowali z odpowiedniego kwadrata :D
			#damy to sobie jako ranges[2][0-2][0-1]
			for i in range(3):
				if(ranges[1][i]) == 0:
					ranges[2].append([0, 0])
				if(ranges[1][i]) == 1:
					ranges[2].append([int(R_size[0]/2), 0])
				if(ranges[1][i]) == 2:
					ranges[2].append([0, int(R_size[1]/2)])
				if(ranges[1][i]) == 3:
					ranges[2].append([int(R_size[0]/2), int(R_size[1]/2)])
			#x,y to wspolrzedne na ktore mapujemy, a,b to wspolrzedne z ktorych mapujemy
			self.print_("Level-2_%i" %(counter));
			for i in range(int(R_size[0]/2)):
				for j in range(int(R_size[1]/2)):
					a = i + ranges[2][0][0]
					b = j + ranges[2][0][1]
					x = A_map[ranges[1][0]][i][j][0] + ranges[0][0]
					y = A_map[ranges[1][0]][i][j][1] + ranges[0][1]
					if mk[x][y] == 1: #Sprawdzamy czy mapowany blok jest ok
						#A[i + ranges[2][0][0]][j + ranges[2][0][1]] = binary[x][y][0:32]
						A[a][b] = binariaToDec(binary[x][y], [[self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["x"], 0],
						 [self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["y"],0], 
						 [self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["s"], 1],
						 [self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["o"], 1], [3, 0]])
						A[a][b][0] *=delta
						A[a][b][1] *=delta
						A[a][b][2] *= zmienne["sMax"]/2**(self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["s"] - 1)
						A[a][b][3] *= zmienne["oMax"]/2**(self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["o"] - 1)
						
						if counter==1 or counter == 3:
							A[a][b][0] += im.size[1]/2;
						if counter==2 or counter == 3:
							A[a][b][1] += im.size[0]/2;
						#self.print_(a,b,x,y);
						#self.print_(A[a][b]);
						#self.print_(int(A[a][b][0]/8), int(A[a][b][1]/8));
						#self.print_(len(mk));
						#self.print_(len(mk[0]));
						#self.print_(mk[12][44])
						if mk[int(A[a][b][0]/8)][int(A[a][b][1]/8)] == 1: #Sprawdzamy czy domain blok jest ok
							wsp2 = porownaj(R[a][b], przeksztalcenie(skaluj(A2[A[a][b][0]:A[a][b][0] + 16, A[a][b][1]:A[a][b][1] + 16]), A[a][b][4]))
							#sys.exit()
							wsp2[0] = binariaToDec(intTobin(wsp2[0]/zmienne["sMax"]*2**(self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["s"] - 1), self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["s"], 1), [[self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["s"], 1]])[0] * zmienne["sMax"]/2**(self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["s"] - 1)
							wsp2[1] = binariaToDec(intTobin(wsp2[1]/zmienne["oMax"]*2**(self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["o"] - 1), self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["o"], 1), [[self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["o"], 1]])[0] * zmienne["oMax"]/2**(self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["o"] - 1)
							if A[a][b][2] != wsp2[0] or A[a][b][3] != wsp2[1]:
								self.print_(str(wsp2) + str(A[a][b]))
								tmp = -1;
								self.statystyki["fraktal"]["zle"] += 1;
								#self.print_("invalid fractals coefficients")
								#self.print_("Aij jest invalid");
								#self.print_([a, b, A[a][b], wsp2])
							else:
								self.statystyki["fraktal"]["dobrze"] += 1;
								tmp = 1;
								#self.print_("Aij jest valid")
						else:
							self.statystyki["fraktal"]["nieznany"] += 1;
							tmp = 0
							#self.print_("Aij is undefined");
					else:
						self.statystyki["fraktal"]["nieznany"] += 1;
						#self.print_(a,b, x, y)
						tmp = 0;
						#self.print_("Aij is undefined")
						
					A[a][b] = [tmp, A[a][b]]
					tamp2[2*x][2*y] = tmp
					tamp2[2*x][2*y+1] = tmp
					tamp2[2*x+1][2*y] = tmp
					tamp2[2*x+1][2*y+1] = tmp
			#sys.exit()
#			print(A)
			self.print_("Level-3_%i" %(counter));
			#Mapowanie bloków B
			for i in range(int(R_size[0]/2)):
				for j in range(int(R_size[1]/2)):
					a = i + ranges[2][1][0]
					b = j + ranges[2][1][1]
					x = B_map[ranges[1][1]][i][j][0] + ranges[0][0]
					y = B_map[ranges[1][1]][i][j][1] + ranges[0][1]
					
					if mk[x][y] == 1: #Sprawdzamy czy mapowany blok jest ok
						#self.print_(B_wsp[a][b])
						#self.print_(binary[x][y][32:72])
						if binary[x][y][self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"]:self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] + self.config["profile"][self.config["profil"]]["bity"]["DCT1"]] == B_wsp[a][b]:
							tmp = 1
							self.statystyki["dct1"]["dobrze"] += 1;
						else:
							self.statystyki["dct1"]["zle"] += 1;
							tmp = -1
					else:
						self.statystyki["dct1"]["nieznany"] += 1;
						tmp = 0
					
					B[a][b] = [tmp, [x,y]]
					tamp3[(2*x+1) % (2*R_size[0])][2*y] = tmp
					tamp3[(2*x+1) % (2*R_size[0])][2*y+1] = tmp
					tamp3[(2*x+2) % (2*R_size[0])][2*y] = tmp
					tamp3[(2*x+2) % (2*R_size[0])][2*y+1] = tmp


			self.print_("Level-4_%i" %(counter));
			#Mapowanie bloków C
			for i in range(int(R_size[0]/2)):
				for j in range(int(R_size[1]/2)):
					a = i + ranges[2][2][0]
					b = j + ranges[2][2][1]
					x = C_map[ranges[1][2]][i][j][0] + ranges[0][0]
					y = C_map[ranges[1][2]][i][j][1] + ranges[0][1]
					
					if mk[x][y] == 1: #Sprawdzamy czy mapowany blok jest ok
						if binary[x][y][self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] + self.config["profile"][self.config["profil"]]["bity"]["DCT1"]:self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] + self.config["profile"][self.config["profil"]]["bity"]["DCT1"] + self.config["profile"][self.config["profil"]]["bity"]["DCT2"]] == C_wsp[a][b]:
							tmp = 1
							self.statystyki["dct2"]["dobrze"] += 1;
						else:
							self.statystyki["dct2"]["zle"] += 1;
							tmp = -1
					else:
						self.statystyki["dct2"]["nieznany"] += 1;
						tmp = 0
					
					C[a][b] = [tmp, [x,y]]
					tamp4[2*x][(2*y+1) % (2*R_size[1])] = tmp
					tamp4[2*x][(2*y+2) % (2*R_size[1])] = tmp
					tamp4[2*x+1][(2*y+1) % (2*R_size[1])] = tmp
					tamp4[2*x+1][(2*y+2) % (2*R_size[1])] = tmp
					
		self.print_("No to jazda")
		for i in range(2*R_size[0]):
			for j in range(2*R_size[1]):
#				print(tamp1[i][j], tamp2[i][j], tamp3[i][j], tamp4[i][j])
#				print(w[0], w[0], w[0], w[0])
				t[i][j] = w[0]*tamp1[i][j] + w[1]*tamp2[i][j] + w[2]*tamp3[i][j] + w[3]*tamp4[i][j]
				#if t[i][j] < 0:
				#	self.print_([i, j], "is damaged");
				#	self.print_(A[i][j])
					
		for i in range(R_size[0]):
			for j in range(R_size[1]):
					A[i][j].append(0)
					if A[i][j][0] < 0:
						x = A[i][j][1][0]
						y = A[i][j][1][1]
						if mk[int(x/8)][int(y/8)] >= 0 \
						and mk[int(x/8) + 1][int(y/8)] >= 0 \
						and mk[int(x/8) +1 ][int(y/8) +1] >= 0 \
						and mk[int(x/8)][int(y/8) + 1] >= 0:
							R[i][j] = DekompresujPojedynczy(przeksztalcenie(skaluj(A2[x:x+16, y:y+16]), A[i][j][1][4]), A[i][j][1][2], A[i][j][1][3])
							A[i][j][2] = 1
							#self.print_(i,j)
						else:
							A[i][j][2] = -1
						#	R[i][j] *= 0	
						#	self.print_(x,y)

		for i in range(R_size[0]):
			for j in range(R_size[1]):
				B[i][j].append(0)
				if B[i][j][0] < 0:
						x = B[i][j][1][0]
						y = B[i][j][1][1]
						if mk[x][y] == 1:
							B_[i][j] = dekodujDCT(dekodujWspDCT(binary[x][y][self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"]:self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] + self.config["profile"][self.config["profil"]]["bity"]["DCT1"]], 6, self))
							B[i][j][2] = 1
						else:
							B_[i][j]*=0;
							B[i][j][2] = -1

		for i in range(R_size[0]):
			for j in range(R_size[1]):
				C[i][j].append(0)
				if C[i][j][0] < 0:
						#self.print_(C[i][j])
						x = C[i][j][1][0]
						y = C[i][j][1][1]
						if mk[x][y] == 1:
							C_[i][j] = dekodujDCT(dekodujWspDCT(binary[x][y][self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] + self.config["profile"][self.config["profil"]]["bity"]["DCT1"]:self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] + self.config["profile"][self.config["profil"]]["bity"]["DCT1"] + self.config["profile"][self.config["profil"]]["bity"]["DCT2"]], 6, self))
							C[i][j][2] = 1
						else:
							C_[i][j]*=0;
							C[i][j][2] = -1


		H = numpy.matrix(im.getdata()).reshape((im.size[1], im.size[0]))
		for i in range(R_size[0]):
			for j in range(R_size[1]):
				H[8*i:8*i+8, 8*j:8*j+8] = C_[i][j]
		#H = H.reshape([im.size[1], im.size[0]])
		H_C = przesunLewo(H, H.shape[1]-4);
		G = Image.fromarray(numpy.uint8(numpy.matrix(H_C)))	#Wyswietlanie obrazka, nie wiem jak dziala na windowsie
		#G.show()
		G.save(nazwa + "Recover_C.pgm")
		#H = Image.fromarray(numpy.uint8(numpy.matrix(H)))	#Wyswietlanie obrazka, nie wiem jak dziala na windowsie
		#H.show()

		H = numpy.matrix(im.getdata()).reshape((im.size[1], im.size[0]))
		for i in range(R_size[0]):
			for j in range(R_size[1]):
				H[8*i:8*i+8, 8*j:8*j+8] = B_[i][j]
		#H = H.reshape([im.size[1], im.size[0]])
		H_B = przesunGora(H, H.shape[0]-4);
		G = Image.fromarray(numpy.uint8(numpy.matrix(H_B)))	#Wyswietlanie obrazka, nie wiem jak dziala na windowsie
		#G.show()
		G.save(nazwa + "Recover_B.pgm")
		#H = Image.fromarray(numpy.uint8(numpy.matrix(H)))	#Wyswietlanie obrazka, nie wiem jak dziala na windowsie
		#H.show()
				
		H = numpy.matrix(im.getdata()).reshape((im.size[1], im.size[0]))
		for i in range(R_size[0]):
			for j in range(R_size[1]):
				H[8*i:8*i+8, 8*j:8*j+8] = R[i][j]
		#H = H.reshape([im.size[1], im.size[0]])
		H_A = H;
		G = Image.fromarray(numpy.uint8(numpy.matrix(H_A)))	#Wyswietlanie obrazka, nie wiem jak dziala na windowsie
		#G.show()
		G.save(nazwa + "Recover_A.pgm")
		#H = Image.fromarray(numpy.uint8(numpy.matrix(H)))	#Wyswietlanie obrazka, nie wiem jak dziala na windowsie
		#H.show()


		for i in range(im.size[1]):
			for j in range(im.size[0]):
				if mk[int(i/8)][int(j/8)] < 1:
					"""if mk[int(i/8)][int(j/8)] < 1 \
					or A[int(i/8)][int(j/8)][0] < 1 \
					or B[int(((i-4) % len(H))/8)][int(j/8)][0] < 1 \
					or C[int(i/8)][int(((j-4) % len(H))/8)][0] < 1:"""
					betas = [];
					
					if A[int(i/8)][int(j/8)][2] > 0:
						betas.append(1);
					else:
						betas.append(0)
						
					if B[int(((i-4) % im.size[1])/8)][int(j/8)][2] > 0:
						betas.append(2);
					else:
						betas.append(0)
						
					if C[int(i/8)][int(((j-4) % im.size[0])/8)][2] > 0:
						betas.append(2);
					else:
						betas.append(0)
						
					#self.print_(i, j, betas)
					if(sum(betas) > 0):
						H[i,j] = (betas[0]*H_A[i,j] + betas[1]*H_B[i,j] + betas[2]*H_C[i,j]) / (betas[0] + betas[1] + betas[2])
					if(sum(betas) == 3):
						try:
							t[math.floor(i/4)][math.floor(j/4)] = 1;
						except IndexError:
							""
						try:
							t[math.floor(i/4)+1][math.floor(j/4)] = 1;
						except IndexError:
							""
						try:
							t[math.floor(i/4)+1][math.floor(j/4)+1] = 1;
						except IndexError:
							""
						try:
							t[math.floor(i/4)][math.floor(j/4)+1] = 1;
						except IndexError:
							""
#					else:
#						H[i,j] = H_A[i,j]*0;
					#else:
					#	self.print_("Cannot recover", i, j)
#		W = Image.fromarray(numpy.uint8(numpy.matrix(H)))	#Wyswietlanie obrazka, nie wiem jak dziala na windowsie
#			W.show()
#		W.save("dev/000.pgm")
					
		for a in range(10):
			self.progress(a, 100)
			for i in range(1, len(t)-1):
				for j in range(1, len(t[0])-1):
					if t[i][j] <= 0:
						licznik = 0;
						suma = numpy.matrix(H[0:4,0:4])*0;
						if t[i-1][j-1] > 0:
							licznik += 1;
							suma += H[(i-1)*4:(i)*4, (j-1)*4:(j)*4]
						if t[i-1][j] > 0:
							licznik += 1;
							suma += H[(i-1)*4:(i)*4, j*4:(j+1)*4]
						if t[i-1][j+1] > 0:
							licznik += 1;
							suma += H[(i-1)*4:(i)*4, (j+1)*4:(j+2)*4]
						if t[i][j-1] > 0:
							licznik += 1;
							suma += H[i*4:(i+1)*4, (j-1)*4:(j)*4]
						if t[i][j+1] > 0:
							licznik += 1;
							suma += H[i*4:(i+1)*4, (j+1)*4:(j+2)*4]
						if t[i+1][j-1] > 0:
							licznik += 1;
							suma += H[(i+1)*4:(i+2)*4, (j-1)*4:(j)*4]
						if t[i+1][j] > 0:
							licznik += 1;
							suma += H[(i+1)*4:(i+2)*4, j*4:(j+1)*4]
						if t[i+1][j+1] > 0:
							licznik += 1;
							suma += H[i*4:(i+1)*4, (j+1)*4:(j+2)*4]
						if licznik > 3:
							#for z in range(20):
							if a%2 != 0:
								H[i*4:(i+1)*4, j*4:(j+1)*4] = suma/licznik;
							elif a > 0:
								#if a>10:
								t[i][j] +=1 ;
			
#			W = Image.fromarray(numpy.uint8(numpy.matrix(H)))	#Wyswietlanie obrazka, nie wiem jak dziala na windowsie
#			W.show()
#			W.save("dev/%i.pgm" %(a))
		self.progress(1,1)
		self.print_("")
		H = Image.fromarray(numpy.uint8(numpy.matrix(H)))	#Wyswietlanie obrazka, nie wiem jak dziala na windowsie
#		H.show()
		
		try:
			if self.plikZapisz == "":
				self.saveDialog();
			nazwa = self.plikZapisz;
		except:
			self.saveDialog();
			nazwa = self.plikZapisz;
			if nazwa == "":
				nazwa = "Recovered.pgm"
		H.save(nazwa)
		self.print_("Zapisano jako `%s`" %(nazwa))
		
		self.plikOtworz = "";
		self.plikZapisz = "";
		print(str(self.statystyki));

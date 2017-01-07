"""
gui.py
"""

from Funkcje import *


class Sefr(object):
    """
    Klasa do obsługi aplikacji graficznej
    """

    def __init__(self):
        """
        Konstruktor
        """
        self.config = {
            "profile": [
                {
                    "nazwa": "default",
                    "bity": {
                        "fraktal":
                            {
                                "suma": 32,
                                "x": 7,
                                "y": 7,
                                "s": 8,
                                "o": 7,
                                "e": 3,
                            },
                        "DCT1": 40,
                        "DCT2": 40,
                        "hash": 16,
                    },
                    "haslo": "Domysle haslo"
                }
            ],
            "profil": 0
        }
        if len(sys.argv) >= 3 and sys.argv[3] == 'znak':
            self.source_file = sys.argv[1]
            self.destination_file = sys.argv[2]
            self.add_watermark()

        elif len(sys.argv) >= 3 and sys.argv[3] == 'recover':
            self.source_file = sys.argv[1]
            self.destination_file = sys.argv[2]
            self.check()

    @classmethod
    def print_(cls, tekst):
        """
        Prints text (logger)

        Args:
            tekst:

        Returns:

        """
        print(tekst)

    @classmethod
    def progress(cls, val, max_val, bar_length=50):
        """
        Shows progress of operation

        Args:
            val:
            max_val:
            bar_length:

        Returns:

        """
        percent = val / max_val
        hashes = '#' * int(round(percent * bar_length))
        spaces = ' ' * (bar_length - len(hashes))
        sys.stdout.write("\rPostep: [{0}] {1}%     ".format(hashes + spaces, int(round(percent * 100000)) / 1000))
        sys.stdout.flush()

    def count_bits(self):
        """
        Count sum of bits

        Returns:

        """
        return self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] + \
               self.config["profile"][self.config["profil"]]["bity"]["DCT1"] + \
               self.config["profile"][self.config["profil"]]["bity"]["DCT2"] + \
               self.config["profile"][self.config["profil"]]["bity"]["hash"]

    # Dodawanie znaku wodnego
    def add_watermark(self):
        """

        Returns:

        """
        if self.count_bits() > 128:
            self.print_("Za dużo bitów. Obecnie: %i, wymagane 128 Zmień ustawienia" % (self.count_bits()))
            return -1

        try:
            im = Image.open(self.source_file)  # Odczytanie obrazu
        except IOError:
            self.print_("Wygląda na to że plik nie jest obrazkiem")
            return -1
        if not (im.mode == 'L'):
            self.print_("Inne rodzaje obrazu niż skala szarości, nie są jeszcze obsługiwane")
            return -1
        if im.size[0] % 8 or im.size[1] % 8:
            self.print_("Obrazy o wymiarach niepodzielnych przez 8 nie są obsługiwane")
            return -1

        matrix_a = remove_2_lsb(numpy.matrix(im.getdata()).reshape((im.size[1], im.size[0])))[0]

        block_size = 8
        self.print_("Kompresja obrazka o rozmiarze " + str(matrix_a.shape))

        # Count delta (should be possible to save coords of block on define number of bits
        if im.size[0] > im.size[1]:
            delta = int(im.size[0] / (2 ** self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["x"]))
        else:
            delta = int(im.size[1] / (2 ** self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["y"]))

        self.print_("Delta: {0}".format(delta))
        self.print_("Tworzenie rangeBloków")
        matrix_r = numpy.array(rangeBlocks(matrix_a, block_size))  # Tworzenie rangeBlokow
        self.print_("Tworzenie domainBloków w czterech ćwiartkach")

        # Tworzenie domain blokow w czterech cwiartkach
        matrix_d = [create_domain_blocks(matrix_a[0:int(matrix_a.shape[0] / 2), 0:int(matrix_a.shape[1] / 2)],
                                         block_size, delta, self),
                    create_domain_blocks(matrix_a[int(matrix_a.shape[0] / 2):, 0:int(matrix_a.shape[1] / 2)],
                                         block_size, delta, self),
                    create_domain_blocks(matrix_a[0:int(matrix_a.shape[0] / 2), int(matrix_a.shape[1] / 2):],
                                         block_size, delta, self),
                    create_domain_blocks(matrix_a[int(matrix_a.shape[0] / 2):, int(matrix_a.shape[1] / 2):],
                                         block_size, delta, self)]

        self.print_("Kompresja obrazka")

        stat = numpy.array([[[[-1, -1], [-1, -1, -1]]] * len(matrix_r[i]) for i in range(len(matrix_r))])

        self.print_("Pierwsza cwiartka")
        stat[0:int(len(matrix_r) / 2), 0:int(len(matrix_r[0]) / 2)] = Kompresuj(
            matrix_r[0:int(len(matrix_r) / 2), 0:int(len(matrix_r[0]) / 2)], matrix_d[3],
            delta, self)
        self.print_("Druga cwiartka")
        stat[int(len(matrix_r) / 2):, 0:int(len(matrix_r[0]) / 2)] = Kompresuj(
            matrix_r[int(len(matrix_r) / 2):, 0:int(len(matrix_r[0]) / 2)], matrix_d[2], delta,
            self)
        self.print_("Trzecia cwiartka")
        stat[0:int(len(matrix_r) / 2), int(len(matrix_r[0]) / 2):] = Kompresuj(
            matrix_r[0:int(len(matrix_r) / 2), int(len(matrix_r[0]) / 2):], matrix_d[1], delta,
            self)
        self.print_("Czwarta cwiartka")
        stat[int(len(matrix_r) / 2):, int(len(matrix_r[0]) / 2):] = Kompresuj(
            matrix_r[int(len(matrix_r) / 2):, int(len(matrix_r[0]) / 2):], matrix_d[0], delta,
            self)

        r_size = (len(matrix_r), len(matrix_r[0]))

        self.print_("Tworzenie dodatkowych rangeBloków")
        matrix_b = rangeBlocks(przesunGora(matrix_a), 8)
        coeff_b = code_dct_jpeg(matrix_b, self)

        matrix_c = rangeBlocks(przesunLewo(matrix_a), 8)
        coeff_c = code_dct_jpeg(matrix_c, self)

        maper = [124, 112, 18, 199, 255, 10, 123, 32, 96, 111, 67, 56, 43, 22, 34, 89, 102, 123, 11, 2, 5, 7, 192, 123,
                 253]
        # Tablice mapowania 4 wpisy w każdym wpis [i][j] w którym są współrzędne punktu na który mapujemy
        # I tak np. matrix_r[0][0] mapujemy na A_map[0][0][0]
        A_map = [getMapping(maper[0:], [int(r_size[0] / 2), int(r_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(maper[1:], [int(r_size[0] / 2), int(r_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(maper[2:], [int(r_size[0] / 2), int(r_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(maper[3:], [int(r_size[0] / 2), int(r_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30)]

        B_map = [getMapping(maper[4:], [int(r_size[0] / 2), int(r_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(maper[5:], [int(r_size[0] / 2), int(r_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(maper[6:], [int(r_size[0] / 2), int(r_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(maper[7:], [int(r_size[0] / 2), int(r_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30)]

        C_map = [getMapping(maper[8:], [int(r_size[0] / 2), int(r_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(maper[9:], [int(r_size[0] / 2), int(r_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(maper[10:], [int(r_size[0] / 2), int(r_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(maper[11:], [int(r_size[0] / 2), int(r_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30)]
        self.print_("Zamiana wspolczynnikow na wartosci binarne")
        wsp = [[None] * r_size[1] for _ in range(r_size[0])]
        binwsp = [[''] * r_size[1] for _ in range(r_size[0])]
        binary = [[None] * r_size[1] for _ in range(r_size[0])]

        # self.print_("Dekompresja obrazka")
        # G = Dekompresuj(im.size, stat)
        # self.print_("Wyswietlenie obrazka")
        # Zamiana współczynników kodowania fraktalnego na binaria
        for i in range(r_size[0]):
            for j in range(r_size[1]):
                binwsp[i][j] += intTobin(stat[i][j][0][0],
                                         self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["x"],
                                         0)  # (format(stat[i][j][0][0], '0%ib' %(7)))
                binwsp[i][j] += intTobin(stat[i][j][0][1],
                                         self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["y"],
                                         0)  # (format(stat[i][j][0][0], '0%ib' %(7)))
                binwsp[i][j] += intTobin(stat[i][j][1][0] / zmienne["sMax"] * 2 ** (
                    self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["s"] - 1),
                                         self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["s"],
                                         1)  # (format(stat[i][j][0][0], '0%ib' %(7)))
                binwsp[i][j] += intTobin(stat[i][j][1][1] / zmienne["oMax"] * 2 ** (
                    self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["o"] - 1),
                                         self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["o"],
                                         1)  # (format(stat[i][j][0][0], '0%ib' %(7)))
                binwsp[i][j] += intTobin(stat[i][j][1][3], 3, 0)  # (format(stat[i][j][0][0], '0%ib' %(7)))

                """if(len(binwsp[i][j]) > 32):
					self.print_("Za duzo bitow dla kodowania fraktalnego")
					binwsp[i][j] = binwsp[i][j][0:32]
					#self.print_(str(stat[i][j]))
					#sys.exit()"""

        # self.print_(B_wsp)
        # sys.exit()
        """
		W binwsp mamy zapisane wartości binarne współczynników kompresji fraktalnej odpowiadające analogicznie: binwsp[0][0] = matrix_r[0][0]
		Informacje o matrix_r[0][0] zapisujemy w A_map[0][0][0] tzn [0][0] dla 0 ćwiartki numerując od lewej górnej zgodnie ze wskazówkami zegara
		"""
        # Najgorsza część, ustalenie co w którym bloku będzie zapisane
        for counter in range(0, 4):
            # Ranges, to będą współczynniki przydatne prz pętlach
            if counter == 0:
                ranges = [[0, 0], [3, 2, 1], []]  # Tutaj mapujemy na blok 0
            elif counter == 1:
                ranges = [[int(r_size[0] / 2), 0], [2, 3, 0], []]  # Tutaj mapujemy na blok 1
            elif counter == 2:
                ranges = [[0, int(r_size[1] / 2)], [1, 0, 3], []]  # Tutaj mapujemy na blok 2
            elif counter == 3:
                ranges = [[int(r_size[0] / 2), int(r_size[1] / 2)], [0, 1, 2], []]  # Tutaj mapujemy na blok 3
            # Mapowanie współczynników
            # Krótki opis dla mnie :)
            # Musimy wiedzieć o ile przesunąć i i j żebyśmy mapowali z odpowiedniego kwadrata :matrix_d
            # damy to sobie jako ranges[2][0-2][0-1]
            for i in range(3):
                if (ranges[1][i]) == 0:
                    ranges[2].append([0, 0])
                if (ranges[1][i]) == 1:
                    ranges[2].append([int(r_size[0] / 2), 0])
                if (ranges[1][i]) == 2:
                    ranges[2].append([0, int(r_size[1] / 2)])
                if (ranges[1][i]) == 3:
                    ranges[2].append([int(r_size[0] / 2), int(r_size[1] / 2)])
            # x,y to wspolrzedne na ktore mapujemy, i,j to wspolrzedne z ktorych mapujemy
            for i in range(int(r_size[0] / 2)):
                for j in range(int(r_size[1] / 2)):
                    a = i + ranges[2][0][0]
                    b = j + ranges[2][0][1]
                    x = A_map[ranges[1][0]][i][j][0] + ranges[0][0]
                    y = A_map[ranges[1][0]][i][j][1] + ranges[0][1]

                    binary[x][y] = binwsp[a][b]
                    if (len(binary[x][y])) > self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"]:
                        self.print_("a")
                        sys.exit()
            # sys.exit()
            # Mapowanie bloków matrix_b
            for i in range(int(r_size[0] / 2)):
                for j in range(int(r_size[1] / 2)):
                    a = i + ranges[2][1][0]
                    b = j + ranges[2][1][1]
                    x = B_map[ranges[1][1]][i][j][0] + ranges[0][0]
                    y = B_map[ranges[1][1]][i][j][1] + ranges[0][1]
                    if binary[x][y] == None:
                        self.print_(str([x, y]))
                        self.print_(str([i, j]))
                        sys.exit()
                    binary[x][y] += coeff_b[a][b]
                    if (len(binary[x][y])) > self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] + \
                            self.config["profile"][self.config["profil"]]["bity"]["DCT1"]:
                        self.print_("b")
                        sys.exit()

            # Mapowanie bloków C
            for i in range(int(r_size[0] / 2)):
                for j in range(int(r_size[1] / 2)):
                    x = C_map[ranges[1][2]][i][j][0] + ranges[0][0]
                    y = C_map[ranges[1][2]][i][j][1] + ranges[0][1]
                    binary[x][y] += coeff_c[i + ranges[2][2][0]][j + ranges[2][2][1]]
                    if (len(binary[x][y])) > self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] + \
                            self.config["profile"][self.config["profil"]]["bity"]["DCT1"] + \
                            self.config["profile"][self.config["profil"]]["bity"]["DCT2"]:
                        self.print_("c")
                        sys.exit()

        self.print_("Zapisywanie danych w obrazku :)")
        for i in range(r_size[0]):
            for j in range(r_size[1]):
                matrix_r[i][j] = zapiszWiadomosc(matrix_r[i][j], binary[i][j])
                matrix_r[i][j] = zapiszWiadomosc(matrix_r[i][j], binary[i][j] + md5Bloku(matrix_r[i][j]))

        H = numpy.matrix(im.getdata()).reshape((im.size[1], im.size[0]))
        for i in range(r_size[0]):
            for j in range(r_size[1]):
                H[block_size * i:block_size * (i + 1), block_size * j:block_size * (j + 1)] = matrix_r[i][j]

        H = Image.fromarray(numpy.uint8(numpy.matrix(H)))  # Wyswietlanie obrazka, nie wiem jak dziala na windowsie
        H.show()

        H.save(self.destination_file)
        self.print_("Zapisano jako `%s`" % (self.destination_file))

    def check(self):
        """
		sprawdzanie znaku wodnego
		TODO: Komentarze
		"""

        self.statystyki = {
            "hash": {
                "dobrze": 0,
                "zle": 0,
            },
            "fraktal": {
                "dobrze": 0,
                "zle": 0,
                "nieznany": 0
            },
            "dct1": {
                "dobrze": 0,
                "zle": 0,
                "nieznany": 0
            },
            "dct2": {
                "dobrze": 0,
                "zle": 0,
                "nieznany": 0
            },
        }

        if self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] \
                + self.config["profile"][self.config["profil"]]["bity"]["DCT1"] \
                + self.config["profile"][self.config["profil"]]["bity"]["DCT2"] \
                + self.config["profile"][self.config["profil"]]["bity"]["hash"] > 128:
            self.print_("Za dużo bitów. Zmień ustawienia")
            return -1

        nazwa = self.source_file

        try:
            im = Image.open(nazwa)  # Odczytanie obrazu
        except IOError:
            self.print_("Wygląda na to że plik nie jest obrazkiem")
            return -1
        if not (im.mode == 'L'):
            self.print_("Inne rodzaje obrazu niż skala szarości, nie są jeszcze obsługiwane")
            return -1
        if im.size[0] % 8 or im.size[1] % 8:
            self.print_("Obrazy o wymiarach niepodzielnych przez 8 nie są obsługiwane")
            return -1
        self.print_("Rozpoczynamy sprawdzanie")

        if im.size[0] > im.size[1]:
            delta = int(im.size[0] / (2 ** self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["x"]))
        else:
            delta = int(im.size[1] / (2 ** self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["y"]))

        A = numpy.matrix(im.getdata()).reshape((im.size[1], im.size[0]))
        A2 = remove_2_lsb(A)[0]
        A2[0:128, 0:128] = 0
        A[0:128, 0:128] = 0
        B_ = rangeBlocks(przesunGora(A2.reshape([im.size[1], im.size[0]])), 8)
        B_wsp = code_dct_jpeg(B_, self)
        C_ = rangeBlocks(przesunLewo(A2.reshape([im.size[1], im.size[0]])), 8)
        C_wsp = code_dct_jpeg(C_, self)
        self.print_("Tworzenie rangeBloków 8x8")
        R = rangeBlocks(A, 8)

        w = [1, 1, 1, 1]
        R_size = (len(R), len(R[0]))
        binary = [[[None]] * R_size[1] for i in range(R_size[0])]
        A = [[[None]] * R_size[1] for i in range(R_size[0])]
        B = [[[None]] * R_size[1] for i in range(R_size[0])]
        C = [[[None]] * R_size[1] for i in range(R_size[0])]
        mk = [[[None]] * R_size[1] for i in range(R_size[0])]
        tamp1 = [[[None]] * 2 * R_size[1] for i in range(2 * R_size[0])]
        tamp2 = [[[None]] * 2 * R_size[1] for i in range(2 * R_size[0])]
        tamp3 = [[[None]] * 2 * R_size[1] for i in range(2 * R_size[0])]
        tamp4 = [[[None]] * 2 * R_size[1] for i in range(2 * R_size[0])]
        t = [[[None]] * 2 * R_size[1] for i in range(2 * R_size[0])]

        # Level1

        for i in range(R_size[0]):
            for j in range(R_size[1]):
                tmp = sprawdzmd5Bloku(R[i][j])
                R[i][j] = tmp[1]
                binary[i][j] = tmp[2]
                mk[i][j] = tmp[0]
                tamp1[2 * i][2 * j] = mk[i][j]
                tamp1[2 * i][2 * j + 1] = mk[i][j]
                tamp1[2 * i + 1][2 * j] = mk[i][j]
                tamp1[2 * i + 1][2 * j + 1] = mk[i][j]
                if mk[i][j] == -1:
                    self.statystyki["hash"]["zle"] += 1
                # self.print_("invalid hash")
                else:
                    self.statystyki["hash"]["dobrze"] += 1

        # R is original without 2LSB
        # Level2

        Maper = [124, 112, 18, 199, 255, 10, 123, 32, 96, 111, 67, 56, 43, 22, 34, 89, 102, 123, 11, 2, 5, 7, 192, 123,
                 253]

        # Tablice mapowania 4 wpisy w każdym wpis [i][j] w którym są współrzędne punktu na który mapujemy
        # I tak np. R[0][0] mapujemy na A_map[0][0][0]
        A_map = [getMapping(Maper[0:], [int(R_size[0] / 2), int(R_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(Maper[1:], [int(R_size[0] / 2), int(R_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(Maper[2:], [int(R_size[0] / 2), int(R_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(Maper[3:], [int(R_size[0] / 2), int(R_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30)]

        B_map = [getMapping(Maper[4:], [int(R_size[0] / 2), int(R_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(Maper[5:], [int(R_size[0] / 2), int(R_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(Maper[6:], [int(R_size[0] / 2), int(R_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(Maper[7:], [int(R_size[0] / 2), int(R_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30)]

        C_map = [getMapping(Maper[8:], [int(R_size[0] / 2), int(R_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(Maper[9:], [int(R_size[0] / 2), int(R_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(Maper[10:], [int(R_size[0] / 2), int(R_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30),
                 getMapping(Maper[11:], [int(R_size[0] / 2), int(R_size[1] / 2)],
                            str(self.config["profile"][self.config["profil"]]["haslo"]) * 30)]

        for counter in range(0, 4):
            # Ranges, to będą współczynniki przydatne prz pętlach
            if counter == 0:
                ranges = [[0, 0], [3, 2, 1], []]  # Tutaj mapujemy na blok 0
            elif counter == 1:
                ranges = [[int(R_size[0] / 2), 0], [2, 3, 0], []]  # Tutaj mapujemy na blok 1
            elif counter == 2:
                ranges = [[0, int(R_size[1] / 2)], [1, 0, 3], []]  # Tutaj mapujemy na blok 2
            elif counter == 3:
                ranges = [[int(R_size[0] / 2), int(R_size[1] / 2)], [0, 1, 2], []]  # Tutaj mapujemy na blok 3
            # Mapowanie współczynników
            # Krótki opis dla mnie :)
            # Musimy wiedzieć o ile przesunąć i i j żebyśmy mapowali z odpowiedniego kwadrata :D
            # damy to sobie jako ranges[2][0-2][0-1]
            for i in range(3):
                if (ranges[1][i]) == 0:
                    ranges[2].append([0, 0])
                if (ranges[1][i]) == 1:
                    ranges[2].append([int(R_size[0] / 2), 0])
                if (ranges[1][i]) == 2:
                    ranges[2].append([0, int(R_size[1] / 2)])
                if (ranges[1][i]) == 3:
                    ranges[2].append([int(R_size[0] / 2), int(R_size[1] / 2)])
            # x,y to wspolrzedne na ktore mapujemy, a,b to wspolrzedne z ktorych mapujemy
            self.print_("Level-2_%i" % (counter))
            for i in range(int(R_size[0] / 2)):
                for j in range(int(R_size[1] / 2)):
                    a = i + ranges[2][0][0]
                    b = j + ranges[2][0][1]
                    x = A_map[ranges[1][0]][i][j][0] + ranges[0][0]
                    y = A_map[ranges[1][0]][i][j][1] + ranges[0][1]
                    if mk[x][y] == 1:  # Sprawdzamy czy mapowany blok jest ok
                        # A[i + ranges[2][0][0]][j + ranges[2][0][1]] = binary[x][y][0:32]
                        A[a][b] = binariaToDec(binary[x][y], [
                            [self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["x"], 0],
                            [self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["y"], 0],
                            [self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["s"], 1],
                            [self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["o"], 1], [3, 0]])
                        A[a][b][0] *= delta
                        A[a][b][1] *= delta
                        A[a][b][2] *= zmienne["sMax"] / 2 ** (
                            self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["s"] - 1)
                        A[a][b][3] *= zmienne["oMax"] / 2 ** (
                            self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["o"] - 1)

                        if counter == 1 or counter == 3:
                            A[a][b][0] += im.size[1] / 2
                        if counter == 2 or counter == 3:
                            A[a][b][1] += im.size[0] / 2

                        if mk[int(A[a][b][0] / 8)][int(A[a][b][1] / 8)] == 1:  # Sprawdzamy czy domain blok jest ok
                            wsp2 = porownaj(R[a][b], przeksztalcenie(
                                skaluj(A2[A[a][b][0]:A[a][b][0] + 16, A[a][b][1]:A[a][b][1] + 16]), A[a][b][4]))

                            wsp2[0] = binariaToDec(intTobin(wsp2[0] / zmienne["sMax"] * 2 ** (
                                self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["s"] - 1),
                                                            self.config["profile"][self.config["profil"]]["bity"][
                                                                "fraktal"]["s"], 1), [[self.config["profile"][
                                                                                           self.config["profil"]][
                                                                                           "bity"]["fraktal"]["s"],
                                                                                       1]])[0] * zmienne[
                                          "sMax"] / 2 ** (
                                self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["s"] - 1)
                            wsp2[1] = binariaToDec(intTobin(wsp2[1] / zmienne["oMax"] * 2 ** (
                                self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["o"] - 1),
                                                            self.config["profile"][self.config["profil"]]["bity"][
                                                                "fraktal"]["o"], 1), [[self.config["profile"][
                                                                                           self.config["profil"]][
                                                                                           "bity"]["fraktal"]["o"],
                                                                                       1]])[0] * zmienne[
                                          "oMax"] / 2 ** (
                                self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["o"] - 1)
                            if A[a][b][2] != wsp2[0] or A[a][b][3] != wsp2[1]:
                                self.print_(str(wsp2) + str(A[a][b]))
                                tmp = -1
                                self.statystyki["fraktal"]["zle"] += 1

                            else:
                                self.statystyki["fraktal"]["dobrze"] += 1
                                tmp = 1
                                # self.print_("Aij jest valid")
                        else:
                            self.statystyki["fraktal"]["nieznany"] += 1
                            tmp = 0
                            # self.print_("Aij is undefined")
                    else:
                        self.statystyki["fraktal"]["nieznany"] += 1
                        # self.print_(a,b, x, y)
                        tmp = 0
                    # self.print_("Aij is undefined")

                    A[a][b] = [tmp, A[a][b]]
                    tamp2[2 * x][2 * y] = tmp
                    tamp2[2 * x][2 * y + 1] = tmp
                    tamp2[2 * x + 1][2 * y] = tmp
                    tamp2[2 * x + 1][2 * y + 1] = tmp

            self.print_("Level-3_%i" % (counter))
            # Mapowanie bloków B
            for i in range(int(R_size[0] / 2)):
                for j in range(int(R_size[1] / 2)):
                    a = i + ranges[2][1][0]
                    b = j + ranges[2][1][1]
                    x = B_map[ranges[1][1]][i][j][0] + ranges[0][0]
                    y = B_map[ranges[1][1]][i][j][1] + ranges[0][1]

                    if mk[x][y] == 1:  # Sprawdzamy czy mapowany blok jest ok
                        # self.print_(B_wsp[a][b])
                        # self.print_(binary[x][y][32:72])
                        if binary[x][y][self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"]:
                                self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] +
                                self.config["profile"][self.config["profil"]]["bity"]["DCT1"]] == B_wsp[a][b]:
                            tmp = 1
                            self.statystyki["dct1"]["dobrze"] += 1
                        else:
                            self.statystyki["dct1"]["zle"] += 1
                            tmp = -1
                    else:
                        self.statystyki["dct1"]["nieznany"] += 1
                        tmp = 0

                    B[a][b] = [tmp, [x, y]]
                    tamp3[(2 * x + 1) % (2 * R_size[0])][2 * y] = tmp
                    tamp3[(2 * x + 1) % (2 * R_size[0])][2 * y + 1] = tmp
                    tamp3[(2 * x + 2) % (2 * R_size[0])][2 * y] = tmp
                    tamp3[(2 * x + 2) % (2 * R_size[0])][2 * y + 1] = tmp

            self.print_("Level-4_%i" % (counter))
            # Mapowanie bloków C
            for i in range(int(R_size[0] / 2)):
                for j in range(int(R_size[1] / 2)):
                    a = i + ranges[2][2][0]
                    b = j + ranges[2][2][1]
                    x = C_map[ranges[1][2]][i][j][0] + ranges[0][0]
                    y = C_map[ranges[1][2]][i][j][1] + ranges[0][1]

                    if mk[x][y] == 1:  # Sprawdzamy czy mapowany blok jest ok
                        if binary[x][y][self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] +
                                self.config["profile"][self.config["profil"]]["bity"]["DCT1"]:
                                        self.config["profile"][self.config["profil"]]["bity"]["fraktal"]["suma"] +
                                        self.config["profile"][self.config["profil"]]["bity"]["DCT1"] +
                                self.config["profile"][self.config["profil"]]["bity"]["DCT2"]] == C_wsp[a][b]:
                            tmp = 1
                            self.statystyki["dct2"]["dobrze"] += 1
                        else:
                            self.statystyki["dct2"]["zle"] += 1
                            tmp = -1
                    else:
                        self.statystyki["dct2"]["nieznany"] += 1
                        tmp = 0

                    C[a][b] = [tmp, [x, y]]
                    tamp4[2 * x][(2 * y + 1) % (2 * R_size[1])] = tmp
                    tamp4[2 * x][(2 * y + 2) % (2 * R_size[1])] = tmp
                    tamp4[2 * x + 1][(2 * y + 1) % (2 * R_size[1])] = tmp
                    tamp4[2 * x + 1][(2 * y + 2) % (2 * R_size[1])] = tmp

        self.print_("Sklejanie")
        for i in range(2 * R_size[0]):
            for j in range(2 * R_size[1]):
                t[i][j] = w[0] * tamp1[i][j] + w[1] * tamp2[i][j] + w[2] * tamp3[i][j] + w[3] * tamp4[i][j]

        for i in range(R_size[0]):
            for j in range(R_size[1]):
                A[i][j].append(0)
                if A[i][j][0] < 0:
                    x = A[i][j][1][0]
                    y = A[i][j][1][1]
                    if mk[int(x / 8)][int(y / 8)] >= 0 \
                            and mk[int(x / 8) + 1][int(y / 8)] >= 0 \
                            and mk[int(x / 8) + 1][int(y / 8) + 1] >= 0 \
                            and mk[int(x / 8)][int(y / 8) + 1] >= 0:
                        R[i][j] = DekompresujPojedynczy(przeksztalcenie(skaluj(A2[x:x + 16, y:y + 16]), A[i][j][1][4]),
                                                        A[i][j][1][2], A[i][j][1][3])
                        A[i][j][2] = 1
                    else:
                        A[i][j][2] = -1

        for i in range(R_size[0]):
            for j in range(R_size[1]):
                B[i][j].append(0)
                if B[i][j][0] < 0:
                    x = B[i][j][1][0]
                    y = B[i][j][1][1]
                    if mk[x][y] == 1:
                        B_[i][j] = dekodujDCT(dekodujWspDCT(binary[x][y][
                                                            self.config["profile"][self.config["profil"]]["bity"][
                                                                "fraktal"]["suma"]:
                                                            self.config["profile"][self.config["profil"]]["bity"][
                                                                "fraktal"]["suma"] +
                                                            self.config["profile"][self.config["profil"]]["bity"][
                                                                "DCT1"]], 6, self))
                        B[i][j][2] = 1
                    else:
                        B_[i][j] *= 0
                        B[i][j][2] = -1

        for i in range(R_size[0]):
            for j in range(R_size[1]):
                C[i][j].append(0)
                if C[i][j][0] < 0:
                    x = C[i][j][1][0]
                    y = C[i][j][1][1]
                    if mk[x][y] == 1:
                        C_[i][j] = dekodujDCT(dekodujWspDCT(binary[x][y][
                                                            self.config["profile"][self.config["profil"]]["bity"][
                                                                "fraktal"]["suma"] +
                                                            self.config["profile"][self.config["profil"]]["bity"][
                                                                "DCT1"]:
                                                            self.config["profile"][self.config["profil"]]["bity"][
                                                                "fraktal"]["suma"] +
                                                            self.config["profile"][self.config["profil"]]["bity"][
                                                                "DCT1"] +
                                                            self.config["profile"][self.config["profil"]]["bity"][
                                                                "DCT2"]], 6, self))
                        C[i][j][2] = 1
                    else:
                        C_[i][j] *= 0
                        C[i][j][2] = -1

        H = numpy.matrix(im.getdata()).reshape((im.size[1], im.size[0]))
        for i in range(R_size[0]):
            for j in range(R_size[1]):
                H[8 * i:8 * i + 8, 8 * j:8 * j + 8] = C_[i][j]

        H_C = przesunLewo(H, H.shape[1] - 4)
        G = Image.fromarray(numpy.uint8(numpy.matrix(H_C)))	#Wyswietlanie obrazka, nie wiem jak dziala na windowsie
        G.show()
        G.save(nazwa + "Recover_C.pgm")

        H = numpy.matrix(im.getdata()).reshape((im.size[1], im.size[0]))
        for i in range(R_size[0]):
            for j in range(R_size[1]):
                H[8 * i:8 * i + 8, 8 * j:8 * j + 8] = B_[i][j]

        H_B = przesunGora(H, H.shape[0] - 4)
        G = Image.fromarray(numpy.uint8(numpy.matrix(H_B)))	#Wyswietlanie obrazka, nie wiem jak dziala na windowsie
        G.show()
        G.save(nazwa + "Recover_B.pgm")

        H = numpy.matrix(im.getdata()).reshape((im.size[1], im.size[0]))
        for i in range(R_size[0]):
            for j in range(R_size[1]):
                H[8 * i:8 * i + 8, 8 * j:8 * j + 8] = R[i][j]

        H_A = H
        G = Image.fromarray(numpy.uint8(numpy.matrix(H_A)))	#Wyswietlanie obrazka, nie wiem jak dziala na windowsie
        G.show()
        G.save(nazwa + "Recover_A.pgm")



        for i in range(im.size[1]):
            for j in range(im.size[0]):
                if mk[int(i / 8)][int(j / 8)] < 1:
                    betas = []

                    if A[int(i / 8)][int(j / 8)][2] > 0:
                        betas.append(1)
                    else:
                        betas.append(0)

                    if B[int(((i - 4) % im.size[1]) / 8)][int(j / 8)][2] > 0:
                        betas.append(2)
                    else:
                        betas.append(0)

                    if C[int(i / 8)][int(((j - 4) % im.size[0]) / 8)][2] > 0:
                        betas.append(2)
                    else:
                        betas.append(0)

                    # self.print_(i, j, betas)
                    if (sum(betas) > 0):
                        H[i, j] = (betas[0] * H_A[i, j] + betas[1] * H_B[i, j] + betas[2] * H_C[i, j]) / (
                            betas[0] + betas[1] + betas[2])
                    if (sum(betas) == 3):
                        try:
                            t[math.floor(i / 4)][math.floor(j / 4)] = 1
                        except IndexError:
                            pass
                        try:
                            t[math.floor(i / 4) + 1][math.floor(j / 4)] = 1
                        except IndexError:
                            pass
                        try:
                            t[math.floor(i / 4) + 1][math.floor(j / 4) + 1] = 1
                        except IndexError:
                            pass
                        try:
                            t[math.floor(i / 4)][math.floor(j / 4) + 1] = 1
                        except IndexError:
                            pass

        for a in range(10):
            self.progress(a, 100)
            for i in range(1, len(t) - 1):
                for j in range(1, len(t[0]) - 1):
                    if t[i][j] <= 0:
                        licznik = 0
                        suma = numpy.matrix(H[0:4, 0:4]) * 0
                        if t[i - 1][j - 1] > 0:
                            licznik += 1
                            suma += H[(i - 1) * 4:(i) * 4, (j - 1) * 4:(j) * 4]
                        if t[i - 1][j] > 0:
                            licznik += 1
                            suma += H[(i - 1) * 4:(i) * 4, j * 4:(j + 1) * 4]
                        if t[i - 1][j + 1] > 0:
                            licznik += 1
                            suma += H[(i - 1) * 4:(i) * 4, (j + 1) * 4:(j + 2) * 4]
                        if t[i][j - 1] > 0:
                            licznik += 1
                            suma += H[i * 4:(i + 1) * 4, (j - 1) * 4:(j) * 4]
                        if t[i][j + 1] > 0:
                            licznik += 1
                            suma += H[i * 4:(i + 1) * 4, (j + 1) * 4:(j + 2) * 4]
                        if t[i + 1][j - 1] > 0:
                            licznik += 1
                            suma += H[(i + 1) * 4:(i + 2) * 4, (j - 1) * 4:(j) * 4]
                        if t[i + 1][j] > 0:
                            licznik += 1
                            suma += H[(i + 1) * 4:(i + 2) * 4, j * 4:(j + 1) * 4]
                        if t[i + 1][j + 1] > 0:
                            licznik += 1
                            suma += H[i * 4:(i + 1) * 4, (j + 1) * 4:(j + 2) * 4]
                        if licznik > 3:
                            # for z in range(20):
                            if a % 2 != 0:
                                H[i * 4:(i + 1) * 4, j * 4:(j + 1) * 4] = suma / licznik
                            elif a > 0:
                                # if a>10:
                                t[i][j] += 1
        self.progress(1, 1)
        self.print_("")
        H = Image.fromarray(numpy.uint8(numpy.matrix(H)))  # Wyswietlanie obrazka, nie wiem jak dziala na windowsie

        H.save(self.destination_file)
        self.print_("Zapisano jako `%s`" % (self.destination_file))

        self.source_file = ""
        self.destination_file = ""
        print(str(self.statystyki))

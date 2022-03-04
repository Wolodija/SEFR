#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Graficzna aplikacja SEFR:
Autorzy: Dominik Rosiek & Piotr Ścibor
"""
print("Importowanie bibliotek");
from gui import *
print("Biblioteki zaimportowano")

def main():
    numpy.set_printoptions(threshold= 10e40)
    app = QtWidgets.QApplication(sys.argv)
    Ap = SEFR_GUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()   
 

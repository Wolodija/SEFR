#!/usr/bin/python3.3
import os;
import sys;
from subprocess import *
from PIL import Image      #Moduł do przetwarzania obrazów
os.system("./main.py lena/lena.pgm lena/out.pgm znak")
os.system(">lena%s.txt" %sys.argv[1])
ile = int(sys.argv[1])
for i in range(ile+1):
  print(i)
  im = Image.open("lena/out.pgm")
  data = list(im.getdata())
  for j in range(int(256*256/ile*i)):
    data[j] = 0;
  newimg = Image.new("L", im.size)
  newimg.putdata(data)

  newimg.save("lena/out2.pgm")
  os.system("./main.py lena/out2.pgm lena/out2.pgm recover")
  os.popen("compare -metric PSNR lena/lena.pgm lena/out2.pgm lena/diff%s.pgm 2>> lena%s.txt" %(i, sys.argv[1])).readlines();
sudo aptitude update
sudo aptitude install python3 libtiff4-dev libjpeg8-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.5-dev tk8.5-dev \
    python-tk python3-dev python3-setuptools python3-scipy \
    python3-numpy python3-pyqt4 -y

wget https://pypi.python.org/packages/source/P/Pillow/Pillow-2.4.0.zip#md5=b46ac9f00580920ffafe518bc765e43c
unzip Pillow-2.4.0.zip
cd Pillow-2.4.0
sudo python3 setup.py install
cd ../
sudo rm -rf Pillow-2.4.0*

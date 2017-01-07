echo AWGN 0.5
compare -metric PSNR Big/awgn.pgm awgn0.5.pgm out.pgm
echo
compare -metric PSNR Big/awgn.pgm Big/awgnout_0.5.pgm out.pgm
echo

echo AWGN 1
compare -metric PSNR Big/awgn.pgm awgn1.pgm out.pgm
echo
compare -metric PSNR Big/awgn.pgm Big/awgnout_1.pgm out.pgm
echo

echo AWGN 5
compare -metric PSNR Big/awgn.pgm awgn5.pgm out.pgm
echo
compare -metric PSNR Big/awgn.pgm Big/awgnout_5.pgm out.pgm
echo

echo Quad_1
compare -metric PSNR Big/awgn.pgm quad_1.pgm out.pgm
echo
compare -metric PSNR Big/awgn.pgm Big/quad_1.pgm out.pgm
echo

echo Quad_2
compare -metric PSNR Big/awgn.pgm quad_2.pgm out.pgm
echo
compare -metric PSNR Big/awgn.pgm Big/quad_2.pgm out.pgm
echo

echo Quad_3
compare -metric PSNR Big/awgn.pgm quad_3.pgm out.pgm
echo
compare -metric PSNR Big/awgn.pgm Big/quad_3.pgm out.pgm
echo

echo Quad_4
compare -metric PSNR Big/awgn.pgm quad_4.pgm out.pgm
echo
compare -metric PSNR Big/awgn.pgm Big/quad_4.pgm out.pgm
echo

echo Quad_all
compare -metric PSNR Big/awgn.pgm quad_all.pgm out.pgm
echo
compare -metric PSNR Big/awgn.pgm Big/quad_all.pgm out.pgm
echo

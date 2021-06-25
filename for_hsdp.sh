#!/bin/sh

# one way
\rm *oceanload* *bodyload* *.oceantotal *.bodytotal *.total Hilo.strain
#########
../bin/polymake << EOF > poly.tmp
- osu.hawaii.2010 
EOF
for n in m2 k1 o1 s2 
do 
../bin/nloadf Hilo 19.7241 -155.0868 0 ../tidmod/$n.osu.tpxo72.2010 ../green/gr.gbocen.wef.p01.cm l poly.tmp > $n.oceanloadglobal
../bin/nloadf Hilo 19.7241 -155.0868 0 ../tidmod/$n.osu.hawaii.2010 ../green/gr.gbocen.wef.p01.cm l poly.tmp + > $n.oceanloadlocal
cat $n.oceanloadglobal $n.oceanloadlocal | ../bin/loadcomb c > $n.oceantotal
cat $n.oceantotal | ../bin/loadcomb b > $n.bodytotal
if [ $n == m2 ]; then
	cp $n.bodytotal tmp
else
	cat all.bodyload $n.bodytotal > tmp
fi
mv tmp all.bodyload
if [ $n == m2 ]; then
	cp $n.oceantotal tmp
else
	cat all.oceanload $n.oceantotal > tmp
fi
mv tmp all.oceanload
done
\rm *oceanloadglobal *oceanloadlocal *oceantotal *bodytotal
#########

cat all.bodyload | ../bin/harprp l 0 | ../bin/hartid 2006 5 1 0 0 0 17520 900 > bodyload.strain.0
cat all.bodyload | ../bin/harprp l 90 | ../bin/hartid 2006 5 1 0 0 0 17520 900 > bodyload.strain.90
cat all.oceanload | ../bin/harprp l 0 | ../bin/hartid 2006 5 1 0 0 0 17520 900 > oceanload.strain.0
cat all.oceanload | ../bin/harprp l 90 | ../bin/hartid 2006 5 1 0 0 0 17520 900 > oceanload.strain.90

paste bodyload.strain.90 oceanload.strain.90 oceanload.strain.0 bodyload.strain.0 | awk '{print $1+$2, $3+$4}' > Hilo.strain
cp Hilo.strain ~/Documents/hawaii_permeability/

### borehole location 

# one way
\rm *oceanload* *bodyload* *.oceantotal *.bodytotal *.total Hilo.strain
#########
../bin/polymake << EOF > poly.tmp
- osu.hawaii.2010 
EOF
for n in m2 k1 o1 s2 
do 
../bin/nloadf BH 19.7127777777777777 -155.05416666666666667 0 ../tidmod/$n.osu.tpxo72.2010 ../green/gr.gbocen.wef.p01.cm l poly.tmp > $n.oceanloadglobal
../bin/nloadf BH 19.7127777777777777 -155.05416666666666667 0 ../tidmod/$n.osu.hawaii.2010 ../green/gr.gbocen.wef.p01.cm l poly.tmp + > $n.oceanloadlocal
cat $n.oceanloadglobal $n.oceanloadlocal | ../bin/loadcomb c > $n.oceantotal
cat $n.oceantotal | ../bin/loadcomb b > $n.bodytotal
if [ $n == m2 ]; then
	cp $n.bodytotal tmp
else
	cat all.bodyload $n.bodytotal > tmp
fi
mv tmp all.bodyload
if [ $n == m2 ]; then
	cp $n.oceantotal tmp
else
	cat all.oceanload $n.oceantotal > tmp
fi
mv tmp all.oceanload
done
\rm *oceanloadglobal *oceanloadlocal *oceantotal *bodytotal
#########

cat all.bodyload | ../bin/harprp l 0 | ../bin/hartid 2006 5 1 0 0 0 17520 900 > bodyload.strain.0
cat all.bodyload | ../bin/harprp l 90 | ../bin/hartid 2006 5 1 0 0 0 17520 900 > bodyload.strain.90
cat all.oceanload | ../bin/harprp l 0 | ../bin/hartid 2006 5 1 0 0 0 17520 900 > oceanload.strain.0
cat all.oceanload | ../bin/harprp l 90 | ../bin/hartid 2006 5 1 0 0 0 17520 900 > oceanload.strain.90

paste bodyload.strain.90 oceanload.strain.90 oceanload.strain.0 bodyload.strain.0 | awk '{print $1+$2, $3+$4}' > BH.strain
cp BH.strain ~/Documents/hawaii_permeability/

# the other way
#../bin/ertid <<EOF 
#2006 121 0 
#2006 121 23.75 
#0.25
#t 
#19.7241 
#-155.0868
#0 
#0 
#2
#0
#90
#azi1
#azi2
#EOF
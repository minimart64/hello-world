#! /bin/bash

# count of files in ~/Documents/Photos
# loop to repeat cnee call that many times
# cnee creates the puzzles
# jigidize then adds the new puzzle codes to the list
# this one creates private puzzles

cd ~/Documents/Photos
declare -i count; count=0
for i in $(ls); do
mv $i ~/Documents/cneeing/
cnee --replay --file ~/Documents/git/Jigidize/cneeScript.xns -force-core-replay
mv ~/Documents/cneeing/$i ~/Documents/cneed/
count+=1
echo $count
done

echo "Jigidizing"
~/Documents/git/Jigidize/jigidize.py -x $count

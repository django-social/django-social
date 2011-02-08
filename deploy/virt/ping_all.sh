for S in `seq 1 20` 
do
S3=`printf '%03d' $S`
ping -c 4 s$S3.lan
done

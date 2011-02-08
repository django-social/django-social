for S in `seq 1 20` 
do
S3=`printf '%03d' $S`
virsh --connect qemu:///system start s$S3 
done

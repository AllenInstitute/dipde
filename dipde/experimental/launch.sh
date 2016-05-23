
export NUMBER_OF_NODES=2

for ii in $(seq 0 $((NUMBER_OF_NODES-1)))
do
	python $1 $ii &
done

wait
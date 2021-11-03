
for step in {2..8}; do
    limit=$((10 ** $step))

    for thread in 1 2 4 8; do
        for i in {1..10}; do
            python3 main.py $thread $limit

            sleep 1
        done
    done
done
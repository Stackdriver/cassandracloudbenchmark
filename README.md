#Setup:
1. Authorize port 7000, 7199, 9160 for cassandra group
2. Authorize port 22 for client
3. Launch 4 m1.xlarge or n1-standard-4-d 
    - (NOTE: Only tested on ami-973db5fe and centos-6-v20130522 using scratch disk as boot volume)
4. Fill out benchmark.conf with internal/external IPs of hosts launched
5. Run ./bootstrap
6. Run ./run_benchmark
7. Summarized results will be in ./results
8. Raw results will be in ./cassandra.xxxx

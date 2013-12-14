#!/bin/bash
# Boostrap a Cassandra Node Using Puppet on CentOS6

# The node to use for bootstrapping Cassandra clients into the cluster.
SEED_NODE=$1

mkdir /cassandra_data

# Format a 2nd disk (if available) to mount on /cassandra_data for sstables
# aws standard for m1.xlarge
if [ -b /dev/xvdf ]; then
  umount /dev/xvdf
  /sbin/mkfs.ext4 -E lazy_itable_init=0 /dev/xvdf
  mount -o noatime /dev/xvdf /cassandra_data
# gce default for n-standard-4-d
elif [ -b /dev/sdb ]; then
  echo "n
p
1
1
+300G
w
" | /sbin/fdisk /dev/sdb
  umount /dev/sdb1
  /sbin/mkfs.ext4 -E lazy_itable_init=0 /dev/sdb1
  mount -o noatime /dev/sdb1 /cassandra_data
fi

chmod 777 /cassandra_data

# Bootstrap the Node
/usr/bin/puppet apply --verbose -e "class {'cassandra': cassandra_seed_node => '$SEED_NODE' }"

# Wait for Cassandra to finish bootstrapping into the cluster
status=""
while [ "$status" != "NORMAL" ]; do
  sleep 5
  status=`/usr/bin/nodetool netstats |awk /^Mode:/'{print $2}'`
  echo "Waiting for status NORMAL"
  echo "Status is: $status"
done

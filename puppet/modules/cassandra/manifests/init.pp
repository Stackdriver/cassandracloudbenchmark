# == Class: cassandra
#
#  Installs and configures Cassandra for the Cassandra Cloud Benchmark
#
# === Parameters
#
#   $cassandra_seed_node - Node to connect to for bootstraping into the cluster.
#
# === Examples
#
#   class { 'cassandra': }
#
# === Authors
#
# * Joey Imbasciano <joey@stackdriver.com>
#
class cassandra($cassandra_seed_node = undef) {
    include cassandra::service
}

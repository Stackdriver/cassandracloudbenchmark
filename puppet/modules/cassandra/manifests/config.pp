# == Class: cassandra::config
#
#  Configures Cassandra for the Cassandra Cloud Benchmark
#
# === Parameters
#
#   None
#
# === Examples
#
#   class { 'cassandra::config': }
#
# === Authors
#
# * Joey Imbasciano <joey@stackdriver.com>
#
class cassandra::config {
    include cassandra::package
    
    $initial_seed = $cassandra::cassandra_seed_node
    file { "cassandra-config":
        path    => '/etc/cassandra/conf/cassandra.yaml',
        content => template('cassandra/cassandra.yaml.erb'),
        mode    => 755,
        owner   => cassandra,
        group   => cassandra,
        require => Class['cassandra::package'],
    }
}

# == Class: cassandra::service
#
#   Starts the Cassandra service
#
# === Parameters
#
#   None
#
# === Examples
#
#   class { 'cassandra::service': }
#
# === Authors
#
# * Joey Imbasciano <joey@stackdriver.com>
#
class cassandra::service {
    include cassandra::package
    include cassandra::config

    service { "cassandra":
        enable  => true,
        ensure  => running,
        # The init script for Cassandra is broken and doesn't return the 
        # correct status when stopped/started.
        hasstatus => false,
        status    => 'ps -U cassandra -u cassandra -f |egrep "org.apache.cassandra.service.CassandraDaemon$"',
        require => Class['cassandra::config'],
    }
}

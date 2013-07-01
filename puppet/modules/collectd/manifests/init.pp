# == Class: collectd
#
#  Installs and configures collectd
#
# === Parameters
#
#   None
#
# === Examples
#
#   class { 'collectd': }
#
# === Authors
#
# * Joey Imbasciano <joey@stackdriver.com>
#
class collectd {
    package { "collectd":
        ensure => installed,
    }
    file { "collectd-benchmark.conf":
        path    => "/etc/collectd.d/collectd-benchmark.conf",
        source  => "puppet:///modules/collectd/collectd-benchmark.conf",
        require => Package['collectd'],
        notify  => Service['collectd'],
    }
    service { "collectd":
        enable  => true,
        ensure  => running,
        require => [ Package['collectd'], File['collectd-benchmark.conf'] ],
    }
}

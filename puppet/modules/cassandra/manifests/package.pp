# == Class: cassandra::package
#
#  Installs Cassandra based on Datastax recommended installation:
#     http://www.datastax.com/docs/1.2/install/install_rpm
#
# === Parameters
#
#   None
#
# === Examples
#
#   class { 'cassandra::package': }
#
# === Authors
#
# * Joey Imbasciano <joey@stackdriver.com>
#
class cassandra::package {
    include cassandra::java
    include cassandra::repo

    package { "jna":
        ensure => installed,
    }

    package { "dsc12":
        ensure  => "1.2.11-1",
        notify  => Exec["update-java-priorities"],
        require => [ Class["cassandra::repo"], Class["cassandra::java"], Package["jna"] ],
    }

    # Both JNA and DSC pull in versions of java which mess with the system java.
    # After installing cassandra, ensure the alternatives are set correctly.
    # This will use the highest priority java available in alternatives. Which
    # in our case should be SunJava6.
    exec { "update-java-priorities":
        require     => Package["dsc12"],
        command     => "/usr/sbin/alternatives --auto java",
        refreshonly => true,
    }
}

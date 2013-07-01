# == Class: cassandra::java
#
#   Installs SunJava JRE 1.6 for use with this Cassandra benchmark.
#
# === Parameters
#
#   None
#
# === Examples
#
#   class { 'cassandra::java': }
#
# === Authors
#
# * Joey Imbasciano <joey@stackdriver.com>
#
class cassandra::java {
    $sunjava_pkg      = "jre-6u45-linux-amd64.rpm"
    $sunjava_version  = "jre1.6.0_45"
    $sunjava_src_url  = "https://s3.amazonaws.com/cassandracloudbenchmark/rpms"
    $sunjava_priority = "20000"

    package { "jre":
        ensure   => installed,
        provider => rpm,
        source   => "$sunjava_src_url/$sunjava_pkg",
        notify   => Exec["install-sun-java"],
    }

    exec { "install-sun-java":
        require     => Package["jre"],
        command     => "/usr/sbin/alternatives --install /usr/bin/java java /usr/java/$sunjava_version/bin/java $sunjava_priority",
        refreshonly => true,
    }
}

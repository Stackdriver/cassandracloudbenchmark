# == Class: cassandra::repo
#
#   Install the Datastax Cassandra repository.
#
# === Parameters
#
#   None
#
# === Examples
#
#   class { 'cassandra::repo': }
#
# === Authors
#
# * Joey Imbasciano <joey@stackdriver.com>
#
class cassandra::repo {
    
   yumrepo { "datastax-repo":
        baseurl    => "http://rpm.datastax.com/community",
        descr      => "DataStax Repo for Apache Cassandra",
        enabled    => "1",
        gpgcheck   => "0",
    }
}

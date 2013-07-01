# == Class: summarizer
#
#  Installs dependencies for the collectd summarizer
#
# === Parameters
#
#   None
#
# === Examples
#
#   class { 'summarizer': }
#
# === Authors
#
# * Joey Imbasciano <joey@stackdriver.com>
#
class summarizer {

    # Puppet doesn't support groupinstall yet :)
    # http://projects.puppetlabs.com/issues/5175
    exec { "groupinstall-devtools":
      unless  => '/usr/bin/yum grouplist "Development tools" | /bin/grep "^Installed Groups"',
      command => '/usr/bin/yum -y groupinstall "Development tools"',
      timeout => 1200,
    }
    package { "python-devel":
        ensure => installed,
    }
    package { "python-pip":
        ensure => installed,
    }
    exec { "install-numpy":
        require => [ Exec['groupinstall-devtools'], Package['python-devel'], Package['python-pip'] ],
        command => "/usr/bin/python-pip install numpy==1.7.1",
        unless  => "/usr/bin/python-pip freeze |grep numpy==1.7.1",
        timeout => 1200,
    }

    package { "python-argparse":
        ensure => installed,
    }
}

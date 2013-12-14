#!/bin/bash
# Install EPEL, Puppet, and Collectd

# Install our puppet code
rm -rf /etc/puppet
/bin/mv /tmp/puppet /etc/puppet

# EPEL Repo
/bin/rpm -q epel-release || /bin/rpm -Uvh http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm

# Puppet Repo
/bin/rpm -q puppetlabs-release || /bin/rpm -ivh http://yum.puppetlabs.com/el/6/products/i386/puppetlabs-release-6-7.noarch.rpm

# Install Puppet
/bin/rpm -q puppet || /usr/bin/yum install -y puppet

# Clear the iptables rules, security groups are enough for benchmarks.
/sbin/iptables -F

# Install collectd
/usr/bin/puppet apply --verbose -e "include ::collectd"

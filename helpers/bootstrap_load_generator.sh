#!/bin/bash
/usr/bin/puppet apply --verbose -e "include cassandra::package"
/usr/bin/puppet apply --verbose -e "include ::summarizer"

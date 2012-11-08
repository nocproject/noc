#!/usr/bin/perl

# SHJS - Syntax Highlighting in JavaScript
# Copyright (C) 2007, 2008 gnombat@users.sourceforge.net
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

use strict;
use warnings;

use SourceHighlight::JavaScript;

sub usage() {
  die "Usage: sh2js.pl FILE.lang\n";
}

################################################################################
# main

if (not @ARGV) {
  usage();
}

foreach (@ARGV) {
  if ($_ eq '-h' or $_ eq '-help' or $_ eq '--help') {
    usage();
  }
}

SourceHighlight::JavaScript::sh2js($ARGV[0]);

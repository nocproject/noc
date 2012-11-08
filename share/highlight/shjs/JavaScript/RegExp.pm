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

package JavaScript::RegExp;

use strict;
use warnings;

use fields qw(_source _flags);

sub to_string {
  my JavaScript::RegExp $self = shift;
  my $source = $self->{_source};
  $source =~ s|/|\\/|g;
  my $flags = $self->{_flags};
  return "/$source/$flags";
}

use overload '""' => \&to_string;

sub new {
  my $class = shift;
  my $source = shift;
  my $flags = shift;

  my JavaScript::RegExp $self = fields::new($class);
  $self->{_source} = $source;
  $self->{_flags} = $flags;
  return $self;
}

1;

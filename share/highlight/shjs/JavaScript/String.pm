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

package JavaScript::String;

use strict;
use warnings;

use fields qw(_value);

sub to_string {
  my JavaScript::String $self = shift;
  return "'" . $self->{_value} . "'";
}

use overload '""' => \&to_string;

sub new {
  my $class = shift;
  my $value = shift;

  my JavaScript::String $self = fields::new($class);
  $self->{_value} = $value;
  return $self;
}

1;

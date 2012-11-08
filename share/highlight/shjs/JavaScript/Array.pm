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

package JavaScript::Array;

use strict;
use warnings;

use fields qw(_value);

sub to_string {
  my JavaScript::Array $self = shift;
  my $array = $self->{_value};
  my $result = '[';
  my $first = 1;
  foreach my $elem (@$array) {
    if ($first) {
      $first = 0;
    }
    else {
      $result .= ', ';
    }
    $result .= "'" . $elem . "'";
  }
  $result .= ']';
  return $result;
}

use overload '""' => \&to_string;

sub new {
  my $class = shift;
  my $value = shift;

  my JavaScript::Array $self = fields::new($class);
  $self->{_value} = $value;
  return $self;
}

1;

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

package Regex::Boost;

use strict;
use warnings;

# there are 95 printable characters: 52 letters, 10 numbers, 1 space
# 95 - 52 - 10 - 1 = 32 punctuation!
my $ALNUM = 'A-Za-z0-9';
my $PUNCT = '`~!@#$%&*()_=+{}|;:",<.>/?\'\\\[\]\^\-';
my $GRAPH = $ALNUM . $PUNCT;
my $PRINT = $GRAPH . ' ';

my %CHARACTER_CLASS_NAME_TRANSLATIONS = (
  alnum => $ALNUM,
  alpha => 'A-Za-z',
#  ascii =>
  blank => ' \t',
#  cntrl
  d => '\d',
  digit => '\d',
  graph => $GRAPH,
  l => 'a-z',
  lower => 'a-z',
  print => $PRINT,
  punct => $PUNCT,
  s => '\s',
  space => '\s',
  u => 'A-Z',
  upper => 'A-Z',
  w => 'A-Za-z0-9_',
  word => 'A-Za-z0-9_',
  xdigit => 'A-Fa-f0-9',
);

sub serialize(\@) {
  my $tokens = shift;
  my $result = '';
  foreach my $token (@$tokens) {
    if (ref $token) {
      foreach my $character (@$token) {
        if ($character =~ m/^\[:([a-z]+):\]$/) {
          $result .= $CHARACTER_CLASS_NAME_TRANSLATIONS{$1};
        }
        else {
          $result .= $character;
        }
      }
    }
    else {
      if ($token eq '(?<=' or $token eq '(?<!') {
        # JavaScript doesn't support lookbehind
        return undef;
      }
      elsif ($token eq '\<' or $token eq '\>') {
        $result .= '\b';
      }
      elsif ($token eq '\A') {
        $result .= '^';
      }
      elsif ($token eq '\z' or $token eq '\Z') {
        $result .= '$';
      }
      else {
        $result .= $token;
      }
    }
  }
  return $result;
}

sub backslash_token(\$) {
  my $regex = shift;
  if (${$regex} =~ m/\G(c.)/gc) {
    return "\\$1";
  }
  elsif (${$regex} =~ m/\G(x\d\d)/gc) {
    return "\\$1";
  }
  elsif (${$regex} =~ m/\G(x\{\d{4}\})/gc) {
    return "\\$1";
  }
  elsif (${$regex} =~ m/\G(0\d{3})/gc) {
    return "\\$1";
  }
  elsif (${$regex} =~ m/\G(.)/gc) {
    return "\\$1";
  }
  else {
    die;
  }
}

=head2 Regex::Boost::tokenize

Breaks a regular expression into tokens.

=cut

sub tokenize ($) {
  my $regex = shift;

  my @tokens;
  pos($regex) = 0;
  my $length = length($regex);
  while (pos($regex) < $length) {
    if ($regex =~ m/\G(\$)/gc) {
      push @tokens, $1;
    }
    elsif ($regex =~ m/\G\\/gc) {
      my $result = backslash_token($regex);
      return undef unless defined $result;
      push @tokens, $result;
    }
    elsif ($regex =~ m/\G(\(\?:|\(\?=|\(\?!|\(\?<=|\(\?<!|\(|\))/gc) {
      push @tokens, $1;
    }
    elsif ($regex =~ m/\G\[/gc) {
      # the character class
      if ($regex =~ m/\G\^/gc) {
        push @tokens, '[^';
      }
      else {
        push @tokens, '[';
      }
      my $cc = [];
      push @tokens, $cc;

      # first character
      my $first = 1;
      for (;;) {
        my $character;
        if ($first and $regex =~ m/\G(\]|-)/gc) {
          $character = $1;
        }
        elsif (not $first and $regex =~ m/\G(\])/gc) {
          last;
        }
        elsif (not $first and $regex =~ m/\G(-)/gc) {
          $character = $1;
        }
        elsif ($regex =~ m/\G\\/gc) {
          $character = backslash_token($regex);
          die unless defined $character;
        }
        elsif ($regex =~ m/\G(\[:[a-z]+:\])/gc) {
          $character = $1;
        }
        elsif ($regex =~ m/\G(.)/gc) {
          $character = $1;
        }
        else {
          die;
        }
        $first = 0;
        push @$cc, $character;
      }
      push @tokens, ']';
    }
    elsif ($regex =~ m/\G(.)/gc) {
      push @tokens, $1;
    }
    else {
      die;
    }
  }
  return \@tokens;
}

=head2 Regex::Boost::boost2js($regex)

Converts a Boost regular expression to a JavaScript regular expression.  $regex
is a string representing a Boost regular expression.  The result is a string
representing a JavaScript regular expression or undef if $regex is invalid.

=cut

sub boost2js ($) {
  my $regex = shift;

  my $tokens = tokenize $regex;
  if (not defined $tokens) {
    return undef;
  }

  # search through the tokens for things that don't work in JavaScript
  foreach my $token (@$tokens) {
    if (ref $token) {
      # this is a character class
    }
    else {
      if ($token eq '(?<=' or $token eq '(?<!') {
        # JavaScript doesn't support lookbehind
        return undef;
      }
    }
  }

  return serialize @$tokens;
}

1;

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

package SourceHighlight::DOM;

use strict;
use warnings;

use Data::Dumper;

use Parse::RecDescent;

use Regex::Boost;

sub _loadfile {
  my $file = shift;
  open my $lang, '<', "$file" or die "$file: $!";
  local $/;
  my $result = <$lang>;
  close $lang;
  return $result;
}

my $GRAMMAR = <<'ZZZ';

Language: Definition(s?) End
          {
            $item{'Definition(s?)'};
          }
        | <error>

Definition: RedefinitionOrSubstitution NonStateDefinition Exit
            {
              my $definition = $item{NonStateDefinition};
              foreach my $attribute ('RedefinitionOrSubstitution', 'Exit') {
                if ($item{$attribute}) {
                  $definition->{$item{$attribute}} = 1;
                }
              }
              $definition;
            }
          | RedefinitionOrSubstitution StateOrEnvironment NonStateDefinition 
            'begin'
            Definition(s)
            'end'
            {
              my $definition = $item{NonStateDefinition};
              if ($item{RedefinitionOrSubstitution}) {
                $definition->{$item{RedefinitionOrSubstitution}} = 1;
              }
              $definition->{$item{StateOrEnvironment}} = $item{'Definition(s)'};
              $definition;
            }
          | 'vardef' Keyword '=' CommaList
            {
              my $definition = {};
              $definition->{type} = 'VariableDefinition';
              $definition->{identifier} = $item{Keyword};
              $definition->{regex} = $item{CommaList};
              $definition;
            }
          | 'include' '"' <skip:''> m/(?:\\["\\]|[^"])*/ '"'
            {
              $return = ();
              $text = SourceHighlight::DOM::_loadfile($item[4]) . $text;
              -1;
            }

NonStateDefinition: Keyword 'delim' Concatenation(2) Escape Multiline Nested
                    {
                      my $definition = {};
                      $definition->{type} = 'DelimitedDefinition';
                      $definition->{class} = $item{Keyword};
                      $definition->{begin} = $item{'Concatenation(2)'}[0];
                      $definition->{end} = $item{'Concatenation(2)'}[1];
                      $definition->{escape} = $item{Escape};
                      $definition->{multiline} = $item{Multiline};
                      $definition->{nested} = $item{Nested};
                      $definition;
                    }
                  | Keyword 'start' Concatenation
                    {
                      my $definition = {};
                      $definition->{type} = 'LineWideDefinition';
                      $definition->{class} = $item{Keyword};
                      $definition->{regex} = $item{Concatenation};
                      $definition;
                    }
                  | Keyword '=' CommaList Nonsensitive
                    {
                      my $definition = {};
                      $definition->{type} = 'SimpleDefinition';
                      $definition->{class} = $item{Keyword};
                      $definition->{regex} = $item{CommaList};
                      $definition->{nonsensitive} = $item{Nonsensitive};
                      $definition;
                    }
                  | '(' Keywords ')' '=' BackrefRegex {
                      my $definition = {};
                      $definition->{type} = 'SimpleDefinition';
                      $definition->{class} = $item{Keywords};
                      $definition->{regex} = $item{BackrefRegex};
                      $definition;
                    }

Escape: 'escape' Concatenation
      | ''
Exit: 'exitall' | 'exit' | ''
StateOrEnvironment: 'state' | 'environment'
Multiline: 'multiline' | ''
RedefinitionOrSubstitution: 'redef' | 'subst' | ''
Nested: 'nested' | ''
Nonsensitive: 'nonsensitive' | ''

CommaList: Concatenation(s /,/)
Concatenation: StringOrRegexOrVariable(s /\+/)
StringOrRegexOrVariable: String | Regex | BackrefRegex | Variable

Keyword: m/\w+/
Keywords: Keyword(s /,/)
String: '"' <skip:''> m/(?:\\["\\]|[^"])*/ '"'
{
  my $value = $item[3];
  # the characters | and \ are left intact
  $value =~ s/\r|\n//g;
  $value =~ s/([*+?.()[\]{}^\$])/\\$1/g;
  $value =~ s/\\"/"/g;
  $value;
}
Regex: "'" <skip:''> m/(?:\\['\\]|[^'])*/ "'"
{
  my $value = $item[3];
  $value =~ s/\r|\n//g;
  $value =~ s/\\'/'/g;
  # change ( to (?:
  my $tokens = Regex::Boost::tokenize($value);
  my $result = '';
  foreach my $token(@$tokens) {
    if (ref $token) {
      foreach my $character (@$token) {
        $result .= $character;
      }
    }
    else {
      if ($token eq '(') {
        # change parentheses to non-capturing parentheses
        $result .= '(?:';
      }
      else {
        $result .= $token;
      }
    }
  }
  $result;
}
BackrefRegex: '`' <skip:''> m/(?:\\[`\\]|[^`])*/ '`'
{
  my $value = $item[3];
  $value =~ s/\r|\n//g;
  $value =~ s/\\`/`/g;
  $value;
}
Variable: '$' <skip:''> /\w+/
{
  my $definition = {};
  $definition->{type} = 'VariableReference';
  $definition->{identifier} = $item[3];
  $definition;
}

End: m/^\Z/

ZZZ

sub _prune($);

sub _prune($) {
  my $definitions = shift;
  my $length = scalar @$definitions;
  for (my $i = $length - 1; $i >= 0; $i--) {
    my $definition = $definitions->[$i];
    if ($definition == -1) {
      splice @$definitions, $i, 1;
    }
    elsif ($definition->{state}) {
      _prune($definition->{state});
    }
    elsif ($definition->{environment}) {
      _prune($definition->{environment});
    }
  }
}

$Parse::RecDescent::skip = '(?:\s|#.*\n|#.*$)*';
$::RD_WARN = 3;
# $::RD_AUTOACTION = '$#item > 1? $item[1]: ""';
my $parser = Parse::RecDescent->new($GRAMMAR) or die "Bad grammar!";

sub parse($) {
  my $string = shift;
  my $tree = $parser->Language($string);
  _prune($tree) if defined $tree;
  return $tree;
}

sub _evaluate_variable {
  my $var = shift;
  my $symbol_table = shift;
  if (not exists $symbol_table->{$var->{identifier}}) {
    die;
  }
  return $symbol_table->{$var->{identifier}};
}

sub _evaluate_concatenation {
  my $concatenation = shift;
  my $symbol_table = shift;

  if (not ref $concatenation) {
    # this must already be evaluated
    return $concatenation;
  }

  my $length = scalar @$concatenation;
  my @result;
  for (my $i = 0; $i < $length; $i++) {
    my $term = $concatenation->[$i];
    if (ref($term)) {
      push @result, _evaluate_variable($term, $symbol_table);
    }
    else {
      push @result, $term;
    }
  }
  return join '', @result;
}

sub _evaluate_comma_list {
  my $comma_list = shift;
  my $symbol_table = shift;

  if (not ref $comma_list) {
    # this must already be evaluated
    return $comma_list;
  }

  my $length = scalar @$comma_list;
  my @result;
  for (my $i = 0; $i < $length; $i++) {
    # each term is a concatenation
    my $concatenation = $comma_list->[$i];
    push @result, _evaluate_concatenation($concatenation, $symbol_table);
  }
  return join '|', @result;
}

sub _simplify($$);

sub _simplify($$) {
  my $definitions = shift;
  my $symbol_table = shift;

  my $length = scalar(@$definitions);

  # join consecutive simple definitions with same CSS class
  for (my $i = 0; $i < $length - 1; $i++) {
    my $definition = $definitions->[$i];
    if ($definition == -1) {
      die;
    }

    if (not ref $definition) {
      die;
    }

    my $next_definition = $definitions->[$i + 1];
    if ($next_definition == -1) {
      die;
    }

    if (not ref $next_definition) {
      die;
    }

    my $type = $definition->{type};
    if ($definition->{type} eq 'SimpleDefinition' and
        not $definition->{state} and
        not $definition->{environment} and
        $next_definition->{type} eq 'SimpleDefinition' and
        not $next_definition->{state} and
        not $next_definition->{environment} and
        $definition->{class} eq $next_definition->{class}) {
      $next_definition->{regex} = [@{$definition->{regex}}, @{$next_definition->{regex}}];
      $definitions->[$i] = -1;
    }
  }
  _prune($definitions);

  $length = scalar(@$definitions);

  # Pass 1:
  # - evaluate variables
  # - perform concatenations
  for (my $i = 0; $i < $length; $i++) {
    my $definition = $definitions->[$i];
    if ($definition == -1) {
      die;
    }

    if (not ref $definition) {
      die;
    }

    my $type = $definition->{type};
    if ($type eq 'VariableDefinition') {
      my $identifier = $definition->{identifier};
      my $value = _evaluate_comma_list($definition->{regex}, $symbol_table);
      $symbol_table->{$identifier} = $value;
      $definitions->[$i] = -1;
      next;
    }

    my $class = $definition->{class};

    if ($type eq 'SimpleDefinition') {
      my $value = _evaluate_comma_list($definition->{regex}, $symbol_table);
      my $add_word_boundaries = 0;
      if ($value =~ m/^\w/ and $value =~ m/\w$/) {
        $add_word_boundaries = 1;
      }
      # no longer used - use 'i' flag instead
      # if ($definition->{nonsensitive}) {
      #   $value =~ s/([A-Za-z])/\[\u$1\l$1\]/g;
      # }
      if ($add_word_boundaries) {
        $value = "\\b(?:$value)\\b";
      }
      $definition->{regex} = $value;
    }
    elsif ($type eq 'LineWideDefinition') {
      my $value = _evaluate_concatenation($definition->{regex}, $symbol_table);
      $definition->{regex} = $value;
    }
    elsif ($type eq 'DelimitedDefinition') {
      $definition->{begin} = _evaluate_concatenation($definition->{begin}, $symbol_table);
      $definition->{end} = _evaluate_concatenation($definition->{end}, $symbol_table);
      # this is how we make escape characters work:
      if ($definition->{escape}) {
        $definition->{escape} = _evaluate_concatenation($definition->{escape}, $symbol_table);
      }
    }
    else {
      die;
    }

    # check for states
    my $state;
    if (exists $definition->{state}) {
      $state = 'state';
    }
    if (exists $definition->{environment}) {
      $state = 'environment';
    }
    if (defined $state) {
      _simplify($definition->{$state}, $symbol_table);
    }

    # check for redef or subst
    if ($definition->{redef}) {
      for (my $j = $i - 1; $j >= 0; $j--) {
        if ($definitions->[$j] == -1) {
          next;
        }
        if (not ref $class and 
            not ref $definitions->[$j]{class} and
            $class eq $definitions->[$j]{class}) {
          # destroy the old definition
          $definitions->[$j] = -1;
        }
      }
      delete $definition->{redef};
    }
    elsif ($definition->{subst}) {
      # find the first
      my $first = $i;
      $definitions->[$i] = -1;
      for (my $j = $i - 1; $j >= 0; $j--) {
        if ($definitions->[$j] == -1) {
          next;
        }
        if (not ref $class and 
            not ref $definitions->[$j]{class} and
            $class eq $definitions->[$j]{class}) {
          $first = $j;
          $definitions->[$j] = -1;
        }
      }
      $definitions->[$first] = $definition;
      delete $definition->{subst};
    }

  }

  # pass 2:
  # - prune the tree
  _prune($definitions);
}

sub simplify($) {
  my $definitions = shift;
  my $symbol_table = {};
  _simplify($definitions, $symbol_table);
}

1;

=head1 NAME

SourceHighlight::DOM - a "document object model" for source-highlight

=head1 DESCRIPTION

This module creates a "document object model" or parse tree for a
source-highlight language definition.

head1 METHODS

The SourceHighlight::DOM package has the following class methods:

=head2 SourceHighlight::DOM::parse()

  my $parse_tree = SourceHighlight::DOM::parse($string);

This method constructs a parse tree from a file name.  The parse tree is simply
a reference to an array of definitions.  Each definition is a hash with at least
one element: the "type" element.  The type must be one of the types described
below.

=head3 SimpleDefinition

Each definition with this type has the following attributes:

=head4 class

The name of the element being defined.  This will ultimately represent a CSS
class.

=head4 regex

The regular expression for this language element.  This actually represents a 
comma-separated list, and so it is represented by a (reference to a) list.  Each
element of this list represents a concatenation of strings, and so again it is
represented as a (reference to a) list.  Finally, each element of this list is
either a string representing a regular expression or a VariableReference object.

Note that source-highlight allows literal strings as well as regular
expressions, but SourceHighlight::DOM->parse() converts these to regular
expressions before the parse tree is returned.  Thus, you should assume, for example,
that a * character literal in a string represents a quantifier, unless it
is escaped with a backslash.

=head4 nonsensitive

A true value if the "nonsensitive" keyword has been applied to this definition;
a false value otherwise (in which case the attribute may not even exist).

=head4 redef

A true value if the "redef" keyword has been applied to this definition.

=head4 subst

A true value if the "subst" keyword has been applied to this definition.

=head4 exit

A true value if the "exit" keyword has been applied to this definition.

=head4 exitall

A true value if the "exitall" keyword has been applied to this definition.

=head4 state, environment

A reference to a list of definitions, just like the top-level list returned by
the SourceHighlight::DOM::parse() method.

=head3 LineWideDefinition

Each definition of this type has the following attributes:

=head4 class

The name of the element being defined.

=head4 regex

The regular expression for this language element.  This actually represents a
concatenation of strings, and so it is represented as a (reference to a)
list. Each element of this list is a string representing a regular
expression or a VariableReference object.

Note the asymmetry with SimpleDefinition.  In that class, the regex attribute
can be a comma-separated list of concatenations of strings, so it is represented
as a list of lists of strings.  In LineWideDefinition, this can only be a
concatenation of strings (it cannot be a comma-separated list), so it is
represented as a list of strings.

=head4 redef, subst, exit, exitall, state, environment

These attributes are the same as those in SourceHighlight::DOM::SimpleDefinition.

=head3 DelimitedDefinition

Each definition of this type has the following elements:

=head4 class

The name of the element being defined.

=head4 begin, end

The beginning and ending regular expressions, respectively.  Each of these is a list
of strings, representing a concatenation.

head4 escape

A list of strings representing a concatenation.

=head4 multiline, nested, redef, subst, exit, exitall, state, environment

=head3 VariableDefinition

=head4 identifier

The name of the variable being defined.

=head4 regex

The value assigned to the variable.  This is a list of lists of strings.

=head2 SourceHighlight::DOM::simplify($parse_tree)

This method does the following for the entire tree (recursively, including
states and environments):

=over

=item Evaluates all variable references.

=item Combines concatenations and comma-separated lists.

=item Prunes all variable definitions.

=item Evaluates all redefs or substs.

=back

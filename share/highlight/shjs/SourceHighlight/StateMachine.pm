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

package SourceHighlight::StateMachine;

use strict;
use warnings;

sub _state($$);

sub _state($$) {
  my $state_machine = shift;
  my $definitions = shift;

  my $state = [];
  my $state_index = push(@$state_machine, $state) - 1;
  foreach my $definition (@$definitions) {
    my $type = $definition->{type};

    my $pattern = {};
    push @$state, $pattern;

    $pattern->{class} = $definition->{class};

    if ($definition->{nonsensitive}) {
      $pattern->{nonsensitive} = 1;
    }

    if ($definition->{state}) {
      $pattern->{state} = 1;
    }

    if ($definition->{exit}) {
      $pattern->{exit} = $definition->{exit};
    }
    elsif ($definition->{exitall}) {
      $pattern->{exitall} = $definition->{exitall};
    }

    my $next;
    if ($definition->{environment}) {
      $next = $definition->{environment};
    }
    elsif ($definition->{state}) {
      $next = $definition->{state};
    }

    if ($type eq 'LineWideDefinition' or $type eq 'DelimitedDefinition') {
      if (not defined $next) {
        $next = [];
      }
    }

    my $next_index;
    if (defined $next) {
      $next_index = _state($state_machine, $next);
      $pattern->{next} = $next_index;
      $next = $state_machine->[$next_index];
    }

    if ($type eq 'LineWideDefinition') {
      $pattern->{regex} = $definition->{regex};
      my $end_pattern = {};
      # Regex::Boost sees the 'n' at the end and thinks it's an alphanumeric keyword
      # $end_pattern->{regex} = '\n';
      $end_pattern->{regex} = '$';
      $end_pattern->{exit} = 1;
      unshift @$next, $end_pattern;
    }
    elsif ($type eq 'DelimitedDefinition') {
      $pattern->{regex} = $definition->{begin};

      if ($definition->{nested}) {
        my $nested_pattern = {};
        $nested_pattern->{regex} = $definition->{begin};
        $nested_pattern->{next} = $next_index;
        $nested_pattern->{class} = $definition->{class};
        if ($definition->{state}) {
          $nested_pattern->{state} = 1;
        }
        unshift @$next, $nested_pattern;
      }

      my $end_pattern = {};
      $end_pattern->{regex} = $definition->{end};
      $end_pattern->{exit} = 1;
      $end_pattern->{class} = $definition->{class};
      unshift @$next, $end_pattern;

      if ($definition->{escape}) {
        my $escape_pattern = {};
        $escape_pattern->{regex} = $definition->{escape} . '(?:' . $definition->{escape} . '|' . $definition->{end} . ')';
        unshift @$next, $escape_pattern;
      }

      if (not $definition->{multiline} and
          not $definition->{state} and
          not $definition->{environment}) {
        # we declare that the end of the line ends the pattern
        # This helps prevent runaway strings etc.
        my $end_of_line_pattern = {};
        $end_of_line_pattern->{regex} = '$';
        $end_of_line_pattern->{exit} = 1;
        unshift @$next, $end_of_line_pattern;
      }
    }
    elsif ($type eq 'SimpleDefinition') {
      $pattern->{regex} = $definition->{regex};
    }
    else {
      die;
    }
  }

  return $state_index;
}

sub _states_equal($$) {
  my $state1 = shift;
  my $state2 = shift;

  my $length = scalar(@{$state1->{state}});
  if ($length != scalar(@{$state2->{state}})) {
    return 0;
  }

  for (my $i = 0; $i < $length; $i++) {
    my $pattern1 = $state1->{state}->[$i];
    my $pattern2 = $state2->{state}->[$i];

    if ($pattern1->{regex} ne $pattern2->{regex}) {
      return 0;
    }

    if ($pattern1->{nonsensitive} and not $pattern2->{nonsensitive} or
        $pattern2->{nonsensitive} and not $pattern1->{nonsensitive}) {
      return 0;
    }

    if (exists($pattern1->{class}) and not exists($pattern2->{class}) or
        exists($pattern2->{class}) and not exists($pattern1->{class})) {
      return 0;
    }
    elsif (exists($pattern1->{class}) and exists($pattern2->{class})) {
      if (ref($pattern1->{class}) and ref($pattern2->{class})) {
        my $length1 = scalar(@{$pattern1->{class}});
        my $length2 = scalar(@{$pattern2->{class}});
        if ($length1 != $length2) {
          return 0;
        }
        for (my $j = 0; $j < $length1; $j++) {
          if ($pattern1->{class}->[$j] ne $pattern2->{class}->[$j]) {
            return 0;
          }
        }
      }
      elsif (not ref($pattern1->{class}) and not ref($pattern2->{class})) {
        if ($pattern1->{class} ne $pattern2->{class}) {
          return 0;
        }
      }
      else {
        return 0;
      }
    }

    if ($pattern1->{exit} and not $pattern2->{exit} or
        $pattern2->{exit} and not $pattern1->{exit}) {
      return 0;
    }

    if ($pattern1->{exitall} and not $pattern2->{exitall} or
        $pattern2->{exitall} and not $pattern1->{exitall}) {
      return 0;
    }

    if (exists($pattern1->{next}) and not exists($pattern2->{next}) or
        exists($pattern2->{next}) and not exists($pattern1->{next})) {
      return 0;
    }
    elsif (exists($pattern1->{next}) and exists($pattern2->{next}) and
           not ($pattern1->{next} == $state1 and $pattern2->{next} == $state2) and
           $pattern1->{next} != $pattern2->{next}) {
      return 0;
    }
  }

  return 1;
}

sub _calculate_height($);

sub _calculate_height($) {
  my $state = shift;

  my $height = 0;
  foreach my $pattern (@{$state->{state}}) {
    if (exists $pattern->{next}) {
      my $next = $pattern->{next};
      if ($next == $state) {
        next;
      }
      if (not exists $next->{height}) {
        _calculate_height($next);
      }
      my $h = $next->{height} + 1;
      if ($height < $h) {
        $height = $h;
      }
    }
  }
  $state->{height} = $height;
}

sub _optimize($) {
  my $state_machine = shift;

  # change states from arrays into objects
  my $length = scalar(@$state_machine);
  for (my $i = 0; $i < $length; $i++) {
    my $object = {};
    $object->{index} = $i;
    $object->{incoming} = [];
    $object->{state} = $state_machine->[$i];
    $state_machine->[$i] = $object;
  }

  # change each `next' field from array index to reference
  foreach my $state (@$state_machine) {
    foreach my $pattern (@{$state->{state}}) {
      if (exists $pattern->{next}) {
        my $next = $pattern->{next};
        $pattern->{next} = $state_machine->[$next];
        my $incoming = $pattern->{next}->{incoming};
        push @$incoming, $pattern;
      }
    }
  }

  # calculate the "height" of each state
  _calculate_height($state_machine->[0]);

  # group states by height
  my @heights;
  foreach my $state (@$state_machine) {
    my $height = $state->{height};
    if (not ref($heights[$height])) {
      $heights[$height] = [];
    }
    push @{$heights[$height]}, $state;
  }

  # remove duplicate states
  my $max_height = scalar(@heights) - 1;
  for (my $height = 0; $height <= $max_height; $height++) {
    my $states = $heights[$height];
    if (not ref($states)) {
      next;
    }
    my $num_states = scalar(@$states);
    for (my $i = $num_states - 1; $i > 0; $i--) {
      my $statei = $states->[$i];
      for (my $j = $i - 1; $j >= 0; $j--) {
        my $statej = $states->[$j];
        if (_states_equal($statei, $statej)) {
          # change all incoming patterns to point to the other state
          my $incoming = $statei->{incoming};
          foreach my $pattern (@$incoming) {
            $pattern->{next} = $statej;
          }
          push @{$statej->{incoming}}, @$incoming;
          $state_machine->[$statei->{index}] = -1;
          last;
        }
      }
    }
  }

  # write out the result
  my $result = [];
  my $result_index = 0;
  foreach my $state (@$state_machine) {
    if (not ref $state) {
      next;
    }
    my $incoming = $state->{incoming};
    foreach my $pattern (@$incoming) {
      $pattern->{next} = $result_index;
    }
    $result->[$result_index] = $state->{state};
    $result_index++;
  }

  return $result;
}

sub state_machine($) {
  my $definitions = shift;
  SourceHighlight::DOM::simplify($definitions);
  my $state_machine = [];
  _state($state_machine, $definitions);

  for (my $i = 0; $i < scalar(@$state_machine); $i++) {
    my $old_state = $state_machine->[$i];
    foreach my $pattern (@$old_state) {
      my $regex = $pattern->{regex};
      $regex = Regex::Boost::boost2js($regex);
      defined $regex or die "Invalid boost regex: $regex\n";
      $pattern->{regex} = $regex;
    }
  }

  $state_machine = _optimize($state_machine);

  return $state_machine;
}

1;

=head1 NAME

SourceHighlight::StateMachine - a state machine for source-highlight

=head1 DESCRIPTION

This module creates a state machine for a source-highlight language definition.

=head1 METHODS

=head2 SourceHighlight::StateMachine::state_machine($dom)

Creates a state machine from a DOM.  The state machine is simply a (reference to
a) list of states; each state is a (reference to a) list of patterns; each
pattern is a hash which is similar to a definition in the DOM.  It may have
the attributes "class", "regex", "exit", "exitall" as in the DOM.  It may
also contain the attribute "state" for a pattern which represents a state
and the attribute "next".  If "next" exists, it is a an integer index to the
top-level list of states.

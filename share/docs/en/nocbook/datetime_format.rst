.. _datetime_format:

Appendix 2: Datetime format
===========================
NOC uses the same format as PHP's date() function (http://php.net/date) with some custom extensions.
Available format characters:

=========== =========================================================================== ===============================================
Format char Description                                                                 Example output
a           'a.m.' or 'p.m.'                                                            'a.m.'
A           'AM' or 'PM'                                                                'AM'
b           Month, textual, 3 letters, lowercase.                                       'jan'
B           Not implemented.                                                            
d           Day of the month, 2 digits with leading zeros.                              '01' to '31'
D           Day of the week, textual, 3 letters.                                        'Fri'
f           Time, in 12-hour hours and minutes, with minutes left off if they're zero.  '1', '1:30'
F           Month, textual, long.                                                       'January'
g           Hour, 12-hour format without leading zeros.                                 '1' to '12'
G           Hour, 24-hour format without leading zeros.                                 '0' to '23'
h           Hour, 12-hour format.                                                       '01' to '12'
H           Hour, 24-hour format.                                                       '00' to '23'
i           Minutes.                                                                    '00' to '59'
I           Not implemented.                                                            
j           Day of the month without leading zeros.                                     '1' to '31'
l           Day of the week, textual, long.                                             'Friday'
L           Boolean for whether it's a leap year.                                       True or False
m           Month, 2 digits with leading zeros.                                         '01' to '12'
M           Month, textual, 3 letters.                                                  'Jan'
n           Month without leading zeros.                                                '1' to '12'
N           Month abbreviation in Associated Press style.                               'Jan.', 'Feb.', 'March', 'May'
O           Difference to Greenwich time in hours.                                      '+0200'
P           Time, in 12-hour hours, minutes and 'a.m.'/'p.m.' with extensions           1 a.m.', '1:30 p.m.', 'midnight', 'noon'
r           RFC 2822 formatted date.                                                    'Thu, 21 Dec 2000 16:01:07 +0200'
s           Seconds, 2 digits with leading zeros.                                       '00' to '59'
S           English ordinal suffix for day of the month, 2 characters.                  'st', 'nd', 'rd' or 'th'
t           Number of days in the given month.                                          28 to 31
T           Time zone of this machine.                                                  'EST', 'MDT'
U           Not implemented.                                                            
w           Day of the week, digits without leading zeros.                              '0' (Sunday) to '6' (Saturday)
W           ISO-8601 week number of year, with weeks starting on Monday.                1, 53
y           Year, 2 digits.                                                             '99'
Y           Year, 4 digits.                                                             '1999'
z           Day of the year.                                                            0 to 365
Z           Time zone offset in seconds. (West of UTC is negative, east - positive.     -43200 to 43200
=========== =========================================================================== ===============================================

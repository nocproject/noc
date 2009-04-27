**************
Knowledge Base
**************
Overview
========
Knowledge base (KB) is a special kind of database to share knowledge between
the staff. Basic element of knowledge base is an **article**. Article is a
free-form text message (possible) containing some pieces of knowledge to be shared:
troubleshooting info, hints, references, rumors, FAQs, whitepapers, guides, manuals,
spoilers, common cases and other info. 
Each KB Article has unique number and can be referred by number (i.e. KB100).
Unlimited amount of files, containing text, image and binary data can be attached
to the article.

NOC's KB is similar to wiki and can mimic the wiki behavior. Though KB do not force
specific markup syntax for articles. Desired markup for specific article can be set instead.
Markup syntaxes supported through **parsers**. Some parsers (i.e. Creole) implements
common wiki-syntax with inter-articles and inter-wiki links allowing KB to be used
instead of Wiki.

Written natural language explicitly specified for article. Article also can
be assigned to several **categories**.

Terminology
============
* Article - Free-form text message
* Attachment - File, attached to the article
* Category - Article can be assigned to
* Language - Written natural language of article
* Parser - plugin to convert specific markup syntax to HTML

Link Syntax
===========
Though link syntax vary between **parsers** the predefined set of rules exists:
* KB<id> - Link to the KB's entry **<id>**
* TT<id> - Link to the trouble ticket **<id>**
* attach:<name> - Link to the article attachment **<name>**
* URL - Remains unchanged

Macros
======
Macros are text snippets which can be expanded during preview time. Macros are not
bound to specific markup language and can be used in all markup languages which
offer macro support

now
---
Expands to current date and time. Accepts optional format argument.
Uses the same format as PHP's date() function (http://php.net/date) with some custom extensions.
Available format strings:

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

Example (Creole)::

    <<now>>
    <<now format='Y.m.d H:i:s'>>

Markup Syntaxes
===============
Plain Text
----------
Plain text without specific formatting. Text will be marked as pre-formated
and displayed as-is.

Creole
------
`Creole <http://www.wikicreole.org/>`_ is a lightweight markup language aimed at being common
markup language for wikies.

Emphasized text::

    //italic//
    **bold**

Lists::

    * Bullet list
    * second item
    ** Sub item
    
    # Numbered list
    # Second item
    ## Sub item

Links::

    [[link]]
    [[link|Text]]

Headings::

    = Extra-Large Heading
    == Large heading
    === Medium heading
    ==== Small Heading

Linebreaks::

    force\\linebreak

Horizontal line::

    ----

Images::

    {{attachment_name|title}}
    
Tables::

    |= |= table |= header |
    | a | table | row |
    | b | table | row |

No markup::

    {{{
    This text will //not// be **formatted**.
    }}}

CSV
---
`Comma-separated values <http://en.wikipedia.org/wiki/Comma-separated_values>`_ is a common data-interchange format.
Each line represents database record. Columns are separated by commas. Cell can be surrounded by quotes to cancel
effect of in-cell commas.

Example::

    Col1,Col2,Col3
    1,2,"First and second"
    3,4,"Third, Fourth"

CSV article will be rendered as HTML Table.

Forms
=====
Knowledge Base
--------------
Permissions
^^^^^^^^^^^
======= ========================================
add     kb | KB Entry | Can add KBEntry
change  kb | KB Entry | Can change KBEntry
delete  kb | KB Entry | Can delete KBEntry
======= ========================================

Setup
=====
Categories
----------
Permissions
^^^^^^^^^^^
======= =========================================
add     kb | KB Category | Can add KBCategory
change  kb | KB Category | Can change KBCategory
delete  kb | KB Category | Can delete KBCategory
======= =========================================

Entries
-------
Permissions
^^^^^^^^^^^
======= ========================================
add     kb | KB Entry | Can add KBEntry
change  kb | KB Entry | Can change KBEntry
delete  kb | KB Entry | Can delete KBEntry
======= ========================================
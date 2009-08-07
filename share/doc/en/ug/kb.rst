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

KB supports global and user bookmarks conception. Bookmarks are shortcuts for frequently
used KB Articles. Global bookmarks are created by administrator and are visible for every user.
User bookmarks are maintained by each user independently and seen only by this user. Bookmarks
often used as entry points to knowledge base. Good practice is to set up bookmarks to
index articles, containing links to other articles and usage hints. This will help users
to navigate along KB.

Terminology
============
* Article - Free-form text message
* Attachment - File, attached to the article
* Category - Article can be assigned to
* Language - Written natural language of article
* Parser - plugin to convert specific markup syntax to HTML
* Bookmark - shortcut to the KB article

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
Expands to current date and time. Accepts optional format argument. See :ref:`datetime_format` for
format characters description.

Example (Creole)::

    <<now>>
    <<now format='Y.m.d H:i:s'>>

format
------
Performs syntax highlighting for specified syntax. Accepts optional *syntax* argument.
All `pygments built-in formats <http://pygments.org/docs/lexers/>`_ are supported.

Examples (Creole)::

    <<format syntax="python">>
    def test(s):
        return s+1
    <</format>>
    
    <<format syntax="c">>
    int main(int argc, char** argv)
    {
        return 0;
    }
    <</format>>

NOC's built-in parsers can be used as well. To use built-in config parser *syntax* must
be started with "noc.", followed by profile name.

Example (Creole)::

    <<format syntax="noc.Cisco.IOS">>
    ! test
    interface GigabitEthernet1/0/1
        shutdown
    <</format>>

rack
----
Rack macro offers simple XML-based language for rack space allocation and renders neat rack image.

Example (Creole)::

    <<rack>>
    <rackset id="test">
        <rack id="Rack 01" height="42U">
            <allocation id="UPS" position="1" height="5U" />
        </rack>
        
        <rack id="Rack 02" height="44U">
            <allocation id="UPS" position="1" height="5U" reserved="1" />
            <allocation id="MX480" position="6" height="6U" />
        </rack>
    </rackset>
    <</rack>>

Tags are

rackset
^^^^^^^
Top-level tag and rack container. There can be only single rackset per macro

Attributes:

 * id - name of the rackset
 * label (optional) - rack labels position. One of - "bottom" (default), "top", "both" or "none"

rack
^^^^
Rack. Place for allocations.

Parent tag: rackspace

Attributes:

 * id - name of the rack
 * height - height of the rack in units. May have "U" letter at the end.

allocation
^^^^^^^^^^
Rack space allocation. Can be equipment or reserved space. You need no declare empty space implicitly.

Parent tag: rack

Attributes:

 * id - name of the allocation
 * position - bottom position in the rack. Lowest position of the rack is 1.
 * height - height in the units. May have "U" letter at the end.
 * reserved (optional) - 0 (default) - equipment present in rack, 1 - equipment is planned for placement

search
------
*search* macro renders a list of articles satisfying given criteria. Format::

    search [category=cat1,...,catN] [language=lang] [limit=N] [order_by=field] [display_list=field1,...,fieldN] [title=s]

Where:

* category=cat1,...,catN - Restrict articles to those having categories cat1 and cat2 and ... catN set
* language=lang - Restrict articles to those having language *lang* set. Additional restriction to *category*
* limit=N - limit list to first *N* items found
* order_by=field - Order list by field. Field is one of id, subject. Prepend field name with minus (-) to apply descending order
* display_list=field1,...,fieldN - Render field1,....,fieldN in a list. Available fields are id, subject
* title=s - Render list title *s*

Examples (Creole)::

    <<search title="All articles">>
    
    <<search title="Russian articles" language="Russian">>
    
    <<search title="Rack schemes" category="Rack" >>
    
    <<search title="Last article" order_by="-id" limit="1">>

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

Macros::

    <<macro1 arg1='value1' arg2='value2'>>
    ...
    <<macro2 arg1='value1' arg2='value2'>>
        Macro Text
    <</macro2>>

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

Convert from other wiki/kb engines
==================================

MoinMoin
--------
Unpack MoinMoin **data** directory. **data** directory should contain at least **pages** directory,
where Wiki pages and attachments are stored.

Run converter tool::

    # su - noc
    $ cd /opt/noc
    $ python manage.py convert-moin [--encoding=encoding] [--language=language] [--category=category] <path to data>

where:

* encoding - MoinMoin wiki encoding (utf-8 by default).
* language - Language to be set on imported articles (English by default)
* category - Category to include imported articles into (Do not set articles category by default)
* path to data - full path to MoinMoin data directory

Ensure **data** directory and files below are accessible from user **noc**.

All attachments and modification history are migrated during convertion process.

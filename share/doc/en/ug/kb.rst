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
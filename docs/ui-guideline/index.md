# NOC UI Guideline

This document defines a framework for detecting and mitigating UI-related problems
and is intended for NOC front-end developers and Q&A testers.
The declared requirements are mandatory for the NOC User Interface. 
The violation of the following rules must always be considered an error and must be fixed.
This document is subject to periodical review and will evolve to cover all aspects of the user interface.

## UI Problems

Problems detected during the testing stage must be referred by their codes.

## Flaws

Flaws are visual imperfection which not directly affects user operations, but are seen by the eye and disrupt a visual harmony. Thus, flaws make UI less pleasant to use and, therefore, affect the overall experience.

* `UI-FLAW-0001`: Each panel containing text or editable fields must have a padding of 4.

## Inconsistencies

Inconsistency means the same things in different places are performed differently, which leads to counter-intuitive behavior and, therefore, leads to bugs and affects the overall experience.

* `UI-INC-0001`: Forms allowing editing must have buttons "Save" and "Close" located in the leftmost part of the toolbar
* `UI-INC-0002`: The following buttons always must have the following glyphs:

    | Button | Glyph      |
    | ------ | ---------- |
    | Save   | save       |
    | Close  | arrow-left |

* `UI-INC-0002` Form fields Remote System/Remote Id/BI ID must be grouped into the "Integration" field set.
* `UI-INC-0003`: All search fields must have a "Search..." placeholder.
* `UI-INC-0004`: Fields ID, UUID, and BI ID, while not editable, must have a glyph "clipboard" placed just after the value. Pressing the glyph must trigger the "Copied to clipboard" info notification and the field value must be copied to the clipboard.

## Bug

Bugs are direct malfunctions in the UI that prevent a user from performing the task.
The bugs are addressed by appropriate issues.
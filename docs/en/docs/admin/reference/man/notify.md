# notify


## Name

*notify*: Send notification to [reference-notification-group](../../../user/reference/concepts/notification-group/index.md)

## Synopsis

    noc notify [--debug] [--dry-run]
        [--notification-group=<group_name>]
        [--template=<template name>] [--var=*key*=<value>]
        [--subject=<subject>]
        [--body=<body>]
        [--body-file=<file_name>]

## Description

*notify* renders body and subject and sends to given notification groups

Arguments:
* --debug - Print debugging message
* --dry-run - Do not really send message
* --notification-group=*group_name* - Send message to [reference-notification-group](../../../user/reference/concepts/notification-group/index.md).
  Multiple *Notification Groups* may be set
* --template=*template_name* - Render subject and body from [reference-template](../../../user/reference/concepts/template/index.md).
  Template variables may be set via additional *--var* parameters
* --var=*key*=*value* - Set template's context variable *key* to value *value*.
  Used with *--template* parameter
* --subject=*subject* - Set subject directly. Overrides *--template* option
* --body=*body* - Set message body directly. Overrides *--template* option
* --body-file=*file_name* - Read body from file *file_name*. Overrides *--body* and *--template* options

## Examples

Send message from template *t1*. Set *host* variable to *myhost* and
*reason* variable to *testing*

    /opt/noc$ ./noc notify --notification-group=mygroup\
        --template=t1 --var=host=myhost --var=reason=testing

Send message to notification groups *mygroup1* and *mygroup2*

    /opt/noc$ ./noc notify \
        --notification-group=mygroup1 \
        --notification-group=mygroup2 \
        --subject=Test \
        --body=Hi

Send message from file

    /opt/noc$ ./noc notify \
        --notification-group=mygroup \
        --subject=Test\ from\ file \
        --body-file=/path/to/file.txt

Read body from stdin

    /opt/noc$ ./noc notify \
        --notification-group=mygroup \
        --subject=Test\ from\ file \
        --body-file=/dev/stdin

## See also

* [reference-template](../../../user/reference/concepts/template/index.md)
* [reference-notification-group](../../../user/reference/concepts/notification-group/index.md)

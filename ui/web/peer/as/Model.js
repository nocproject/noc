//---------------------------------------------------------------------
// peer.as Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.as.Model");

Ext.define("NOC.peer.as.Model", {
  extend: "Ext.data.Model",
  rest_url: "/peer/as/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "asn",
      type: "integer",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "project",
      type: "string",
    },
    {
      name: "project__label",
      type: "string",
      persist: false,
    },
    {
      name: "profile",
      type: "string",
    },
    {
      name: "profile__label",
      type: "string",
      persist: false,
    },
    {
      name: "organisation",
      type: "string",
    },
    {
      name: "organisation__label",
      type: "string",
      persist: false,
    },
    {
      name: "administrative_contacts",
      type: "auto",
    },
    {
      name: "tech_contacts",
      type: "auto",
    },
    {
      name: "maintainers",
      type: "auto",
    },
    {
      name: "routes_maintainers",
      type: "auto",
    },
    {
      name: "header_remarks",
      type: "string",
    },
    {
      name: "footer_remarks",
      type: "string",
    },
    {
      name: "rir",
      type: "int",
    },
    {
      name: "rir__label",
      type: "string",
      persist: false,
    },
    {
      name: "labels",
      type: "auto",
    },
    // CSS
    {
      name: "row_class",
      type: "string",
      persist: false,
    },
  ],
});

//---------------------------------------------------------------------
// project.project Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.project.project.Model");

Ext.define("NOC.project.project.Model", {
  extend: "Ext.data.Model",
  rest_url: "/project/project/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "code",
      type: "string",
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "shape_overlay_glyph",
      type: "string",
    },
    {
      name: "shape_overlay_glyph__label",
      type: "string",
      persist: false,
    },
    {
      name: "shape_overlay_position",
      type: "string",
    },
    {
      name: "shape_overlay_form",
      type: "string",
    },
    {
      name: "remote_system",
      type: "string",
    },
    {
      name: "remote_system__label",
      type: "string",
      persist: false,
    },
    {
      name: "remote_id",
      type: "string",
    },
    {
      name: "bi_id",
      type: "string",
      persist: false,
    },
  ],
});

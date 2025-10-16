//---------------------------------------------------------------------
// dev.spec Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dev.spec.Model");

Ext.define("NOC.dev.spec.Model", {
  extend: "Ext.data.Model",
  rest_url: "/dev/spec/",

  fields: [
    {
      name: "id",
      type: "string",
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
      name: "name",
      type: "string",
    },
    {
      name: "author",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "answers",
      type: "auto",
    },
    {
      name: "changes",
      type: "auto",
    },
    {
      name: "quiz",
      type: "string",
    },
    {
      name: "quiz__label",
      type: "string",
      persist: false,
    },
    {
      name: "revision",
      type: "int",
      defaultValue: 1,
    },
    {
      name: "uuid",
      type: "string",
    },
  ],
});

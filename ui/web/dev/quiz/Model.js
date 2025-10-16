//---------------------------------------------------------------------
// dev.quiz Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dev.quiz.Model");

Ext.define("NOC.dev.quiz.Model", {
  extend: "Ext.data.Model",
  rest_url: "/dev/quiz/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "uuid",
      type: "string",
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "questions",
      type: "auto",
    },
    {
      name: "revision",
      type: "int",
      defaultValue: 1,
    },
    {
      name: "changes",
      type: "auto",
    },
    {
      name: "disclaimer",
      type: "string",
    },
  ],
});

import {parse} from "espree";
import type {Node} from "estree";
import {ExtDefineVisitor} from "../visitors/ExtDefineVisitor.ts";

describe("ExtDefineVisitor", () => {
  it("should extract className and requires from AST", () => {
    const code = `
      Ext.define('MyApp.view.Main', {
        requires: ['NOC.view.Other', "Ext.ux.form.field.BoxSelect"],
        extend: 'Ext.panel.Panel',
        mixins: ['NOC.mixin.SomeMixin'],
        uses: ['MOC.util.SomeUtil']
      });
    `;
    const ast = parse(code, {ecmaVersion: 2020, sourceType: "module"}) as Node;
    const visitor = new ExtDefineVisitor();
    const result = visitor.walk(ast);

    expect(result.className).toBe("MyApp.view.Main");
    expect(result.requires).toEqual([
      "NOC.view.Other",
      "Ext.ux.form.field.BoxSelect",
      "NOC.mixin.SomeMixin",
      "MOC.util.SomeUtil",
    ]);
  });
});

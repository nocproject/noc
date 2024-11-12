import {parse} from "espree";
import type {Node} from "estree";
import {ExtApplicationVisitor} from "../visitors/ExtApplicationVisitor.ts";

describe("ExtApplicationVisitor", () => {
  it("should extract application requires from AST", () => {
    const code = `
      Ext.application({
        name: "Ext.Draw sandbox",
        paths: {
          "NOC": "/ui",
        },
        requires: [
          "NOC.Application",
        ],
        launch: function(){
          Ext.setGlyphFontFamily("FontAwesome");
          Ext.require("NOC.Application", function(){
            Ext.create("NOC.Application");
          },this);
        },
      });
    `;
    const ast = parse(code, {ecmaVersion: 2020, sourceType: "module"}) as Node;
    const visitor = new ExtApplicationVisitor();
    const result = visitor.walk(ast);

    expect(result.className).toBe("Ext.application");
    expect(result.requires).toEqual([
      "NOC.Application",
    ]);
  });
});

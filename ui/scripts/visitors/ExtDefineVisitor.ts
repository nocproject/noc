import type {Node} from "estree";
import type {RequireInfo} from "../ExtJsParser.ts";
import {MethodCallVisitor} from "../visitors/MethodCallVisitor.ts";

export class ExtDefineVisitor{
  private visitor: MethodCallVisitor;

  constructor(){
    this.visitor = new MethodCallVisitor("Ext.define", ["requires", "extend", "mixins", "uses", "model"]);
  }

  walk(ast: Node): RequireInfo{
    this.visitor.visitNode(ast);
    const result = this.visitor.getResults();
    const filter_fn = (value: string) => {
      if(value.startsWith("Ext.ux")) return true;
      if(value.startsWith("Ext.")) return false;
      return true;
    };
    return {
      className: result.argument,
      requires: result.values.filter(filter_fn),
    };
  }
}

import type {CallExpression, MemberExpression, Node, Property, SpreadElement} from "estree";
import type {RequireInfo} from "../ExtJsParser.ts";
import {BaseMethodVisitor} from "./BaseMethodVisitor.ts";

export interface ValueResult {
  argument: string;
  values: string[];
}

const METHOD_NAME = "Ext.application";

export class ExtApplicationVisitor extends BaseMethodVisitor{
  private keys: string[];
  private results: ValueResult = {argument: "", values: []};

  constructor(){
    super(METHOD_NAME);
    this.keys = ["requires", "extend", "mixins", "uses", "model"];
  }

  walk(ast: Node): RequireInfo{
    this.visitNode(ast);
    const result = this.getResults();
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

  visitCallExpression(node: CallExpression): void{
    if(node.callee.type === "MemberExpression"){
      const memberExpr = node.callee as MemberExpression;
      const currentFullMethodName = this.extractFullMethodName(memberExpr);

      if(currentFullMethodName === this.fullMethodName){
        const args = node.arguments;

        if(args.length == 1 && args[0].type === "ObjectExpression"){
          const configValues = this.extractConfigValues(args[0]);

          this.results = {
            argument: METHOD_NAME,
            values: configValues,
          };
        }
      }
    }
  }

  private extractConfigValues(node: Node): string[]{
    if(node.type === "ObjectExpression"){
      const values: string[] = [];

      node.properties.forEach((prop: Property | SpreadElement) => {
        if(prop.type === "Property" && prop.key.type === "Identifier"){
          const key = prop.key.name;
          const value = prop.value;

          if(this.keys.includes(key)){
            if(value.type === "Literal" && typeof value.value === "string"){
              values.push(value.value);
            } else if(value.type === "ArrayExpression"){
              const arrayValues = value.elements
                .map((elem) => {
                  if(
                    elem?.type === "Literal" &&
                    typeof elem.value === "string"
                  ){
                    return elem.value;
                  }
                  return null;
                })
                .filter((v): v is string => v !== null);
              values.push(...arrayValues);
            }
          }
        }
      });

      return values;
    }
    return [];
  }

  getResults(): ValueResult{
    return this.results;
  }
}

import type {CallExpression, Expression, Identifier, MemberExpression, Node} from "estree";
import type {RequireInfo} from "../ExtJsParser.ts";
import {BaseMethodVisitor} from "./BaseMethodVisitor.ts";

export interface Replacement {
    type: "CallExpression" | "UnaryExpression";
    callee?: ((node: CallExpression) => Expression) | Expression;
    arguments?: Expression[];
    argument?: Expression;
    operator?: string;
    prefix?: boolean;
}

export interface MethodReplacement {
  name: string;
  replacement: Replacement;
}

export class MethodReplaceVisitor extends BaseMethodVisitor{
  private ast: Node;
  private replacement: Replacement;

  constructor(fullMethodName: string, replacement: Replacement, ast: Node){
    super(fullMethodName);
    this.ast = ast;
    this.replacement = replacement;
  }

  private getMethodName(memberExpr: MemberExpression): string{
    const object = memberExpr.object as Identifier;
    const property = memberExpr.property as Identifier;
    return `${object.name}.${property.name}`;
  }

  private applyReplacement(node: CallExpression, replacement: Replacement){
    let finalReplacement = replacement;
    if(typeof replacement.callee === "function"){
      finalReplacement = {
        ...replacement,
        callee: replacement.callee(node),
      };
    }
    Object.assign(node, finalReplacement);
  }

  visitCallExpression(node: CallExpression): void{
    if(node.callee.type === "MemberExpression"){
      const memberExpr = node.callee as MemberExpression;
      const currentFullMethodName = memberExpr.object.type === "Identifier"
        ? this.getMethodName(memberExpr)
        : this.extractFullMethodName(memberExpr);

      if(currentFullMethodName === this.fullMethodName){
        this.applyReplacement(node, this.replacement);
        // let finalReplacement = this.replacement;
        // if(typeof this.replacement.callee === "function"){
        //   finalReplacement = {
        //     ...this.replacement,
        //     callee: this.replacement.callee(node),
        //   };
        // }
        // Object.assign(node, finalReplacement);
        // Object.assign(node, {
        //   type: "UnaryExpression",
        //   operator: "void",
        //   prefix: true,
        //   argument: {type: "Literal", value: 0},
        // });
      }
    }
    if(node.callee.type === "Identifier"){
      const identifier = node.callee as Identifier;
      if(identifier.name === this.fullMethodName){
        this.applyReplacement(node, this.replacement);
        // let finalReplacement = this.replacement;
        // if(typeof this.replacement.callee === "function"){
        //   finalReplacement = {
        //     ...this.replacement,
        //     callee: this.replacement.callee(node),
        //   };
        // }
        // Object.assign(node, finalReplacement);
        // Object.assign(node, {
        //   type: "CallExpression",
        //   callee: node.arguments[2],
        //   arguments: [],
        // });
      }
    }
    node.arguments.forEach(arg => {
      this.visitNode(arg);
    });

    this.visitNode(node.callee);
  }

  walk(): RequireInfo{
    return {
      className: this.fullMethodName,
      requires: [],
    }
  }

  getResults(): Node{
    this.visitNode(this.ast);
    return this.ast;
  }
}

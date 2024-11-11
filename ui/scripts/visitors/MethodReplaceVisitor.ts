import type {CallExpression, Expression, Identifier, MemberExpression, Node} from "estree";
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
      }
    }
    if(node.callee.type === "Identifier"){
      const identifier = node.callee as Identifier;
      if(identifier.name === this.fullMethodName){
        this.applyReplacement(node, this.replacement);
      }
    }
    node.arguments.forEach(arg => {
      this.visitNode(arg);
    });

    this.visitNode(node.callee);
  }

  getResults(): Node{
    this.visitNode(this.ast);
    return this.ast;
  }
}

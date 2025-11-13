import type {CallExpression, Expression, ExpressionStatement, Identifier, MemberExpression, Node} from "estree";
import type {RequireInfo} from "../ExtJsParser.ts";
import {BaseMethodVisitor} from "./BaseMethodVisitor.ts";

export interface Replacement {
    type: "CallExpression" | "UnaryExpression" | "ExpressionStatement";
    callee?: ((node: CallExpression) => Expression) | Expression;
    arguments?: Expression[];
    argument?: Expression;
    operator?: string;
    expression?: Expression;
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

  visitNode(node: Node): void{
    if(!node) return;
    switch(node.type){
      case "CallExpression":
        this.visitCallExpression(node as CallExpression);
        break;
      case "ExpressionStatement":
        this.visitExpressionStatement(node as ExpressionStatement);
        break;
      default:
        Object.entries(node).forEach(([key, value]) => {
          if(key === "type" || key === "loc" || key === "range") return;
          if(value && typeof value === "object"){
            if(Array.isArray(value)){
              value.forEach(item => {
                if(item && typeof item === "object" && "type" in item){
                  this.visitNode(item as Node);
                }
              });
            } else if("type" in value){
              this.visitNode(value as Node);
            }
          }
        });
    }
  }
  
  visitCallExpression(node: CallExpression): void{
    if(
      node.callee.type === "MemberExpression" &&
    node.callee.property.type === "Identifier" &&
    node.callee.property.name === "catch" &&
    node.callee.object.type === "CallExpression"
    ){
      const thenCall = node.callee.object;
      if(
        thenCall.callee.type === "MemberExpression" &&
      thenCall.callee.property.type === "Identifier" &&
      thenCall.callee.property.name === "then" &&
      thenCall.callee.object.type === "CallExpression"
      ){
        const loadSetCall = thenCall.callee.object;
        if(
          loadSetCall.callee.type === "MemberExpression" &&
        this.getFullMemberPath(loadSetCall.callee) === this.fullMethodName
        ){
          Object.assign(node, this.replacement);
          return;
        }
      }
    }

    if(node.callee.type === "MemberExpression"){
      const memberExpr = node.callee as MemberExpression;
      const currentFullMethodName = this.getFullMemberPath(memberExpr);

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

  visitExpressionStatement(node: ExpressionStatement): void{
    if(
      node.expression.type === "CallExpression" &&
      node.expression.callee.type === "MemberExpression" &&
      node.expression.callee.property.type === "Identifier" &&
      node.expression.callee.property.name === "catch" &&
      node.expression.callee.object.type === "CallExpression"
    ){
      const thenCall = node.expression.callee.object;
      if(
        thenCall.callee.type === "MemberExpression" &&
        thenCall.callee.property.type === "Identifier" &&
        thenCall.callee.property.name === "then" &&
        thenCall.callee.object.type === "CallExpression"
      ){
        const loadSetCall = thenCall.callee.object;
        if(
          loadSetCall.callee.type === "MemberExpression" &&
          this.getFullMemberPath(loadSetCall.callee) === this.fullMethodName
        ){
          Object.assign(node, this.replacement);
          return;
        }
      }
    }
    this.visitNode(node.expression);
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

  private getFullMemberPath(expr: MemberExpression): string{
    const parts: string[] = [];
    let current: MemberExpression | Identifier = expr;
    while(current){
      if(current.type === "MemberExpression"){
        if(current.property.type === "Identifier"){
          parts.unshift(current.property.name);
        }
        current = current.object as MemberExpression | Identifier;
      } else if(current.type === "Identifier"){
        parts.unshift(current.name);
        break;
      } else{
        break;
      }
    }
    return parts.join(".");
  }
}

import type {CallExpression, MemberExpression, Node} from "estree";
import type {RequireInfo} from "../ExtJsParser.ts";

export abstract class MethodVisitor{
  protected fullMethodName: string;

  constructor(fullMethodName: string){
    this.fullMethodName = fullMethodName;
  }

  abstract visitNode(node: Node): void;
  abstract visitCallExpression(node: CallExpression): void;
  abstract walk(ast: Node): RequireInfo;
}

export abstract class BaseMethodVisitor extends MethodVisitor{
  visitNode(node: Node): void{
    if(!node) return;
    switch(node.type){
      case "CallExpression":
        this.visitCallExpression(node as CallExpression);
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

  abstract walk(ast: Node): RequireInfo;

  abstract visitCallExpression(node: CallExpression): void;

  protected extractFullMethodName(memberExpr: MemberExpression): string{
    let objectName = "";
    if(memberExpr.object.type === "Identifier"){
      objectName = memberExpr.object.name;
    }
    const methodName =
      memberExpr.property.type === "Identifier" ? memberExpr.property.name : "";
    return `${objectName}.${methodName}`;
  }

  abstract getResults(): unknown;
}

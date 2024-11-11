import type {CallExpression, MemberExpression, Node} from "estree";

export interface Visitor {
  visitNode(node: Node): void;
  visitCallExpression(node: CallExpression): void;
}

export abstract class BaseMethodVisitor implements Visitor{
  protected fullMethodName: string;

  constructor(fullMethodName: string){
    this.fullMethodName = fullMethodName;
  }

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

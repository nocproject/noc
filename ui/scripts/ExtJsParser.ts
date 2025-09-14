import * as espree from "espree";
import type {Node} from "estree";
import type {MethodVisitor} from "./visitors/BaseMethodVisitor.ts";

export interface RequireInfo {
  className: string;
  requires: string[];
}

interface ParseOptions {
  parserOptions?: espree.Options;
  debug?: boolean;
}

export class ExtJsParser{
  private readonly ast: Node;
  private visitor: MethodVisitor;

  constructor(contents: string, options: ParseOptions, visitor: MethodVisitor){
    this.visitor = visitor;

    try{
      this.ast = espree.parse(contents, options.parserOptions) as Node;
    } catch(error){
      if(error instanceof SyntaxError){
        console.error(`Syntax error while parsing contents: ${error.message}`);
        throw new Error(`Syntax error while parsing contents: ${error.message}`);
      }
      throw new Error(`Failed to parse contents: ${error}`);
    }
  }

  findDependencies(): RequireInfo{
    return this.visitor.walk(this.ast);
  }
}

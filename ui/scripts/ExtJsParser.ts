import * as espree from "espree";
import type {Node} from "estree";
import {ExtDefineVisitor} from "./visitors/ExtDefineVisitor.ts";

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
  private visitor: ExtDefineVisitor;

  constructor(contents: string, options: ParseOptions){
    this.visitor = new ExtDefineVisitor();
    
    try{
      this.ast = espree.parse(contents, options.parserOptions) as Node;
    } catch(error){
      if(error instanceof SyntaxError){
        throw new Error(`Syntax error while parsing contents: ${error.message}`);
      }
      throw new Error(`Failed to parse contents: ${error}`);
    }
  }

  findDependencies(): RequireInfo{
    return this.visitor.walk(this.ast);
  }
}

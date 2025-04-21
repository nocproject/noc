import * as esbuild from "esbuild";
import {BaseBuilder} from "./BaseBuilder.ts";

export class ProdBuilder extends BaseBuilder{
  readonly className: string = "ProdBuilder";

  async start(): Promise<void>{
    try{
      await this.initialize();
      await this.build();
      console.log("Production build completed successfully");
    } catch(error){
      console.error("Production build failed:", error);
      process.exit(1);
    }
  }

  async clean(): Promise<void>{
    await this.clearBuildDir();
  }

  async stop(): Promise<void>{
    if(this.context){
      await this.context.dispose();
    }
    console.log("Prod builder stopped");
  }

  private async build(): Promise<void>{
    await esbuild.build(this.getBaseBuildOptions());
  }
}

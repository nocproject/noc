import * as esbuild from "esbuild";
import {BaseBuilder} from "./BaseBuilder.ts";

export class ProdBuilder extends BaseBuilder{
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

  private async build(): Promise<void>{
    await esbuild.build(this.getBaseBuildOptions());
  }
}

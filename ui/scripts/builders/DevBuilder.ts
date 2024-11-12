import type {ServeResult} from "esbuild";
import * as esbuild from "esbuild";
import {BaseBuilder} from "./BaseBuilder.ts";

export class DevBuilder extends BaseBuilder{
  async start(): Promise<void>{
    try{
      await this.initialize();
      await this.createContext();
      await this.watch();

      const {host, port} = await this.serve();
      console.log("watching...");
      console.log(`serve on http://${host}:${port}`);
    } catch(error){
      console.error("Development server start failed:", error);
      await this.stop();
      process.exit(1);
    }
  }

  private async createContext(): Promise<void>{
    const options = this.getBaseBuildOptions();
    this.context = await esbuild.context({
      ...options,
    });
  }

  private async watch(): Promise<void>{
    if(!this.context){
      throw new Error("Context not initialized");
    }
    await this.context.watch();
  }

  private async serve(): Promise<ServeResult>{
    if(!this.context){
      throw new Error("Context not initialized");
    }
    return await this.context.serve({
      servedir: this.options.buildDir,
    });
  }
}

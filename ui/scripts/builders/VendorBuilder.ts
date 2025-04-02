import * as esbuild from "esbuild";
import fs from "fs-extra";
import path from "path";
import {ExternalLibsPlugin} from "../plugins/ExternalLibsPlugin.ts";
import {BaseBuilder} from "./BaseBuilder.ts";

export class VendorBuilder extends BaseBuilder{
  readonly className: string = "VendorBuilder";

  async start(): Promise<void>{
    try{
      this.setBuildOptions();
      await this.initialize();
      await this.buildVendors();
      console.log("Vendor build completed successfully");
    } catch(error){
      console.error("Vendor build failed:", error);
      process.exit(1);
    }
  }

  async clean(): Promise<void>{
    const vendorBundlePath = path.join(this.options.buildDir, this.options.esbuildOptions.entryNames!);
    console.log("Cleaning vendor build directory...");
    if(await fs.pathExists(vendorBundlePath)){
      await fs.remove(vendorBundlePath);
      console.log(`${vendorBundlePath} removed`);
    }

  }

  async stop(): Promise<void>{
    if(this.context){
      await this.context.dispose();
    }
    console.log("Vendor build stopped");
  }

  private setBuildOptions(): void{
    const externalLibsPlugin = new ExternalLibsPlugin({
      debug: this.options.pluginDebug,
      isDev: this.options.isDev,
      outputDir: this.options.buildDir,
      outputFileName: this.options.esbuildOptions.entryNames!,
    });
    this.options.esbuildOptions = {
      ...this.getBaseBuildOptions(),
      outdir: path.join(this.options.buildDir),
      entryPoints: [],
      plugins: [
        externalLibsPlugin.getPlugin(),
      ],
    };
  }

  private async buildVendors(): Promise<void>{
    // await this.createVendorFile();
    try{
      await esbuild.build(this.options.esbuildOptions!);
      console.log(`Successfully built vendor-bundle `);
    } catch(error){
      console.error(`Failed to build vendor bundle:`, error);
      throw error;
    }
  }

  private async createVendorFile(): Promise<string>{
    const vendors = this.getDependencyFromPackage();
    const imports = vendors.map(vendor =>
      `import "${vendor}";`,
    ).join("\n");

    const vendorContent = `
// Auto-generated vendor imports
${imports}
// Export vendors object
export const vendors = {
  modules: [${vendors.map(v => `"${v}"`).join(", ")}],
};`;
    const outputPath = path.resolve(process.cwd(), this.options.entryPoint!);
    await fs.outputFile(outputPath, vendorContent);

    return outputPath;
  }

  private getDependencyFromPackage(): string[]{
    try{
      const packageJsonPath = path.resolve(process.cwd(), "package.json");
      const packageJson = fs.readJsonSync(packageJsonPath);
      const dependencies = {
        ...packageJson.dependencies || {},
      };

      return Object.keys(dependencies);
    } catch(error){
      console.error("Error reading package.json:", error);
      return [];
    }
  }
}

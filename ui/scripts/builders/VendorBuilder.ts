import * as esbuild from "esbuild";
import fs from "fs-extra";
import path from "path";
import {BaseBuilder} from "./BaseBuilder.ts";

export class VendorBuilder extends BaseBuilder{
  async start(): Promise<void>{
    try{
      await this.initialize();
      await this.buildVendors();
      console.log("Vendor build completed successfully");
    } catch(error){
      console.error("Vendor build failed:", error);
      process.exit(1);
    }
  }

  private async buildVendors(): Promise<void>{
    const vendorDir = path.join(this.options.buildDir);
    const buildOptions: esbuild.BuildOptions = {
      ...this.getBaseBuildOptions(),
      outdir: vendorDir,
      plugins: [ ],
    };

    await this.createVendorFile();
    try{
      await esbuild.build(buildOptions);
      console.log(`Successfully built vendor-bundle `);
    } catch(error){
      console.error(`Failed to build vendor bundle:`, error);
      throw error;
    }
  }

  private async createVendorFile(): Promise<string>{
    const vendors = this.getDependencyFromPackage();
    const imports = vendors.map(vendor =>
      `import '${vendor}';`,
    ).join("\n");

    const vendorContent = `
// Auto-generated vendor imports
${imports}
// Export vendors object
export const vendors = {
  modules: [${vendors.map(v => `'${v}'`).join(", ")}]
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

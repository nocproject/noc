//---------------------------------------------------------------------
// JointJS API - Main Entry Point
//---------------------------------------------------------------------
// Copyright (C) 2007-2026 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

import {dia, highlighters, shapes, util, V, version} from "@joint/core";
// import {cellNamespace} from "./elements.ts";
// import * as factories from "./factories.ts";
// import * as filters from "./filters.ts";
// import {breakText} from "./text-utils.ts";

// Re-export types
// export* from "./elements.ts";
// export* from "./factories.ts";
// export* from "./filters.ts";
// export* from "./text-utils.ts";
// export* from "./types.ts";
/**
 * Unified JointAPI object
 * Aggregates all JointJS functionality for NOC
 */
const JointAPI = {
  // Core JointJS exports
  dia,
  shapes,
  //   cellNamespace,
  V,
  highlighters,
  version,
  
  // Extended utilities
  util: {
    ...util,
    parseCssNumeric: (val: string, units: string[]) => {
      const numeric = parseFloat(val);
      if(isNaN(numeric)) return null;

      const regex = /^(-?[\d.]+)([a-z%]*)$/i;
      const match = val.match(regex);
      if(!match) return null;

      const unit = match[2];
      if(units && units.indexOf(unit) === -1) return null;

      return {
        value: numeric,
        unit: unit,
      };
    },
  },
  test: function(){
    console.log("JointAPI is working! + 7");
  }, 
  // Factory methods
  //   createGraph: factories.createGraph,
  //   createPaper: factories.createPaper,
  
  // SVG filter helpers
  //   loadSvgFilters: filters.loadSvgFilters,
  //   generateColorFilters: filters.generateColorFilters,
  
  // Text utilities
//   breakText,
};

// Expose to global window for legacy code compatibility
declare global {
  interface Window {
    jointAPI: typeof JointAPI;
  }
}

window.jointAPI = JointAPI;

export default JointAPI;

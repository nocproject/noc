import DOMPurify, {Config} from "dompurify"
import {micromark} from "micromark"
import {Extension, gfm, gfmHtml, HtmlExtension} from "micromark-extension-gfm"

interface MicromarkOptions {
    extensions?: Extension[]
    htmlExtensions?: HtmlExtension[]
    sanitize?: boolean
    purifyOptions?: Config
}

declare global {
    interface Window {
        micromark: typeof MicromarkAPI
    }
}

const MicromarkAPI = {
  render: function(text: string, options: MicromarkOptions = {}){
    const defaultOptions: MicromarkOptions = {
      extensions: [gfm()],
      htmlExtensions: [gfmHtml()],
      sanitize: true,
      purifyOptions: {},
    }
    
    const finalOptions = Object.assign({}, defaultOptions, options)
    
    let html = micromark(text, {
      extensions: finalOptions.extensions,
      htmlExtensions: finalOptions.htmlExtensions,
    })
    
    if(finalOptions.sanitize){
      const purify = DOMPurify as {sanitize: (html: string, config?: Config) => string}
      html = purify.sanitize(html, finalOptions.purifyOptions)
    }
    
    return html
  },
  
  renderUnsafe: function(text: string, options: MicromarkOptions = {}){
    const defaultOptions = {
      extensions: [gfm()],
      htmlExtensions: [gfmHtml()],
    }
    
    const finalOptions = Object.assign({}, defaultOptions, options)
    return micromark(text, finalOptions)
  },
  
  sanitize: function(html: string, options: Config = {}){
    return (DOMPurify as {sanitize: (html: string, config?: Config) => string}).sanitize(html, options)
  },
  
  micromark: micromark,
  gfm: gfm,
  gfmHtml: gfmHtml,
  DOMPurify: DOMPurify,
}

window.micromark = MicromarkAPI

export default MicromarkAPI;
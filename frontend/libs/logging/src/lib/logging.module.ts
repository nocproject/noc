import { ModuleWithProviders, NgModule, Optional, SkipSelf } from '@angular/core';
import { LoggingService, LogConfigService } from './logging.service';

export { LoggingService } from './logging.service';
export { LogLevel } from './log-level';

@NgModule()
export class LoggingModule {
  constructor(@Optional() @SkipSelf() parentModule?: LoggingModule) {
    if (parentModule) {
      throw new Error(
        'LoggingModule is already loaded. Import it in the AppModule only');
    }
  }

  static forRoot(config: LogConfigService): ModuleWithProviders<LoggingModule> {
    return {
      ngModule: LoggingModule,
      providers: [
        {
          provide: LoggingService, useFactory: () => {
            return new LoggingService(config);
          }
        }
      ]
    }
  }
}

import { Injectable, Optional } from '@angular/core';

import { LogLevel } from './log-level';

export class LogConfigService {
  level = LogLevel.Debug;
}

@Injectable()
export class LoggingService {
  private readonly logLevel: LogLevel = LogLevel.None;
  constructor(@Optional() config?: LogConfigService) {
    if(config) {
      this.logLevel = config.level;
    }
  }

  logError(message: any, ...args: any[]) {
    if (this.loggingIsTurnedOff()) {
      return;
    }

    args.length ? console.error(message, args) : console.error(message);
  }

  logWarning(message: any, ...args: string[]) {
    if (!this.logLevelIsSet()) {
      return;
    }

    if (this.loggingIsTurnedOff()) {
      return;
    }

    if (!this.currentLogLevelIsEqualOrSmallerThan(LogLevel.Warn)) {
      return;
    }

    args.length ? console.warn(message, args) : console.warn(message);
  }

  logDebug(message: any, ...args: string[]) {
    if (!this.logLevelIsSet()) {
      return;
    }

    if (this.loggingIsTurnedOff()) {
      return;
    }

    if (!this.currentLogLevelIsEqualOrSmallerThan(LogLevel.Debug)) {
      return;
    }

    args.length ? console.log(message, args) : console.log(message);
  }

  private currentLogLevelIsEqualOrSmallerThan(logLevel: LogLevel) {
    if (this.logLevelIsSet()) {
      return this.logLevel <= logLevel;
    }

    return true;
  }

  private logLevelIsSet() {
    return !!this.logLevel;
  }

  private loggingIsTurnedOff() {
    return this.logLevel === LogLevel.None;
  }
}

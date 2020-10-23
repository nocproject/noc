import { Injectable } from '@angular/core';

import { OAuth2Configuration } from '../models';

@Injectable()
export class ConfigurationProvider {
  private internalConfiguration: OAuth2Configuration;

  get oauth2Configuration(): OAuth2Configuration {
    return this.internalConfiguration;
  }

  hasValidConfig() {
    return !!this.internalConfiguration;
  }

  constructor() {
  }

  setConfig(configuration: OAuth2Configuration): void {
    this.internalConfiguration = { ...this.internalConfiguration, ...configuration };
  }
}

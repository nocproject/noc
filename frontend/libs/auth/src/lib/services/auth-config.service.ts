import { Injectable } from '@angular/core';

import { OAuth2Configuration } from '../models';
import { ConfigurationProvider } from './config.provider';

@Injectable()
export class AuthConfigService {

  constructor(
    private readonly configurationProvider: ConfigurationProvider
  ) {
  }

  withConfig(passedConfig: OAuth2Configuration): Promise<any> {
    return new Promise((resolve) => {
      this.configurationProvider.setConfig(passedConfig);
      resolve();
    });
  }
}

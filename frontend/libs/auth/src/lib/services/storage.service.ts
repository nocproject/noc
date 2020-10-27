import { Inject, Injectable } from '@angular/core';

import { StorageKeys, TokensStored } from '../models';
import { STORAGE } from '../utils';

@Injectable()
export class StorageService {
  constructor(
    @Inject(STORAGE) private storage: Storage
  ) {
  }

  get(key: StorageKeys) {
    return this.storage.getItem(key);
  }

  set(key: StorageKeys, value: string) {
    this.storage.setItem(key, value);
  }

  getAccessToken(): string | null {
    return this.get('access_token');
  }

  getRefreshToken(): string | null {
    return this.get('refresh_token');
  }

  getTokens(): TokensStored {
    return {
      access_token: this.get('access_token'),
      access_token_expires_at: this.get('access_token_expires_at'),
      refresh_token: this.get('refresh_token')
    };
  }

  removeTokens(): void {
    this.storage.removeItem('access_token');
    this.storage.removeItem('access_token_expires_at');
    this.storage.removeItem('refresh_token');
  }
}

import { Inject, Injectable, InjectionToken } from '@angular/core';

import { StorageKeys, TokensStored } from '../models';

export const BROWSER_STORAGE = new InjectionToken<Storage>('Browser Storage', {
  factory: () => localStorage
});

@Injectable()
export class StorageService {
  constructor(
    @Inject(BROWSER_STORAGE) private storage: Storage
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

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { Credentials, TokensStored, TokenResponse, RevokeResponse } from '../models';
import { StorageService } from './public';
import { ConfigurationProvider } from './config.provider';

@Injectable()
export class OAuth2SecurityService {

  constructor(
    private http: HttpClient,
    private configurationProvider: ConfigurationProvider,
    private storageService: StorageService
  ) {
  }

  login({ username, password }: Credentials): Observable<TokensStored> {
    return this.http.post<TokenResponse>(this.configurationProvider.oauth2Configuration.tokenEndpoint, {
      grant_type: 'password',
      username: username,
      password: password
    }).pipe(map((tokens) => this.saveTokens(tokens)));
  }

  refresh(token: string): Observable<TokensStored> {
    return this.http.post<TokenResponse>(this.configurationProvider.oauth2Configuration.tokenEndpoint, {
      grant_type: 'refresh_token',
      refresh_token: token
    }).pipe(map((tokens) => this.saveTokens(tokens)));
  }

  logout(token: string): Observable<RevokeResponse> {
    this.storageService.removeTokens();
    return this.http.post<RevokeResponse>(this.configurationProvider.oauth2Configuration.revokeEndpoint, {
      access_token: token
    });
  }

  // save & mapping TokenResponse to TokensStored
  private saveTokens(tokens: TokenResponse): TokensStored {
    const expireAt = (new Date().valueOf() + tokens.expires_in).toString();

    this.storageService.set('access_token', tokens.access_token);
    this.storageService.set('refresh_token', tokens.refresh_token);
    this.storageService.set('access_token_expires_at', expireAt);
    return {
      access_token: tokens.access_token,
      access_token_expires_at: expireAt,
      refresh_token: tokens.refresh_token
    };
  }
}

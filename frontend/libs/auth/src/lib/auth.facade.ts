import { Injectable } from '@angular/core';

import { interval, Observable, of, Subscription } from 'rxjs';
import { tap } from 'rxjs/operators';

import { Store } from '@ngrx/store';

import { LoggingService } from '@noc/log';

import { ConfigurationProvider, StorageService } from './services';
import * as authAction from './actions/auth.actions';
import * as authApiAction from './actions/auth-api.actions';
import * as authSelectors from './auth.selectors';
import * as fromAuth from './reducers';

@Injectable()
export class AuthFacade {
  private refreshSubscription: Subscription;

  isAuthenticated$ = this.store.select(authSelectors.selectIsAuthenticated);

  constructor(
    private store: Store<fromAuth.State>,
    private loggerService: LoggingService,
    private configurationProvider: ConfigurationProvider,
    private storageService: StorageService
  ) {
  }

  checkAuth(): Observable<boolean> {
    if (!this.configurationProvider.hasValidConfig()) {
      this.loggerService.logError('Please provide a configuration before setting up the module');
      this.store.dispatch(authAction.authenticatedFailure());
      return;
    }
    this.areStoredTokensValid();
    return this.isAuthenticated$.pipe(
      tap((isAuth) => {
        if (!isAuth && this.refreshSubscription) {
          this.destroyRefreshTimer();
        }
      })
    );
  }

  logout(): void {
    const token = this.storageService.getAccessToken();
    this.refreshSubscription.unsubscribe();
    this.store.dispatch(authAction.logout({ token }));
  }

  destroyRefreshTimer() {
    this.refreshSubscription.unsubscribe();
  }

  private startRefreshTimer(): Observable<number> {
    const config = this.configurationProvider.oauth2Configuration;
    this.loggerService.logDebug(`renewTimeBeforeTokenExpiresInSeconds : ${config.renewTimeBeforeTokenExpiresInSeconds}`);
    this.loggerService.logDebug(`silentRenew: ${config.silentRenew}`);
    if (config.silentRenew) {
      return interval(300_000); // every 5 min 60 * 5 * 1000
    }
    return of(0);
  }

  private startRefresh(): void {
    if (this.hasAccessTokenExpiredIfExpiryExists()) {
      this.loggerService.logDebug(`Refresh Access Token`);
      this.store.dispatch(authApiAction.refresh({ refreshToken: this.storageService.getRefreshToken() }));
    }
  }

  private authenticatedSuccess(): void {
    this.refreshSubscription = this.startRefreshTimer().subscribe(() => {
      this.startRefresh();
    });
    this.store.dispatch(authAction.authenticatedSuccess());
    this.store.dispatch(authAction.loadTokens({ tokens: this.storageService.getTokens() }));
  }

  private authenticatedFailure(): void {
    this.store.dispatch(authAction.authenticatedFailure());
  }

  private get isAuthorized(): boolean {
    return !!this.storageService.getAccessToken() && !!this.storageService.getRefreshToken();
  }

  private hasAccessTokenExpiredIfExpiryExists(): boolean {
    const accessTokenExpiresIn = this.storageService.get('access_token_expires_at') || '0';
    const accessTokenHasNotExpired = this.validateAccessTokenNotExpired(
      +accessTokenExpiresIn,
      this.configurationProvider.oauth2Configuration.renewTimeBeforeTokenExpiresInSeconds
    );

    return !accessTokenHasNotExpired;
  }

  private validateAccessTokenNotExpired(accessTokenExpiresAt: number, offsetSeconds: number): boolean {
    const nowWithOffset = new Date().valueOf() + offsetSeconds * 1000;
    const tokenNotExpired = (accessTokenExpiresAt > nowWithOffset);

    this.loggerService.logDebug(`Has access_token expired: ${!tokenNotExpired}, ${accessTokenExpiresAt} > ${nowWithOffset}`);

    // access token not expired?
    return tokenNotExpired;
  }

  private areStoredTokensValid(): void {
    if (!this.isAuthorized) {
      this.authenticatedFailure();
      return;
    }

    if (this.hasAccessTokenExpiredIfExpiryExists()) {
      this.loggerService.logDebug('persisted access_token is expired');
      this.authenticatedFailure();
      return;
    }

    this.loggerService.logDebug('persisted access token are valid');

    this.authenticatedSuccess();
  }
}

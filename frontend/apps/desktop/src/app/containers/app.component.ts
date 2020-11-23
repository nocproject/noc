import { Component, Inject, LOCALE_ID, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { Subscription } from 'rxjs';

import { AuthFacade, StorageService, WINDOW } from '@noc/auth';
import { LoggingService } from '@noc/log';

@Component({
  selector: 'noc-root',
  template: `
    <noc-layout [isAuth]="isAuthenticated$ | async"
                [lang]="localeId"
                (langSwitchEvent)="langSwitch($event)"
                (logoutEvent)="logout()">
      <router-outlet></router-outlet>
    </noc-layout>
  `
})
export class AppComponent implements OnInit, OnDestroy {
  base = this.window['_app_base'] || '/';

  private authSubscription: Subscription;
  isAuthenticated$ = this.authFacade.isAuthenticated$;

  constructor(
    @Inject(LOCALE_ID) public localeId: string,
    @Inject(WINDOW) private window: any,
    private loggerService: LoggingService,
    private storageService: StorageService,
    private authFacade: AuthFacade,
    private router: Router
  ) {
    this.loggerService.logDebug(`LOCALE_ID is ${localeId}`);
  }

  ngOnInit(): void {
    this.authSubscription = this.authFacade
      .checkAuth()
      .subscribe(isAuthenticated => {
        const pathname = '/' + this.window.location.pathname.replace(this.base, '');
        this.loggerService.logDebug(`is authenticated ${isAuthenticated}`);
        if (!isAuthenticated) {
          if ('/login' !== pathname) {
            this.storageService.set('redirect', pathname);
            this.loggerService.logDebug('Save redirect url : ' + this.storageService.get('redirect'));
            this.router.navigate(['/login']).then(this.navigateHandler('login page'));
          }
        }
        if (isAuthenticated) {
          this.loggerService.logDebug('Starting refresh timer');
          this.navigateToStoredUrl();
        }
      });
  }

  ngOnDestroy(): void {
    this.authSubscription.unsubscribe();
    // it's probably not necessary
    this.authFacade.destroyRefreshTimer();
  }

  langSwitch(code: string): void {
    this.loggerService.logDebug(code);
    this.window.location.assign(this.replaceLocale(code));
  }

  logout(): void {
    this.authFacade.logout();
  }

  replaceLocale(localeId: string): string {
    return this.window.location.pathname.replace(`/${this.localeId}/`, `/${localeId}/`)
      + this.window.location.search;
  }

  private navigateHandler(path: string) {
    return result => {
      if (!result) {
        this.loggerService.logError(`Navigate to ${path} failed!`);
      }
    };
  }

  private navigateToStoredUrl() {
    const path = this.storageService.get('redirect') || '/';

    if (path === 'none') {
      return;
    }

    if (this.router.url === path) {
      return;
    }

    if (path.toString().includes('/unauthorized')) {
      this.router.navigate(['/']).then(this.navigateHandler('home'));
    } else {
      this.router.navigate([path]).then(result => {
        if (result) {
          this.storageService.set('redirect', 'none');
        }
      });
    }
  }
}

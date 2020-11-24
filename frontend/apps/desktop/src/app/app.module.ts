import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { APP_INITIALIZER, NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { LayoutModule } from '@angular/cdk/layout';

import { StoreModule } from '@ngrx/store';
import { EffectsModule } from '@ngrx/effects';
import { StoreDevtoolsModule } from '@ngrx/store-devtools';

import { AuthConfigService, AuthModule } from '@noc/auth';
import { LoggingModule, LogLevel } from '@noc/log';

import { AppRoutingModule } from './app-routing.module';
import { MaterialModule } from './material.module';

import { HeaderComponent, LanguagePicker, LayoutComponent } from './components';
import { AppComponent, HomePageComponent, TestPageComponent } from './containers';

import { environment } from '@env/environment';

export function configureAuth(authConfigService: AuthConfigService) {
  return () =>
    authConfigService.withConfig({
        forbiddenRoute: '/forbidden',
        postLoginRoute: '/',
        renewTimeBeforeTokenExpiresInSeconds: 20,
        silentRenew: true,
        unauthorizedRoute: '/unauthorized',
        tokenEndpoint: '/api/login/token',
        revokeEndpoint: '/api/login/revoke'
      }
    );
}

const DECLARED_COMPONENTS = [
  AppComponent,
  HeaderComponent,
  HomePageComponent,
  LayoutComponent,
  LanguagePicker,
  TestPageComponent
];

@NgModule({
  declarations: DECLARED_COMPONENTS,
  imports: [
    AppRoutingModule,
    BrowserAnimationsModule,
    BrowserModule,
    MaterialModule,
    AuthModule.forRoot(),
    LoggingModule.forRoot({
      level: environment.production ? LogLevel.Debug : LogLevel.Debug
    }),
    StoreModule.forRoot(
      {},
      {
        metaReducers: !environment.production ? [] : [],
        runtimeChecks: {
          // strictStateImmutability and strictActionImmutability are enabled by default
          strictStateSerializability: true,
          strictActionSerializability: true,
          strictActionWithinNgZone: true,
          strictActionTypeUniqueness: true
        }
      }
    ),
    EffectsModule.forRoot([]),
    !environment.production ?
      StoreDevtoolsModule.instrument({
        name: 'NOC-desktop App'
      }) :
      // In a production build you would want to disable the Store Devtools
      // logOnly: environment.production,
      [],
    FormsModule,
    LayoutModule
  ],
  providers: [
    AuthConfigService,
    {
      provide: APP_INITIALIZER,
      useFactory: configureAuth,
      deps: [AuthConfigService],
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
}

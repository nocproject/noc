import { ModuleWithProviders, NgModule, Optional, SkipSelf } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { HttpClientModule } from '@angular/common/http';

import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCardModule } from '@angular/material/card';

import { LayoutModule } from '@angular/cdk/layout';

import { StoreModule } from '@ngrx/store';
import { EffectsModule } from '@ngrx/effects';

import { AuthFacade } from './auth.facade';
import { LoginFormComponent } from './components';
import { ForbiddenPageComponent, LoginPageComponent, UnauthorizedPageComponent } from './containers';
import { AuthEffects } from './effects';
import * as fromAuth from './reducers';
import {
  AuthConfigService,
  ConfigurationProvider,
  OAuth2SecurityService,
  StorageService
} from './services';
import { STORAGE, WINDOW } from './utils';
import { _localStorage } from './utils/storage.reference';
import { _window } from './utils/window.reference';

export * from './auth.facade';
export * from './models/public';
export * from './services/public';
export { WINDOW } from './utils';

const DECLARED_COMPONENTS = [
  LoginPageComponent,
  LoginFormComponent,
  ForbiddenPageComponent,
  UnauthorizedPageComponent
];

@NgModule({
  imports: [
    CommonModule,
    ReactiveFormsModule,
    HttpClientModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    LayoutModule,
    StoreModule.forFeature(fromAuth.AUTH_FEATURE_KEY, fromAuth.reducers),
    EffectsModule.forFeature([AuthEffects]),
    RouterModule.forChild([
      { path: 'login', component: LoginPageComponent },
      { path: 'unauthorized', component: UnauthorizedPageComponent },
      { path: 'forbidden', component: ForbiddenPageComponent }
    ])
  ],
  declarations: DECLARED_COMPONENTS
})
export class AuthModule {
  constructor(@Optional() @SkipSelf() parentModule?: AuthModule) {
    if (parentModule) {
      throw new Error(
        'AuthModule is already loaded. Import it in the AppModule only'
      );
    }
  }

  static forRoot(): ModuleWithProviders<AuthModule> {
    return {
      ngModule: AuthModule,
      providers: [
        AuthConfigService,
        AuthFacade,
        ConfigurationProvider,
        OAuth2SecurityService,
        StorageService,
        { provide: STORAGE, useFactory: _localStorage, deps: [] },
        { provide: WINDOW, useFactory: _window, deps: [] }
      ]
    };
  }
}

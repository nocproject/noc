import { Injectable } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';

import { Actions, ofType, createEffect } from '@ngrx/effects';

import { of } from 'rxjs';
import { catchError, exhaustMap, map, tap } from 'rxjs/operators';
import {
  LoginPageActions,
  AuthApiActions,
  AuthActions
} from '../actions';

import { Credentials } from '../models';
import { OAuth2SecurityService } from '../services';

@Injectable()
export class AuthEffects {
  login$ = createEffect(() =>
    this.actions$.pipe(
      ofType(LoginPageActions.login),
      map((action) => action.credentials),
      exhaustMap((auth: Credentials) =>
        this.oauth2SecurityService.login(auth).pipe(
          tap(() => AuthActions.authenticatedSuccess),
          map(tokens => AuthApiActions.loginSuccess({ tokens })),
          catchError((error: HttpErrorResponse) => of(AuthApiActions.loginFailure({ error: JSON.stringify(error) })))
        )
      )
    )
  );

  logout$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthActions.logout),
      map((action) => action.token),
      exhaustMap((token: string) =>
        this.oauth2SecurityService.logout(token).pipe(
          tap(() => AuthActions.authenticatedFailure),
          map((response) => response.status),
          map(status => AuthApiActions.logoutSuccess({ status })),
          catchError((error: HttpErrorResponse) => of(AuthApiActions.logoutFailure({ error: JSON.stringify(error) })))
        )
      )
    )
  );

  refresh$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthApiActions.refresh),
      map((action) => action.refreshToken),
      exhaustMap((token: string) =>
        this.oauth2SecurityService.refresh(token).pipe(
          map(tokens => AuthApiActions.refreshSuccess({ tokens })),
          catchError((error: HttpErrorResponse) => of(AuthApiActions.refreshFailure({ error: JSON.stringify(error) })))
        )
      )
    )
  );

  constructor(
    private actions$: Actions,
    private oauth2SecurityService: OAuth2SecurityService
    // private router: Router
  ) {
  }
}

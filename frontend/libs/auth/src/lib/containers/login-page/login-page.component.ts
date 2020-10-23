import { Component, OnInit } from '@angular/core';

import { select, Store } from '@ngrx/store';

import { Credentials } from '../../models';
import * as loginPageAction from '../../actions/login-page.actions';
import * as authSelectors from '../../auth.selectors';
import * as fromAuth from '../../reducers';

@Component({
  selector: 'auth-login-page',
  template: `
    <auth-login-form
      (submitted)="onSubmit($event)"
      [pending]="pending$ | async"
      [errorMessage]="error$ | async"
    >
    </auth-login-form>
  `,
  styles: []
})
export class LoginPageComponent implements OnInit {
  pending$ = this.store.pipe(select(authSelectors.selectLoginPagePending));
  error$ = this.store.pipe(select(authSelectors.selectLoginPageError));

  constructor(
    private store: Store<fromAuth.State>
  ) {
  }

  ngOnInit(): void {
  }

  onSubmit(credentials: Credentials) {
    this.store.dispatch(loginPageAction.login({ credentials }));
  }
}

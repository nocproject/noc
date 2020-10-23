import {
  Action,
  combineReducers,
} from '@ngrx/store';
import * as fromAuth from './auth.reducer';
import * as fromLoginPage from './login-page.reducer';

export const AUTH_FEATURE_KEY = 'auth';

export interface State {
  readonly [AUTH_FEATURE_KEY]: AuthState;
}

export interface AuthState {
  [fromAuth.statusFeatureKey]: fromAuth.AuthStatusState;
  [fromLoginPage.loginPageFeatureKey]: fromLoginPage.LoginPageState;
}

export function reducers(state: AuthState | undefined, action: Action) {
  return combineReducers({
    [fromAuth.statusFeatureKey]: fromAuth.reducer,
    [fromLoginPage.loginPageFeatureKey]: fromLoginPage.reducer,
  })(state, action);
}

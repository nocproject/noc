import { createFeatureSelector, createSelector } from '@ngrx/store';
import { AUTH_FEATURE_KEY, AuthState, State } from './reducers';
import { AuthStatusState, statusFeatureKey } from './reducers/auth.reducer';
import { loginPageFeatureKey, LoginPageState } from './reducers/login-page.reducer';

const getTokens = (state: AuthStatusState) => state.tokens;
const getUser = (state: AuthStatusState) => state.user;
const getIsAuthenticated = (state: AuthStatusState) => state.isAuthenticated;

const getError = (state: LoginPageState) => state.error;
const getPending = (state: LoginPageState) => state.pending;

export const selectAuthState = createFeatureSelector<State, AuthState>(
  AUTH_FEATURE_KEY
);

export const selectAuthStatusState = createSelector(
  selectAuthState,
  (state) => state[statusFeatureKey]
);
export const selectUser = createSelector(
  selectAuthStatusState,
  getUser
);
export const selectTokens = createSelector(
  selectAuthStatusState,
  getTokens
);
export const selectIsAuthenticated = createSelector(
  selectAuthStatusState,
  getIsAuthenticated
);
// export const selectLoggedIn = createSelector(selectTokens, (tokens) => !!tokens);

export const selectLoginPageState = createSelector(
  selectAuthState,
  (state) => state[loginPageFeatureKey]
);
export const selectLoginPageError = createSelector(
  selectLoginPageState,
  getError
);
export const selectLoginPagePending = createSelector(
  selectLoginPageState,
  getPending
);

import { createReducer, on } from '@ngrx/store';

import { AuthApiActions, AuthActions } from '../actions';
import { TokensStored, User } from '../models';

export const statusFeatureKey = 'status';

export interface AuthStatusState {
  isAuthenticated: boolean | null;
  tokens: TokensStored | null;
  user: User | null;
}

export const initialState: AuthStatusState = {
  isAuthenticated: false,
  tokens: null,
  user: null
};

export const reducer = createReducer(
  initialState,
  on(AuthApiActions.loginSuccess, (state, { tokens }) => ({ ...state, tokens, isAuthenticated: true })),
  on(AuthApiActions.refreshSuccess, (state, { tokens }) => ({ ...state, tokens, isAuthenticated: true })),
  on(AuthApiActions.refreshFailure, (() => initialState)),
  on(AuthApiActions.userInfoSuccess, (state, { user }) => ({ ...state, user })),
  on(AuthActions.authenticatedSuccess, (state) => ({ ...state, isAuthenticated: true })),
  on(AuthActions.authenticatedFailure, (state) => ({ ...state, isAuthenticated: false })),
  on(AuthActions.loadTokens, (state, { tokens }) => ({ ...state, tokens })),
  on(AuthActions.logout, () => initialState)
);

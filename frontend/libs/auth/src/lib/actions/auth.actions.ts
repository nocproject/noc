import { createAction, props } from '@ngrx/store';

import { TokensStored } from '../models';

export const logout = createAction('[Auth] Logout', props<{ token: string}>());

export const authenticatedSuccess = createAction('[Auth] Authenticated from local store success');
export const authenticatedFailure = createAction('[Auth] Authenticated from local store failure');
export const loadTokens = createAction(
  '[Auth] Load Tokens from local store',
  props<{ tokens: TokensStored }>()
);
export const loadTokensFailure = createAction(
  '[Auth] Load Tokens from local store failure',
  props<{ error: any }>()
);


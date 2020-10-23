import { props, createAction } from '@ngrx/store';

import { TokensStored, User } from '../models';

export const loginSuccess = createAction(
  '[Auth/API] Login Success',
  props<{ tokens: TokensStored }>()
);

export const loginFailure = createAction(
  '[Auth/API] Login Failure',
  props<{ error: string }>()
);

export const logoutSuccess = createAction(
  '[Auth/API] Logout Success',
  props<{ status: boolean }>()
);

export const logoutFailure = createAction(
  '[Auth/API] Logout Failure',
  props<{ error: string }>()
);

export const userInfoSuccess = createAction(
  '[Auth/API] User Info Success',
  props<{ user: User }>()
);

export const userInfoFailure = createAction(
  '[Auth/API] User Info Failure',
  props<{ error: any }>()
);

export const refresh = createAction('[Auth/API] Refresh', props<{ refreshToken: string }>());
export const refreshSuccess = createAction('[Auth/API] Refresh tokens success',
  props<{ tokens: TokensStored }>()
);
export const refreshFailure = createAction('[Auth/API] Refresh tokens failure',
  props<{ error: string }>()
);


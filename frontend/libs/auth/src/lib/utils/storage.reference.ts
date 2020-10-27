import { InjectionToken } from '@angular/core';

export function _localStorage() {
  return localStorage;
}

export const STORAGE = new InjectionToken('Storage');

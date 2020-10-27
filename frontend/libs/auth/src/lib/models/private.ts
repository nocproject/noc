export class Credentials {
  username: string;
  password: string;
}

export class TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token: string;
}

export type OAuthErrorType =
  'invalid_request'
  | 'invalid_client'
  | 'invalid_grant'
  | 'unauthorized_client'
  | 'unsupported_grant_type'
  | 'invalid_scope';

export class OAuthErrorResponse {
  error: OAuthErrorType;
  error_description: string;
  error_uri: string;
}

export class RevokeResponse {
  status: boolean;
  message: string;
}

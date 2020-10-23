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

export class RevokeResponse {
  status: boolean;
  message: string;
}

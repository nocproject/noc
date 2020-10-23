// ToDo make as class with default values
export interface OAuth2Configuration {
  silentRenew: boolean;
  postLoginRoute: string;
  forbiddenRoute: string;
  unauthorizedRoute: string;
  renewTimeBeforeTokenExpiresInSeconds: number;
  tokenEndpoint: string;
  revokeEndpoint: string;
}

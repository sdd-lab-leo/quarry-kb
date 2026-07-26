export interface ApiErrorBody {
  code: string;
  message: string;
}

export interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  error: ApiErrorBody | null;
  meta: unknown;
}

export type ComponentState = "ready" | "not_ready";

export interface ReadinessData {
  status: "ready" | "not_ready";
  components: {
    configuration: ComponentState;
    database: ComponentState;
    migration: ComponentState;
    vector_capability: ComponentState;
  };
}

export type FoundationUiState =
  | "loading"
  | "ready"
  | "needs_attention"
  | "unreachable";

export class ApiError extends Error {
  readonly code: string;
  readonly status: number;

  constructor(code: string, message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
  }
}

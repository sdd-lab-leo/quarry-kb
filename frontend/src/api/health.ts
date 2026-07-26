import { apiRequest, toApiError } from "./client";
import {
  ApiError,
  type FoundationUiState,
  type ReadinessData,
} from "../types/api";

export interface FoundationStatus {
  state: FoundationUiState;
  message: string;
  components?: ReadinessData["components"];
  code?: string;
}

export async function fetchFoundationStatus(): Promise<FoundationStatus> {
  try {
    const { status, body } = await apiRequest<ReadinessData>("/health/ready", { auth: false });
    if (status === 200 && body.success && body.data?.status === "ready") {
      return {
        state: "ready",
        message: "Foundation ready.",
        components: body.data.components,
      };
    }
    if (status === 503 && body.data) {
      return {
        state: "needs_attention",
        message: body.error?.message || "Foundation needs attention.",
        components: body.data.components,
        code: body.error?.code,
      };
    }
    throw toApiError(status, body);
  } catch (error) {
    if (error instanceof ApiError && error.code === "API_UNREACHABLE") {
      return {
        state: "unreachable",
        message: "Unable to reach API.",
        code: error.code,
      };
    }
    if (error instanceof ApiError) {
      return {
        state: "needs_attention",
        message: error.message,
        code: error.code,
      };
    }
    return {
      state: "unreachable",
      message: "Unable to reach API.",
      code: "API_UNREACHABLE",
    };
  }
}

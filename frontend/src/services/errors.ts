import axios from 'axios'

type ErrorResponseWithDetail = {
  detail?: unknown
}

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as unknown
    if (data && typeof data === 'object') {
      const detail = (data as ErrorResponseWithDetail).detail
      if (typeof detail === 'string' && detail.trim().length > 0) return detail
    }
    return error.message || fallback
  }

  if (error instanceof Error) return error.message || fallback

  return fallback
}

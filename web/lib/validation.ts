export const EXERCISES = ["auto", "squat", "jumping_jack", "push_up"] as const;
export type Exercise = (typeof EXERCISES)[number];
export const MAX_FILE_BYTES = 100 * 1024 * 1024;
export const ALLOWED_TYPES = {
  "video/mp4": "mp4",
  "video/quicktime": "mov",
  "video/webm": "webm",
} as const;

export function isExercise(value: unknown): value is Exercise {
  return typeof value === "string" && EXERCISES.includes(value as Exercise);
}

export function isValidWeight(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value) && value >= 30 && value <= 250;
}

export function isValidStorageKey(value: unknown): value is string {
  return typeof value === "string" && /^uploads\/[0-9a-f-]{36}\.(mp4|mov|webm)$/.test(value);
}

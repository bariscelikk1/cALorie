import { describe, expect, it } from "vitest";
import { isExercise, isValidStorageKey, isValidWeight } from "../lib/validation";

describe("request validation", () => {
  it("accepts only supported exercises", () => {
    expect(isExercise("squat")).toBe(true);
    expect(isExercise("running")).toBe(false);
  });

  it("enforces a reasonable body-weight range", () => {
    expect(isValidWeight(70)).toBe(true);
    expect(isValidWeight(0)).toBe(false);
    expect(isValidWeight(Number.NaN)).toBe(false);
    expect(isValidWeight(300)).toBe(false);
  });

  it("rejects arbitrary storage paths", () => {
    expect(isValidStorageKey("uploads/123e4567-e89b-42d3-a456-426614174000.mp4")).toBe(true);
    expect(isValidStorageKey("../private/secret.mp4")).toBe(false);
    expect(isValidStorageKey("uploads/not-a-uuid.mp4")).toBe(false);
  });
});

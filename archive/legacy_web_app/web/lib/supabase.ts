import { createClient } from "@supabase/supabase-js";
import "server-only";

// Server-only client (service role key) — never import this from client components.
export function supabaseAdmin() {
  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_ROLE_KEY) {
    throw new Error("Supabase server environment variables are not configured");
  }
  return createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
}

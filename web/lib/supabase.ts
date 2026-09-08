import { createClient } from "@supabase/supabase-js";

// Server-only client (service role key) — never import this from client components.
export function supabaseAdmin() {
  return createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
}

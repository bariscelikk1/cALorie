import "server-only";

const BUCKET = "workout-videos";

/**
 * Supabase Storage's signed-upload endpoint accepts a plain PUT with the
 * token as a query param, so the browser never needs the Supabase JS client.
 */
export async function createUploadUrl(key: string) {
  const res = await fetch(
    `${process.env.SUPABASE_URL}/storage/v1/object/upload/sign/${BUCKET}/${key}`,
    {
      method: "POST",
      headers: {
        apikey: process.env.SUPABASE_SERVICE_ROLE_KEY!,
        Authorization: `Bearer ${process.env.SUPABASE_SERVICE_ROLE_KEY}`,
        "Content-Type": "application/json",
      },
      body: "{}",
    }
  );

  if (!res.ok) {
    throw new Error(`Failed to create upload URL: ${res.status}`);
  }

  const { url } = await res.json();
  return `${process.env.SUPABASE_URL}/storage/v1${url}`;
}

export async function objectExists(key: string) {
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;
  const res = await fetch(
    `${process.env.SUPABASE_URL}/storage/v1/object/${BUCKET}/${key}`,
    {
      method: "HEAD",
      headers: { apikey: serviceKey, Authorization: `Bearer ${serviceKey}` },
      cache: "no-store",
    },
  );
  return res.ok;
}

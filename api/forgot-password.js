import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).send("Method Not Allowed");

  const { email } = req.body;

  try {
    const { data, error } = await supabase.auth.resetPasswordForEmail(email);

    if (error) return res.status(400).json({ error: error.message });

    return res.status(200).json({
      message: "Password reset link sent to your email.",
      data,
    });
  } catch (err) {
    console.error("Reset error:", err);
    return res.status(500).json({ error: "Internal server error" });
  }
}

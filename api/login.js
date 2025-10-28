import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.SUPABASE_URL, 
  process.env.SUPABASE_KEY
);

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method Not Allowed" });
  }

  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ message: "Missing email or password." });
  }

  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      console.error("Supabase auth error:", error);
      return res.status(401).json({ message: error.message });
    }

    // Supabase sends user confirmation info differently
    if (!data?.user?.email_confirmed_at) {
      return res
        .status(403)
        .json({ message: "Please confirm your email before logging in." });
    }

    return res.status(200).json({
      message: "Login successful!",
      user: data.user,
      session: data.session,
    });
  } catch (err) {
    console.error("Server error:", err);
    return res.status(500).json({ message: "Internal server error" });
  }
}

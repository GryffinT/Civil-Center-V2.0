import { createClient } from "@supabase/supabase-js";

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ message: "Method not allowed" });

  const { userId, password } = req.body;
  if (!userId || !password) return res.status(400).json({ message: "Missing userId or password" });

  try {
    // Find center by password
    const { data: center, error: fetchError } = await supabase
      .from("centers")
      .select("*")
      .eq("password", password)
      .single();

    if (fetchError || !center) return res.status(400).json({ message: "No center found with this password." });

    // Increment member count
    await supabase
      .from("centers")
      .update({ members: center.members + 1 })
      .eq("id", center.id);

    // Add center ID to user metadata
    const { data: userData } = await supabase.auth.admin.getUserById(userId);
    const currentCenters = (userData.user_metadata?.centers) || [];
    await supabase.auth.admin.updateUserById(userId, {
      user_metadata: { centers: [...currentCenters, center.id] }
    });

    return res.status(200).json({ message: `Successfully joined center "${center.name}"!` });

  } catch (err) {
    console.error(err);
    return res.status(500).json({ message: "Server error: " + err.message });
  }
}

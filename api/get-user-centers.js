import { createClient } from "@supabase/supabase-js";

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method not allowed" });
  }

  const { userId } = req.body;
  if (!userId) return res.status(400).json({ message: "Missing userId" });

  try {
    const { data: userData, error: userError } = await supabase.auth.admin.getUserById(userId);
    if (userError || !userData) return res.status(400).json({ message: "Unable to fetch user" });

    const centerIds = userData.user_metadata?.centers || [];

    if (centerIds.length === 0) {
      return res.status(200).json({ centers: [] }); // No centers
    }

    const { data: centers, error: centersError } = await supabase
      .from("centers")
      .select("*")
      .in("id", centerIds);

    if (centersError) return res.status(500).json({ message: centersError.message });

    return res.status(200).json({ centers });

  } catch (err) {
    console.error(err);
    return res.status(500).json({ message: "Server error: " + err.message });
  }
}

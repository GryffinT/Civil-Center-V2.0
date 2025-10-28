import { createClient } from "@supabase/supabase-js";

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ message: "Method not allowed" });

  const { userId, password } = req.body;
  if (!userId || !password) return res.status(400).json({ message: "Missing userId or password" });

  try {
    const { data: center, error: fetchError } = await supabase
      .from("centers")
      .select("*")
      .eq("password", password)
      .single();

    if (fetchError || !center) return res.status(400).json({ message: "No center found with this password." });

    const { data: existingMember, error: memberError } = await supabase
      .from("center_members")
      .select("*")
      .eq("center_id", center.id)
      .eq("user_id", userId)
      .single();

    if (existingMember) return res.status(400).json({ message: "You are already a member of this center." });

    const { error: updateError } = await supabase
      .from("centers")
      .update({ members: center.members + 1 })
      .eq("id", center.id);

    if (updateError) throw updateError;

    const { error: insertMemberError } = await supabase
      .from("center_members")
      .insert([{ user_id: userId, center_id: center.id }]);

    if (insertMemberError) throw insertMemberError;

    return res.status(200).json({ message: `Successfully joined center "${center.name}"!` });

  } catch (err) {
    console.error(err);
    return res.status(500).json({ message: "Server error: " + err.message });
  }
}

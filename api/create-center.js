import { createClient } from "@supabase/supabase-js";

// Create Supabase client
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method not allowed" });
  }

  const { userId, name, password, description } = req.body;

  if (!userId || !name || !password || !description) {
    console.error("Missing required fields:", req.body);
    return res.status(400).json({ message: "Missing required fields." });
  }

  try {
    const centerId = Math.random().toString(36).substring(2, 10);
    console.log("Creating center with ID:", centerId);

    const { data: centerData, error: centerError } = await supabase
      .from("centers")
      .insert([
        {
          id: centerId,
          name,
          password,
          description,
          members: 1,
          posts: JSON.stringify([]),
        },
      ])
      .select();

    if (centerError) {
      console.error("Error inserting center:", centerError);
      return res.status(500).json({ message: "Failed to create center.", error: centerError });
    }

    console.log("Center created:", centerData);

    const { data: memberData, error: memberError } = await supabase
      .from("center_members")
      .insert([{ user_id: userId, center_id: centerId }])
      .select();

    if (memberError) {
      console.error("Error inserting into center_members:", memberError);
      return res.status(500).json({ message: "Failed to add creator to center_members.", error: memberError });
    }

    console.log("User added to center_members:", memberData);

    return res.status(200).json({
      message: `Center "${name}" created successfully!`,
      id: centerId,
    });

  } catch (err) {
    console.error("Unexpected server error:", err);
    return res.status(500).json({ message: "Server error: " + err.message });
  }
}

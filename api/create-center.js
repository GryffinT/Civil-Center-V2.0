import { createClient } from "@supabase/supabase-js";

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);

export default async function handler(req, res) {
  if (req.method === "POST") {
    const { name, password, description } = req.body;

    const data = {
      id: Math.random().toString(36).substring(2, 10),
      name,
      password,
      description,
      members: 1
    };

    const { error } = await supabase.from("centers").insert([data]);

    if (error) return res.status(400).json({ message: error.message });

    return res.status(200).json({ message: `Center "${name}" created successfully!` });
  } else {
    res.status(405).json({ message: "Method not allowed" });
  }
}

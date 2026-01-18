import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";

interface Doc {
  id: number;
  title: string;
  created_at: string;
  user_id: number;
  document_uuids: string[];
}

export const DisplayDocs = () => {
  const [loading, setLoading] = useState(false);
  const [docs, setDocs] = useState<Doc[]>([]);

  async function fetchDocs() {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/documents/all", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      const data = await response.json();
      console.log("Fetched data:", data);
      setDocs(data.documents);
    } catch (error) {
      console.error("Error fetching documents:", error);
      setDocs([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchDocs();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Your Documents</h1>
      <div className="grid grid-cols-3 gap-4">
        {docs && docs.length > 0 ? (
          docs.map((doc) => (
            <div key={doc.id} className="">
              <Button>{doc.title}</Button>
            </div>
          ))
        ) : (
          <div>No documents found</div>
        )}
      </div>
    </div>
  );
};

import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { CiText } from "react-icons/ci";

import { DocumentUpload } from "./DocumentUpload";
import { Chat } from "./Chat";
import { DisplayDocs } from "./DisplayDocs";

function Dashboard() {
  const navigate = useNavigate();
  const [showChat, setShowChat] = useState(false);

  useEffect(() => {
    const verifyToken = async () => {
      const token = localStorage.getItem("token");
      try {
        const response = await fetch(
          `http://localhost:8000/auth/verify_token/${token}`,
        );
        if (!response.ok) {
          throw new Error("Token verification failed");
        }
      } catch (error) {
        console.error("Error verifying token:", error);
        localStorage.removeItem("token");
        navigate("/auth/signin");
      }
    };

    verifyToken();
  }, [navigate]);

  return (
    <div className="px-6 py-4">
      {/* Logo Section */}
      <div className="flex items-center gap-2">
        <CiText size={28} />
        <div className="text-2xl font-medium">
          Cite
          <span className="text-gray-300 font-extralight"> Base</span>
        </div>
      </div>

      {/* Document Upload Section */}
      {!showChat ? (
        <div className="min-h-screen flex flex-col gap-6 pt-8">
          <div className="self-start pl-6">
            <DisplayDocs />
          </div>
          <div className="flex justify-center items-center flex-1">
            <DocumentUpload onUploadSuccess={() => setShowChat(true)} />
          </div>
        </div>
      ) : (
        <div className="min-h-screen flex justify-center items-center">
          <Chat />
        </div>
      )}
    </div>
  );
}
export default Dashboard;

import { useEffect } from "react";
import { useNavigate } from "react-router";
import { CiText } from "react-icons/ci";

import { DocumentUpload } from "./DocumentUpload";

function Dashboard() {
  const navigate = useNavigate();

  useEffect(() => {
    const verifyToken = async () => {
      const token = localStorage.getItem("token");
      try {
        const response = await fetch(
          `http://localhost:8000/auth/verify_token/${token}`
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
      <div className="min-h-screen flex justify-center items-center">
        <DocumentUpload />
      </div>
    </div>
  );
}
export default Dashboard;

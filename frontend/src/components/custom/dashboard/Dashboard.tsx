import { useEffect } from "react";
import { useNavigate } from "react-router";

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

  return <div>Dashboard</div>;
}
export default Dashboard;

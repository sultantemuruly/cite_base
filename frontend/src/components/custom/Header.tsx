import { useNavigate } from "react-router";

import { CiText } from "react-icons/ci";
import { Button } from "@/components/ui/button";

function Header() {
  const navigate = useNavigate();

  const redirectToSignin = () => {
    navigate("/auth/signin");
  };

  const redirectToSignup = () => {
    navigate("/auth/signup");
  };

  return (
    <div className="bg-[#0E1112] px-6 py-4 outline-1 outline-gray-500 shadow-md flex items-center justify-between">
      {/* Logo Section */}
      <div className="flex items-center gap-2">
        <CiText size={28} />
        <div className="text-2xl font-medium">
          Cite
          <span className="text-gray-300 font-extralight"> Base</span>
        </div>
      </div>

      {/* Sign In Section */}
      <div className="flex items-center justify-center gap-4">
        <div>
          <Button variant={"default"} onClick={redirectToSignin}>
            Sign In
          </Button>
        </div>
        <div>
          <Button variant={"secondary"} onClick={redirectToSignup}>
            Sign Up
          </Button>
        </div>
      </div>
    </div>
  );
}
export default Header;

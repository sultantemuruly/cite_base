import { Outlet, useNavigate } from "react-router";

import { CiText } from "react-icons/ci";
import { IoMdArrowRoundBack } from "react-icons/io";
import { Button } from "@/components/ui/button";

export default function AuthLayout() {
  const navigate = useNavigate();

  const handleGoBack = () => {
    navigate("/");
  };

  return (
    <div className="py-4 px-6 bg-[#0E1112]">
      {/* Logo Section */}
      <div className="flex items-center gap-4">
        <div>
          <Button onClick={handleGoBack}>
            <IoMdArrowRoundBack />
            Back
          </Button>
        </div>
        <div className="flex items-center gap-2">
          <CiText size={28} />
          <div className="text-2xl font-medium">
            Cite
            <span className="text-gray-300 font-extralight"> Base</span>
          </div>
        </div>
      </div>
      <div className="min-h-screen flex flex-col justify-center items-center bg-[#0F1011]">
        <Outlet />
      </div>
    </div>
  );
}

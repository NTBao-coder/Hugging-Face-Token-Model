import { useState } from "react";
import { Globe, Menu, User } from "lucide-react";

export function TopNav() {
  const [activeTab, setActiveTab] = useState<"homes" | "experiences" | "services">("homes");

  return (
    <header className="sticky top-0 z-40 h-[80px] w-full border-b border-hairline bg-canvas px-6 md:px-12 flex items-center justify-between text-ink select-none">
      {/* Brand Logo */}
      <div className="flex items-center gap-1.5 cursor-pointer">
        <svg
          viewBox="0 0 32 32"
          xmlns="http://www.w3.org/2000/svg"
          aria-label="Airbnb homepage"
          className="h-[32px] w-[32px] fill-rausch"
        >
          <path d="M16 1c2.008 0 3.463.963 4.751 3.269l.533 1.025c1.954 3.83 6.114 12.54 7.1 14.836l.145.353c.667 1.591.91 2.472.96 3.396l.01.415.001.228c0 4.062-2.877 6.478-6.357 6.478-2.224 0-4.556-1.258-6.708-3.386l-.257-.26-.172-.178a25.43 25.43 0 0 1-1.748-2.072 25.43 25.43 0 0 1-1.748 2.072l-.172.178-.257.26C12.456 29.742 10.124 31 7.9 31c-3.48 0-6.358-2.416-6.358-6.478l.002-.228c.05-.924.293-1.805.96-3.396l.145-.353c.986-2.296 5.146-11.006 7.1-14.836l.533-1.025C11.537 1.963 12.992 1 15 1zm0 2c-1.144 0-1.92.517-2.903 2.277L12.56 6.3c-1.92 3.765-6.046 12.408-7.017 14.673l-.155.38c-.544 1.299-.716 1.924-.753 2.502l-.008.239v.088c0 2.875 1.905 4.818 4.373 4.818 1.51 0 3.38-1.018 5.34-3.153l.235-.262.155-.178c1.378-1.614 2.656-3.376 3.197-4.156l.088-.129.088.129c.54 1.056 1.819 2.818 3.197 4.156l.155.178.235.262c1.96 2.135 3.83 3.153 5.34 3.153 2.468 0 4.373-1.943 4.373-4.818v-.088l-.008-.239c-.037-.578-.209-1.203-.753-2.502l-.155-.38c-.971-2.265-5.097-10.908-7.017-14.673l-.537-1.023C17.92 3.517 17.144 3 16 3zm0 9c2.316 0 4.225 1.77 4.542 4.053l.019.26-.002.26a4.57 4.57 0 0 1-4.299 4.421l-.26.007-.26-.007a4.57 4.57 0 0 1-4.299-4.421l-.002-.26.019-.26C11.775 13.77 13.684 12 16 12zm0 2c-1.298 0-2.378.966-2.553 2.222l-.007.16.007.16c.175 1.256 1.255 2.222 2.553 2.222 1.298 0 2.378-.966 2.553-2.222l.007-.16-.007-.16c-.175-1.256-1.255-2.222-2.553-2.222z" />
        </svg>
        <span className="hidden lg:block text-rausch font-bold text-[20px] tracking-tight">airbnb</span>
      </div>

      {/* Product Tabs (Centered) */}
      <nav className="flex items-center gap-6 md:gap-8">
        <button
          onClick={() => setActiveTab("homes")}
          className={[
            "relative pb-1.5 text-[16px] font-semibold transition-colors duration-150",
            activeTab === "homes" ? "text-ink border-b-2 border-ink" : "text-muted hover:text-ink",
          ].join(" ")}
        >
          Nơi lưu trú (Homes)
        </button>

        <button
          onClick={() => setActiveTab("experiences")}
          className={[
            "relative pb-1.5 text-[16px] font-semibold transition-colors duration-150",
            activeTab === "experiences" ? "text-ink border-b-2 border-ink" : "text-muted hover:text-ink",
          ].join(" ")}
        >
          Trải nghiệm (Experiences)
          <span className="absolute -top-1.5 -right-6 rounded-full bg-rausch px-1.5 py-0.5 text-[8px] font-bold text-white uppercase tracking-wider scale-90">
            NEW
          </span>
        </button>

        <button
          onClick={() => setActiveTab("services")}
          className={[
            "relative pb-1.5 text-[16px] font-semibold transition-colors duration-150",
            activeTab === "services" ? "text-ink border-b-2 border-ink" : "text-muted hover:text-ink",
          ].join(" ")}
        >
          Dịch vụ (Services)
          <span className="absolute -top-1.5 -right-6 rounded-full bg-rausch px-1.5 py-0.5 text-[8px] font-bold text-white uppercase tracking-wider scale-90">
            NEW
          </span>
        </button>
      </nav>

      {/* Account Utilities (Right) */}
      <div className="flex items-center gap-4">
        <span className="hidden md:inline-block text-[14px] font-semibold hover:bg-surface-soft px-3 py-2 rounded-full cursor-pointer transition-colors duration-150">
          Trở thành chủ nhà
        </span>

        <button
          aria-label="Chọn ngôn ngữ"
          className="flex h-10 w-10 items-center justify-center rounded-full hover:bg-surface-soft transition-colors duration-150"
        >
          <Globe className="h-[18px] w-[18px]" />
        </button>

        {/* Account Menu Trigger */}
        <div className="flex items-center gap-3 border border-hairline rounded-full pl-3 pr-1.5 py-1.5 hover:shadow-md cursor-pointer transition-all bg-canvas">
          <Menu className="h-[16px] w-[16px]" />
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-muted text-canvas">
            <User className="h-[16px] w-[16px]" />
          </div>
        </div>
      </div>
    </header>
  );
}

export default TopNav;

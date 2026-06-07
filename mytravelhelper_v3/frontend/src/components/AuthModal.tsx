import { useState } from "react";
import { X, Mail, Lock, User } from "lucide-react";

type AuthModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (userData: { email: string; displayName: string; token: string; uid: string }) => void;
};

export function AuthModal({ isOpen, onClose, onSuccess }: AuthModalProps) {
  const [tab, setTab] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const url = tab === "login" 
      ? "http://localhost:8000/api/auth/login" 
      : "http://localhost:8000/api/auth/register";

    const payload = tab === "login"
      ? { email, password }
      : { email, password, display_name: displayName };

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Đã xảy ra lỗi xác thực");
      }

      if (tab === "login") {
        onSuccess({
          email: data.email,
          displayName: data.display_name,
          token: data.id_token,
          uid: data.uid,
        });
        onClose();
      } else {
        // Registration success, switch to login tab and notify
        alert("Đăng ký tài khoản thành công! Vui lòng đăng nhập lại.");
        setTab("login");
        setPassword("");
      }
    } catch (err: any) {
      setError(err.message || "Không thể kết nối với máy chủ");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 select-none">
      {/* Modal Card */}
      <div className="relative w-full max-w-[420px] bg-canvas rounded-lg shadow-xl border border-hairline p-6 text-ink flex flex-col">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full hover:bg-surface-soft text-ink transition-colors border border-hairline bg-canvas shadow-sm"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Modal Title */}
        <div className="text-center mb-6">
          <h2 className="text-[22px] font-bold font-sans tracking-tight">
            {tab === "login" ? "Đăng nhập tài khoản" : "Tạo tài khoản mới"}
          </h2>
          <p className="text-[12px] text-muted mt-1.5">
            Trải nghiệm đặt vé và thanh toán VNPAY Sandbox nhanh chóng
          </p>
        </div>

        {/* Tab Switchers */}
        <div className="grid grid-cols-2 gap-2 border border-hairline p-1 rounded-full mb-6 bg-surface-soft/40">
          <button
            onClick={() => { setTab("login"); setError(null); }}
            className={`py-1.5 text-[13px] font-semibold rounded-full transition-all ${
              tab === "login" ? "bg-canvas text-ink shadow-sm border border-hairline" : "text-muted hover:text-ink"
            }`}
          >
            Đăng nhập
          </button>
          <button
            onClick={() => { setTab("register"); setError(null); }}
            className={`py-1.5 text-[13px] font-semibold rounded-full transition-all ${
              tab === "register" ? "bg-canvas text-ink shadow-sm border border-hairline" : "text-muted hover:text-ink"
            }`}
          >
            Đăng ký
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-500 rounded-lg text-[13px] font-medium leading-relaxed">
            ⚠️ {error}
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {tab === "register" && (
            <div className="space-y-1">
              <label className="text-[11px] font-bold text-ink uppercase tracking-wider block">Tên hiển thị</label>
              <div className="relative">
                <User className="absolute left-3.5 top-3.5 h-[15px] w-[15px] text-muted" />
                <input
                  type="text"
                  required
                  placeholder="Nguyen Van A"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  className="w-full h-10 pl-10 pr-4 rounded-full border border-hairline bg-canvas text-ink text-[13px] focus:outline-none focus:border-black focus:ring-2 focus:ring-blue-500/20 transition-all"
                />
              </div>
            </div>
          )}

          <div className="space-y-1">
            <label className="text-[11px] font-bold text-ink uppercase tracking-wider block">Địa chỉ Email</label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-3.5 h-[15px] w-[15px] text-muted" />
              <input
                type="email"
                required
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full h-10 pl-10 pr-4 rounded-full border border-hairline bg-canvas text-ink text-[13px] focus:outline-none focus:border-black focus:ring-2 focus:ring-blue-500/20 transition-all"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-bold text-ink uppercase tracking-wider block">Mật khẩu</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3.5 h-[15px] w-[15px] text-muted" />
              <input
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full h-10 pl-10 pr-4 rounded-full border border-hairline bg-canvas text-ink text-[13px] focus:outline-none focus:border-black focus:ring-2 focus:ring-blue-500/20 transition-all"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full h-10 bg-black text-white font-semibold text-[13px] rounded-full hover:bg-neutral-800 transition-all active:scale-[0.98] mt-2 disabled:bg-neutral-200 disabled:text-neutral-400"
          >
            {loading ? "Đang xử lý..." : tab === "login" ? "Đăng nhập" : "Đăng ký tài khoản"}
          </button>
        </form>
      </div>
    </div>
  );
}

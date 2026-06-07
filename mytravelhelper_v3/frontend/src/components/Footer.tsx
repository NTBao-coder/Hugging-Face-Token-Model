import { Globe } from "lucide-react";

export function Footer() {
  return (
    <footer className="w-full border-t border-hairline bg-canvas text-ink py-12 px-6 md:px-12 select-none">
      
      {/* 3-Column link grid */}
      <div className="max-w-[1280px] mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 pb-10">
        
        {/* Col 1: Hỗ trợ */}
        <div className="space-y-4">
          <h4 className="text-[14px] font-bold uppercase tracking-wider text-ink">Hỗ trợ</h4>
          <ul className="space-y-2.5 text-[14px] text-body">
            <li><a href="#" className="hover:underline">Trung tâm trợ giúp</a></li>
            <li><a href="#" className="hover:underline">AirCover</a></li>
            <li><a href="#" className="hover:underline">Chống phân biệt đối xử</a></li>
            <li><a href="#" className="hover:underline">Hỗ trợ người khuyết tật</a></li>
            <li><a href="#" className="hover:underline">Các tùy chọn hủy</a></li>
            <li><a href="#" className="hover:underline">Báo cáo lo ngại của khu dân cư</a></li>
          </ul>
        </div>

        {/* Col 2: Đón tiếp khách */}
        <div className="space-y-4">
          <h4 className="text-[14px] font-bold uppercase tracking-wider text-ink">Đón tiếp khách</h4>
          <ul className="space-y-2.5 text-[14px] text-body">
            <li><a href="#" className="hover:underline">Cho thuê nhà trên Airbnb</a></li>
            <li><a href="#" className="hover:underline">AirCover cho Chủ nhà</a></li>
            <li><a href="#" className="hover:underline">Tài nguyên về đón tiếp khách</a></li>
            <li><a href="#" className="hover:underline">Diễn đàn cộng đồng</a></li>
            <li><a href="#" className="hover:underline">Đón tiếp khách có trách nhiệm</a></li>
            <li><a href="#" className="hover:underline">Tham gia lớp học đón khách miễn phí</a></li>
          </ul>
        </div>

        {/* Col 3: Airbnb */}
        <div className="space-y-4">
          <h4 className="text-[14px] font-bold uppercase tracking-wider text-ink">Airbnb</h4>
          <ul className="space-y-2.5 text-[14px] text-body">
            <li><a href="#" className="hover:underline">Trang tin tức</a></li>
            <li><a href="#" className="hover:underline">Tính năng mới</a></li>
            <li><a href="#" className="hover:underline">Cơ hội việc làm</a></li>
            <li><a href="#" className="hover:underline">Nhà đầu tư</a></li>
            <li><a href="#" className="hover:underline">Chỗ ở khẩn cấp Airbnb.org</a></li>
          </ul>
        </div>

      </div>

      {/* Legal Band Divider */}
      <div className="w-full border-t border-hairline-soft max-w-[1280px] mx-auto pt-6 flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Left copyright and links */}
        <div className="flex flex-wrap items-center justify-center md:justify-start gap-x-3 gap-y-1.5 text-[13px] text-muted font-normal">
          <span>© 2026 MyTravelHelper, Inc.</span>
          <span className="text-muted/40 hidden md:inline">·</span>
          <a href="#" className="hover:underline">Quyền riêng tư</a>
          <span className="text-muted/40">·</span>
          <a href="#" className="hover:underline">Điều khoản</a>
          <span className="text-muted/40">·</span>
          <a href="#" className="hover:underline">Sơ đồ trang web</a>
        </div>

        {/* Right Pickers & Socials */}
        <div className="flex items-center gap-6">
          
          {/* Language & Currency picker */}
          <div className="flex items-center gap-4 text-[13px] font-semibold text-ink">
            <a href="#" className="hover:underline flex items-center gap-1.5">
              <Globe className="h-[15px] w-[15px]" /> Tiếng Việt (VN)
            </a>
            <a href="#" className="hover:underline">₫ VND</a>
          </div>

          {/* Social icons */}
          <div className="flex items-center gap-4 text-ink">
            <a href="#" aria-label="Facebook link" className="hover:opacity-80 transition-opacity">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-facebook"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>
            </a>
            <a href="#" aria-label="Twitter link" className="hover:opacity-80 transition-opacity">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-twitter"><path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z"/></svg>
            </a>
            <a href="#" aria-label="Instagram link" className="hover:opacity-80 transition-opacity">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-instagram"><rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/></svg>
            </a>
          </div>

        </div>

      </div>

    </footer>
  );
}

export default Footer;

import { X, Star, Shield, Award, ChevronDown, Check } from "lucide-react";

type Destination = {
  id: string;
  name: string;
  imageUrl: string;
  rating: number;
  reviewCount: number;
  price: string;
  distance: string;
  dates: string;
  category: string;
  description: string;
};

type ListingDetailModalProps = {
  isOpen: boolean;
  onClose: () => void;
  destination: Destination | null;
  onReserve: (dest: Destination, totalAmount: number) => void;
  loading: boolean;
};

export function ListingDetailModal({
  isOpen,
  onClose,
  destination,
  onReserve,
  loading,
}: ListingDetailModalProps) {
  if (!isOpen || !destination) return null;

  // Parse price string to integer (e.g. "2.350.000 ₫" -> 2350000)
  const basePrice = parseInt(destination.price.replace(/[^0-9]/g, ""), 10) || 0;
  const nights = 5;
  const cleaningFee = 150000;
  const totalAmount = basePrice * nights + cleaningFee;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 overflow-y-auto">
      {/* Modal Card */}
      <div className="relative w-full max-w-[1080px] bg-canvas rounded-lg shadow-xl flex flex-col max-h-[90vh] overflow-y-auto border border-hairline">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 z-10 flex h-10 w-10 items-center justify-center rounded-full hover:bg-surface-soft text-ink transition-colors border border-hairline bg-canvas shadow-sm"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Hero image banner */}
        <div className="w-full h-[320px] md:h-[380px] overflow-hidden rounded-t-lg relative">
          <img
            src={destination.imageUrl}
            alt={destination.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
          <div className="absolute bottom-6 left-6 md:left-12 text-white">
            <span className="bg-canvas text-ink text-[11px] font-bold rounded-full px-3 py-1 shadow-sm mb-2 inline-block">
              ★ Khách thích nhất
            </span>
            <h1 className="text-[26px] font-bold leading-tight tracking-normal text-white">
              {destination.name}
            </h1>
            <p className="text-[13px] text-neutral-300 mt-1">{destination.distance} · {destination.dates}</p>
          </div>
        </div>

        {/* Content Layout Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 px-6 md:px-12 py-8 text-ink bg-canvas">
          
          {/* Left Column (Amenities, Stats, Host, Reviews) */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* Signature Rating Display Card */}
            <div className="flex flex-col items-center justify-center p-6 border border-hairline rounded-lg text-center bg-surface-soft/60 relative">
              <div className="flex items-center gap-6">
                {/* Left laurel wreath */}
                <svg className="w-10 h-10 text-ink opacity-30 transform -scale-x-100" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8zm-1-12.41a1 1 0 0 1 .55-.89l2-1A1 1 0 1 1 14.35 5.5l-2 1a1 1 0 0 1-1.35-.59zm-1.8 2.6a1 1 0 0 1 .15-1.05l1.5-1.5a1 1 0 0 1 1.4 1.41L10.75 10a1 1 0 0 1-1.55-.21zm-1 3a1 1 0 0 1-.25-1.15l1-2a1 1 0 1 1 1.8.9l-1 2a1 1 0 0 1-1.55.25z" />
                </svg>
                
                {/* Big rating text */}
                <span className="text-[54px] font-bold tracking-tighter leading-none text-ink">
                  {destination.rating.toFixed(2)}
                </span>
                
                {/* Right laurel wreath */}
                <svg className="w-10 h-10 text-ink opacity-30" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8zm-1-12.41a1 1 0 0 1 .55-.89l2-1A1 1 0 1 1 14.35 5.5l-2 1a1 1 0 0 1-1.35-.59zm-1.8 2.6a1 1 0 0 1 .15-1.05l1.5-1.5a1 1 0 0 1 1.4 1.41L10.75 10a1 1 0 0 1-1.55-.21zm-1 3a1 1 0 0 1-.25-1.15l1-2a1 1 0 1 1 1.8.9l-1 2a1 1 0 0 1-1.55.25z" />
                </svg>
              </div>
              <div className="font-semibold text-[15px] mt-2">Khách thích nhất</div>
              <div className="text-[12px] text-muted font-normal mt-1">
                Một trong những địa điểm được yêu thích nhất dựa trên xếp hạng và độ tin cậy.
              </div>
            </div>

            {/* Description Card */}
            <div>
              <h3 className="text-[18px] font-semibold tracking-tight mb-2">Giới thiệu về chỗ ở</h3>
              <p className="text-[14px] text-body leading-relaxed">{destination.description}</p>
            </div>

            {/* Amenity Rows */}
            <div className="border-t border-b border-hairline py-5">
              <h3 className="text-[18px] font-semibold tracking-tight mb-4">Tiện nghi chỗ ở</h3>
              <div className="grid grid-cols-2 gap-y-3">
                {[
                  "Wifi tốc độ cao miễn phí",
                  "Bể bơi ngoài trời",
                  "Bữa sáng phục vụ tận phòng",
                  "Cho phép mang thú cưng",
                  "Điều hòa & Máy sưởi",
                  "Chỗ đỗ xe miễn phí",
                ].map((amenity, idx) => (
                  <div key={idx} className="flex items-center gap-3 py-1 text-[14px] text-body">
                    <Check className="h-4 w-4 text-ink" />
                    <span>{amenity}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Host Card */}
            <div className="bg-surface-soft rounded-lg p-5 border border-hairline flex flex-col md:flex-row gap-5 items-start justify-between">
              <div className="flex gap-4">
                <div className="h-11 w-11 rounded-full bg-neutral-200 border border-hairline flex items-center justify-center font-bold text-ink text-[16px]">
                  MT
                </div>
                <div>
                  <h4 className="text-[15px] font-semibold leading-none">Host: MyTravelHelper Superhost</h4>
                  <p className="text-[12px] text-muted mt-2 flex items-center gap-1">
                    <Award className="h-3.5 w-3.5 text-ink inline" /> Superhost · 5 năm kinh nghiệm chủ nhà
                  </p>
                  <p className="text-[12px] text-muted mt-0.5">Tỷ lệ phản hồi: 100% (trong vòng 1 giờ)</p>
                </div>
              </div>
              <button className="h-9 px-4 border border-hairline text-ink hover:bg-canvas rounded-full text-[13px] font-medium tracking-normal transition-colors bg-canvas">
                Liên hệ chủ nhà
              </button>
            </div>

            {/* Reviews Card Excerpt (2 Column Grid) */}
            <div>
              <h3 className="text-[18px] font-semibold tracking-tight mb-4">Đánh giá nổi bật</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[
                  {
                    name: "Thanh Bảo",
                    date: "Tháng 5 năm 2026",
                    comment: "Trải nghiệm tuyệt vời! Phòng ốc sạch sẽ, vị trí trung tâm di chuyển dễ dàng, sẽ quay lại lần sau.",
                  },
                  {
                    name: "Alex Johnson",
                    date: "Tháng 4 năm 2026",
                    comment: "Very spacious room, peaceful atmosphere. The pool was amazing. Highly recommend exploring this area.",
                  },
                ].map((review, idx) => (
                  <div key={idx} className="space-y-2 p-4 border border-hairline rounded-lg bg-canvas">
                    <div className="flex gap-3">
                      <div className="h-8 w-8 rounded-full bg-neutral-100 flex items-center justify-center font-semibold text-[12px] border border-hairline">
                        {review.name[0]}
                      </div>
                      <div>
                        <div className="text-[13px] font-semibold">{review.name}</div>
                        <div className="text-[11px] text-muted">{review.date}</div>
                      </div>
                    </div>
                    <p className="text-[13px] text-body leading-relaxed line-clamp-3">
                      "{review.comment}"
                    </p>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* Right Column (Sticky Reservation Card) */}
          <div className="lg:col-span-1">
            <div className="border border-hairline rounded-lg p-6 bg-canvas shadow-sm space-y-5 sticky top-24">
              
              {/* Header Pricing info */}
              <div className="flex justify-between items-end">
                <span className="text-[20px] font-bold tracking-tight text-ink">
                  {destination.price}
                  <span className="text-[13px] font-normal text-muted"> / đêm</span>
                </span>
                <span className="text-[12px] text-muted font-medium underline flex items-center gap-1">
                  <Star className="h-3 w-3 fill-ink stroke-none inline" /> {destination.rating.toFixed(1)} · {destination.reviewCount} đánh giá
                </span>
              </div>

              {/* Date & Guest Selectors */}
              <div className="border border-hairline rounded-lg overflow-hidden divide-y divide-hairline bg-canvas">
                
                {/* Date Inputs */}
                <div className="grid grid-cols-2 divide-x divide-hairline">
                  <div className="p-3 cursor-pointer hover:bg-surface-soft transition-colors">
                    <label className="text-[9px] font-bold text-ink uppercase block">Nhận phòng</label>
                    <span className="text-[12px] text-body">12/06/2026</span>
                  </div>
                  <div className="p-3 cursor-pointer hover:bg-surface-soft transition-colors">
                    <label className="text-[9px] font-bold text-ink uppercase block">Trả phòng</label>
                    <span className="text-[12px] text-body">17/06/2026</span>
                  </div>
                </div>

                {/* Guest Input */}
                <div className="p-3 cursor-pointer hover:bg-surface-soft transition-colors flex justify-between items-center">
                  <div>
                    <label className="text-[9px] font-bold text-ink uppercase block">Khách</label>
                    <span className="text-[12px] text-body">2 khách</span>
                  </div>
                  <ChevronDown className="h-4 w-4 text-muted" />
                </div>
              </div>

              {/* Reserve button */}
              <button
                onClick={() => onReserve(destination, totalAmount)}
                disabled={loading}
                className="w-full h-11 rounded-full bg-black text-white font-semibold text-[14px] hover:bg-neutral-800 transition-all active:scale-[0.98] shadow-sm disabled:bg-neutral-200 disabled:text-neutral-400"
              >
                {loading ? "Đang xử lý đơn..." : "Đặt phòng ngay"}
              </button>

              <p className="text-[12px] text-center text-muted">Hệ thống chuyển hướng tới VNPAY Sandbox</p>

              {/* Fee Breakdown Stack */}
              <div className="space-y-3 pt-3 border-t border-hairline text-[13px]">
                <div className="flex justify-between text-body">
                  <span className="underline">{destination.price} x {nights} đêm</span>
                  <span>{(basePrice * nights).toLocaleString("vi-VN")} ₫</span>
                </div>
                <div className="flex justify-between text-body">
                  <span className="underline">Phí dịch vụ MyTravelHelper</span>
                  <span>0 ₫</span>
                </div>
                <div className="flex justify-between text-body">
                  <span className="underline">Phí vệ sinh</span>
                  <span>{cleaningFee.toLocaleString("vi-VN")} ₫</span>
                </div>
                <div className="flex justify-between font-bold text-[14px] pt-3 border-t border-hairline">
                  <span>Tổng tiền thanh toán</span>
                  <span>{totalAmount.toLocaleString("vi-VN")} ₫</span>
                </div>
              </div>

              {/* Guarantee */}
              <div className="flex items-start gap-3 p-3 rounded-lg border border-hairline bg-surface-soft/60">
                <Shield className="h-4.5 w-4.5 text-ink shrink-0 mt-0.5" />
                <div className="text-[11px] text-body leading-relaxed">
                  <span className="font-bold block text-ink">Bảo vệ toàn diện</span>
                  Mọi đơn đặt phòng đều được bảo vệ miễn phí khi chủ nhà hủy, phòng không khớp mô tả.
                </div>
              </div>

            </div>
          </div>

        </div>

      </div>
    </div>
  );
}

export default ListingDetailModal;

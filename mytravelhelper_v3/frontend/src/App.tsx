import { useState, useEffect } from "react";
import TopNav from "./components/TopNav";
import SearchBar from "./components/SearchBar";
import CategoryStrip from "./components/CategoryStrip";
import TravelDestinationCard from "./components/TravelDestinationCard";
import ListingDetailModal from "./components/ListingDetailModal";
import Footer from "./components/Footer";
import { AuthModal } from "./components/AuthModal";

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

const DESTINATIONS: Destination[] = [
  {
    id: "phu-quoc",
    name: "Resort bãi biển Phú Quốc - Sunset Beach",
    imageUrl: "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=600&q=80",
    rating: 4.88,
    reviewCount: 312,
    price: "2.350.000 ₫",
    distance: "Cách đây 320 km · Dương Đông",
    dates: "Ngày 12 - 17 thg 6",
    category: "Hotel Booking",
    description: "Khu nghỉ dưỡng sát biển, bao gồm bữa sáng buffet hàng ngày và hồ bơi vô cực ngắm hoàng hôn tuyệt đẹp."
  },
  {
    id: "da-nang",
    name: "Biệt thự hồ bơi vô cực Đà Nẵng",
    imageUrl: "https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?auto=format&fit=crop&w=600&q=80",
    rating: 4.95,
    reviewCount: 184,
    price: "4.200.000 ₫",
    distance: "Cách đây 610 km · Bán đảo Sơn Trà",
    dates: "Ngày 14 - 19 thg 6",
    category: "Hotel Booking",
    description: "Biệt thự sang trọng view trực diện biển Mỹ Khê, hồ bơi riêng tràn bờ và đầy đủ dịch vụ quản gia cao cấp."
  },
  {
    id: "sapa",
    name: "Cabin gỗ mộc mạc ngắm mây Sapa",
    imageUrl: "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=600&q=80",
    rating: 4.79,
    reviewCount: 96,
    price: "1.150.000 ₫",
    distance: "Cách đây 280 km · Bản Tả Van",
    dates: "Ngày 20 - 25 thg 6",
    category: "Hotel Booking",
    description: "Cabin bằng gỗ thông tự nhiên giữa thung lũng Mường Hoa, không gian yên tĩnh mộc mạc ngắm mây trôi bềnh bồng."
  },
  {
    id: "vung-tau",
    name: "Nhà phố sát bờ biển Vũng Tàu",
    imageUrl: "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?auto=format&fit=crop&w=600&q=80",
    rating: 4.65,
    reviewCount: 220,
    price: "1.800.000 ₫",
    distance: "Cách đây 95 km · Bãi Sau",
    dates: "Ngày 10 - 15 thg 6",
    category: "Hotel Booking",
    description: "Căn nhà phố đầy đủ tiện nghi, chỉ cách bãi tắm Bãi Sau vài bước chân, lý tưởng cho kỳ nghỉ gia đình."
  },
  {
    id: "bali",
    name: "Biệt thự rừng nhiệt đới Ubud Bali",
    imageUrl: "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=600&q=80",
    rating: 4.92,
    reviewCount: 405,
    price: "3.100.000 ₫",
    distance: "Cách đây 2.400 km · Bali, Indonesia",
    dates: "Ngày 18 - 23 thg 6",
    category: "Tour",
    description: "Tour nghỉ dưỡng trọn gói tại biệt thự võng lưới ngắm trọn thung lũng và rừng dừa nhiệt đới tại Ubud."
  },
  {
    id: "kyoto",
    name: "Nhà cổ truyền thống Machiya Kyoto",
    imageUrl: "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=600&q=80",
    rating: 4.87,
    reviewCount: 142,
    price: "2.850.000 ₫",
    distance: "Cách đây 3.600 km · Kyoto, Nhật Bản",
    dates: "Ngày 05 - 10 thg 7",
    category: "Tour",
    description: "Trải nghiệm văn hóa Nhật Bản tại ngôi nhà gỗ cổ nguyên bản trung tâm Kyoto, bao gồm vé trà đạo."
  },
  {
    id: "paris",
    name: "Căn hộ sang trọng view Tháp Eiffel",
    imageUrl: "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=600&q=80",
    rating: 4.98,
    reviewCount: 512,
    price: "6.900.000 ₫",
    distance: "Cách đây 9.800 km · Quận 7, Paris",
    dates: "Ngày 12 - 18 thg 7",
    category: "Hotel Booking",
    description: "Căn hộ ban công rộng lớn ngắm trọn cảnh Tháp Eiffel lấp lánh ban đêm, thiết kế kiểu Pháp sang trọng."
  },
  {
    id: "ha-long",
    name: "Du thuyền 5 sao trên vịnh Hạ Long",
    imageUrl: "https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=600&q=80",
    rating: 4.91,
    reviewCount: 280,
    price: "5.500.000 ₫",
    distance: "Cách đây 130 km · Vịnh Hạ Long",
    dates: "Ngày 01 - 04 thg 6",
    category: "Tour",
    description: "Tour trọn gói ẩm thực hải sản thượng hạng, chèo thuyền kayak và ngắm cảnh vịnh kỳ quan trên du thuyền 5 sao."
  },
];

type User = {
  email: string;
  displayName: string;
  token: string;
  uid: string;
};

type PaymentResult = {
  responseCode: string;
  txnRef: string;
  amount: number;
  bankCode: string;
  orderInfo: string;
  transactionNo: string;
  success: boolean;
};

export function App() {
  const [selectedDestination, setSelectedDestination] = useState<Destination | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Auth state
  const [user, setUser] = useState<User | null>(() => {
    const token = localStorage.getItem("user_token");
    const infoStr = localStorage.getItem("user_info");
    if (token && infoStr) {
      try {
        const info = JSON.parse(infoStr);
        return {
          email: info.email,
          displayName: info.displayName || info.display_name || "",
          token,
          uid: info.uid
        };
      } catch (e) {
        return null;
      }
    }
    return null;
  });
  
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [destinations, setDestinations] = useState<Destination[]>(DESTINATIONS);
  const [reserveLoading, setReserveLoading] = useState(false);

  // Payment result state
  const [paymentResult, setPaymentResult] = useState<PaymentResult | null>(null);
  const [isPaymentReceiptOpen, setIsPaymentReceiptOpen] = useState(false);

  // Fetch services on mount
  useEffect(() => {
    async function loadServices() {
      try {
        const response = await fetch("http://localhost:8000/api/services");
        if (!response.ok) {
          throw new Error("Không thể tải danh sách dịch vụ");
        }
        const data = await response.json();
        if (Array.isArray(data)) {
          const formatted = data.map((item: any) => ({
            id: item.id,
            name: item.name,
            imageUrl: item.imageUrl,
            rating: item.rating,
            reviewCount: item.reviewCount || 120,
            price: typeof item.price === "number" ? `${item.price.toLocaleString("vi-VN")} ₫` : item.price,
            distance: item.distance,
            dates: item.dates,
            category: item.category || "Hotel Booking",
            description: item.description || ""
          }));
          setDestinations(formatted);
        }
      } catch (e) {
        console.warn("Lỗi tải backend services, sử dụng dữ liệu mặc định:", e);
      }
    }
    loadServices();
  }, []);

  // Parse VNPAY callback parameters on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const responseCode = params.get("vnp_ResponseCode");
    const txnRef = params.get("vnp_TxnRef");
    if (responseCode !== null && txnRef !== null) {
      const amountRaw = params.get("vnp_Amount");
      const amount = amountRaw ? parseInt(amountRaw, 10) / 100 : 0;
      const bankCode = params.get("vnp_BankCode") || "";
      const orderInfo = params.get("vnp_OrderInfo") || "";
      const transactionNo = params.get("vnp_TransactionNo") || "";

      setPaymentResult({
        responseCode,
        txnRef,
        amount,
        bankCode,
        orderInfo: decodeURIComponent(orderInfo.replace(/\+/g, " ")),
        transactionNo,
        success: responseCode === "00"
      });
      setIsPaymentReceiptOpen(true);

      // Clear params from address bar
      const newUrl = window.location.origin + window.location.pathname;
      window.history.replaceState({}, document.title, newUrl);
    }
  }, []);

  const handleOpenDetail = (dest: Destination) => {
    setSelectedDestination(dest);
    setIsModalOpen(true);
  };

  const handleLoginSuccess = (userData: User) => {
    localStorage.setItem("user_token", userData.token);
    localStorage.setItem("user_info", JSON.stringify({
      email: userData.email,
      displayName: userData.displayName,
      uid: userData.uid
    }));
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem("user_token");
    localStorage.removeItem("user_info");
    setUser(null);
  };

  const handleReserve = async (dest: Destination, totalAmount: number) => {
    if (!user) {
      setIsModalOpen(false); // Close destination detail
      setIsAuthOpen(true); // Trigger login modal
      return;
    }

    setReserveLoading(true);
    try {
      // 1. Create order on Backend
      const orderResponse = await fetch("http://localhost:8000/api/orders/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${user.token}`
        },
        body: JSON.stringify({
          service_type: dest.category || "Hotel Booking",
          service_name: dest.name,
          amount: totalAmount
        })
      });

      const orderData = await orderResponse.json();
      if (!orderResponse.ok) {
        throw new Error(orderData.detail || "Không thể tạo đơn đặt phòng");
      }

      // 2. Create VNPAY URL
      const paymentResponse = await fetch("http://localhost:8000/api/payment/create-url", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${user.token}`
        },
        body: JSON.stringify({
          order_id: orderData.order_id,
          ip_address: "127.0.0.1" // Sandbox standard dummy IP
        })
      });

      const paymentData = await paymentResponse.json();
      if (!paymentResponse.ok) {
        throw new Error(paymentData.detail || "Không thể tạo liên kết thanh toán VNPAY");
      }

      // 3. Redirect to VNPAY Sandbox portal
      if (paymentData.payment_url) {
        window.location.href = paymentData.payment_url;
      } else {
        throw new Error("Không nhận được liên kết thanh toán từ VNPAY");
      }
    } catch (err: any) {
      alert(`⚠️ Lỗi đặt phòng: ${err.message || "Đã xảy ra lỗi hệ thống"}`);
    } finally {
      setReserveLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-canvas flex flex-col font-cereal text-ink">
      {/* 1. Header Navigation */}
      <TopNav
        user={user}
        onLoginClick={() => setIsAuthOpen(true)}
        onLogout={handleLogout}
      />

      {/* 2. Global Pill Search Bar */}
      <SearchBar />

      {/* 3. Product Categories Strip */}
      <CategoryStrip />

      {/* 4. Main content floor */}
      <main className="flex-1 max-w-[1280px] mx-auto w-full px-6 md:px-12 py-10 space-y-6">
        
        {/* Section Hero Title */}
        <h2 className="text-[28px] font-bold leading-tight tracking-normal text-ink font-cereal mb-8">
          Ý tưởng cho kỳ nghỉ tiếp theo của bạn
        </h2>

        {/* Responsive Listing Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-10">
          {destinations.map((dest) => (
            <TravelDestinationCard
              key={dest.id}
              name={dest.name}
              imageUrl={dest.imageUrl}
              rating={dest.rating}
              reviewCount={dest.reviewCount}
              price={dest.price}
              distance={dest.distance}
              dates={dest.dates}
              onExplore={() => handleOpenDetail(dest)}
            />
          ))}
        </div>

      </main>

      {/* 5. Sticky Listing Detail Drawer/Modal */}
      <ListingDetailModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedDestination(null);
        }}
        destination={selectedDestination}
        onReserve={handleReserve}
        loading={reserveLoading}
      />

      {/* 6. Firebase Auth Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onSuccess={handleLoginSuccess}
      />

      {/* 7. VNPAY Minimalist Receipt Modal */}
      {isPaymentReceiptOpen && paymentResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 select-none">
          <div className="relative w-full max-w-[420px] bg-canvas rounded-lg shadow-xl border border-hairline p-6 text-ink flex flex-col font-sans">
            
            {/* Title */}
            <div className="text-center mb-6">
              <div className={`mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-hairline mb-3 ${paymentResult.success ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}`}>
                {paymentResult.success ? '✓' : '✗'}
              </div>
              <h2 className="text-[22px] font-bold tracking-tight">
                {paymentResult.success ? "Thanh toán thành công" : "Thanh toán thất bại"}
              </h2>
              <p className="text-[12px] text-muted mt-1.5">
                {paymentResult.success ? "Cảm ơn bạn đã lựa chọn dịch vụ của chúng tôi" : "Đã xảy ra lỗi trong quá trình xử lý giao dịch"}
              </p>
            </div>

            {/* Details Stack */}
            <div className="border border-hairline rounded-lg divide-y divide-hairline bg-surface-soft/40 px-4 py-1 mb-6 text-[13px]">
              <div className="flex justify-between py-2.5">
                <span className="text-muted">Mã đơn hàng:</span>
                <span className="font-semibold font-mono">{paymentResult.txnRef}</span>
              </div>
              <div className="flex justify-between py-2.5">
                <span className="text-muted">Số tiền:</span>
                <span className="font-bold">{paymentResult.amount.toLocaleString("vi-VN")} ₫</span>
              </div>
              <div className="flex justify-between py-2.5">
                <span className="text-muted">Ngân hàng:</span>
                <span className="font-medium">{paymentResult.bankCode}</span>
              </div>
              {paymentResult.transactionNo && (
                <div className="flex justify-between py-2.5">
                  <span className="text-muted">Mã giao dịch VNPAY:</span>
                  <span className="font-mono text-[12px]">{paymentResult.transactionNo}</span>
                </div>
              )}
              <div className="flex justify-between py-2.5">
                <span className="text-muted">Nội dung:</span>
                <span className="text-right truncate max-w-[200px]">{paymentResult.orderInfo}</span>
              </div>
            </div>

            {/* Action Button */}
            <button
              onClick={() => {
                setIsPaymentReceiptOpen(false);
                setPaymentResult(null);
              }}
              className="w-full h-10 bg-black text-white font-semibold text-[13px] rounded-full hover:bg-neutral-800 transition-all active:scale-[0.98]"
            >
              Đóng hóa đơn
            </button>
          </div>
        </div>
      )}

      {/* 8. Legal Footer */}
      <Footer />
    </div>
  );
}

export default App;

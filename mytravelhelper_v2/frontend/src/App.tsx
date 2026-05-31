import { useState } from "react";
import TopNav from "./components/TopNav";
import SearchBar from "./components/SearchBar";
import CategoryStrip from "./components/CategoryStrip";
import TravelDestinationCard from "./components/TravelDestinationCard";
import ListingDetailModal from "./components/ListingDetailModal";
import Footer from "./components/Footer";

type Destination = {
  id: string;
  name: string;
  imageUrl: string;
  rating: number;
  reviewCount: number;
  price: string;
  distance: string;
  dates: string;
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
  },
];

export function App() {
  const [selectedDestination, setSelectedDestination] = useState<Destination | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleOpenDetail = (dest: Destination) => {
    setSelectedDestination(dest);
    setIsModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-canvas flex flex-col font-cereal text-ink">
      {/* 1. Header Navigation */}
      <TopNav />

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
          {DESTINATIONS.map((dest) => (
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
      />

      {/* 6. Legal Footer */}
      <Footer />
    </div>
  );
}

export default App;

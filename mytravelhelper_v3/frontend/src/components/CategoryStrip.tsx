import { useState } from "react";

type Category = {
  id: string;
  name: string;
  icon: string;
};

const CATEGORIES: Category[] = [
  { id: "beach", name: "Bãi biển", icon: "🏖️" },
  { id: "cabins", name: "Cabin", icon: "🏡" },
  { id: "mansions", name: "Biệt thự", icon: "🏰" },
  { id: "islands", name: "Đảo", icon: "🏝️" },
  { id: "trending", name: "Thịnh hành", icon: "🔥" },
  { id: "pools", name: "Hồ bơi tuyệt vời", icon: "🏊" },
  { id: "countryside", name: "Vùng nông thôn", icon: "🚜" },
  { id: "sapa", name: "Nhà trên núi", icon: "⛰️" },
  { id: "camping", name: "Cắm trại", icon: "⛺" },
  { id: "luxe", name: "Luxe", icon: "💎" },
];

export function CategoryStrip() {
  const [activeCategory, setActiveCategory] = useState("beach");

  return (
    <div className="w-full border-b border-hairline bg-canvas px-6 md:px-12 py-3 flex items-center gap-6 overflow-x-auto scrollbar-none select-none">
      {CATEGORIES.map((cat) => {
        const isActive = cat.id === activeCategory;
        return (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id)}
            className={[
              "flex flex-col items-center gap-1.5 pb-2 transition-all shrink-0 cursor-pointer border-b-2 hover:text-ink",
              isActive
                ? "text-ink border-ink font-semibold"
                : "text-muted border-transparent hover:border-muted/30",
            ].join(" ")}
          >
            <span className="text-[20px]">{cat.icon}</span>
            <span className="text-[12px] tracking-wide leading-none">{cat.name}</span>
          </button>
        );
      })}
    </div>
  );
}

export default CategoryStrip;

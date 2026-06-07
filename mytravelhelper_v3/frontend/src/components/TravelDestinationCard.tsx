import { useState, type ButtonHTMLAttributes } from "react";

export type TravelDestinationCardProps = {
  name: string;
  imageUrl: string;
  rating: number;
  reviewCount?: number;
  price?: string;
  distance?: string;
  dates?: string;
  imageAlt?: string;
  onExplore?: ButtonHTMLAttributes<HTMLButtonElement>["onClick"];
  disabled?: boolean;
  className?: string;
};

export function TravelDestinationCard({
  name,
  imageUrl,
  rating,
  reviewCount = 120,
  price = "1.500.000 ₫",
  distance = "Cách đây 120 km",
  dates = "Ngày 15 - 20 thg 6",
  imageAlt,
  onExplore,
  disabled = false,
  className = "",
}: TravelDestinationCardProps) {
  const [isSaved, setIsSaved] = useState(false);
  const safeRating = Math.max(0, Math.min(5, rating));
  const formattedRating = safeRating.toFixed(1);
  const isGuestFavorite = rating >= 4.8;

  return (
    <article
      className={[
        "group w-full bg-canvas text-ink",
        "transition-all duration-200 hover:shadow-card cursor-pointer pb-3",
        className,
      ].join(" ")}
      style={{
        fontFamily: "'Inter', sans-serif"
      }}
    >
      {/* Photo Plate */}
      <div className="relative aspect-square overflow-hidden rounded-lg bg-surface-soft border border-hairline">
        <img
          src={imageUrl}
          alt={imageAlt ?? name}
          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.02]"
          loading="lazy"
        />

        {/* Floating Badges */}
        {isGuestFavorite && (
          <div className="absolute left-3 top-3 z-10 rounded-full bg-canvas px-2.5 py-1 text-[11px] font-semibold leading-[1.18] tracking-normal text-ink border border-hairline shadow-sm">
            ★ Khách thích nhất
          </div>
        )}

        {/* Heart Icon Button */}
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            setIsSaved(!isSaved);
          }}
          aria-label={isSaved ? "Bỏ lưu điểm đến" : "Lưu điểm đến"}
          className="absolute right-3 top-3 z-10 flex h-8 w-8 items-center justify-center rounded-full bg-canvas/90 text-ink border border-hairline shadow-sm transition-all hover:scale-105 active:scale-95"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 32 32"
            aria-hidden="true"
            className={[
              "h-[16px] w-[16px] stroke-black stroke-[2px] transition-colors",
              isSaved ? "fill-black" : "fill-none",
            ].join(" ")}
          >
            <path d="M16 28c7-4.73 14-10 14-17a6.88 6.88 0 0 0-7-7c-3.75 0-6.25 2-7 4.42C15.25 6 12.75 4 9 4a6.88 6.88 0 0 0-7 7c0 7 7 12.27 14 17z" />
          </svg>
        </button>
      </div>

      {/* Meta Content */}
      <div className="space-y-1.5 px-1 pt-3">
        <div className="flex items-start justify-between gap-3">
          <h3 className="overflow-hidden text-[15px] font-semibold leading-5 tracking-normal text-ink group-hover:text-black transition-colors line-clamp-1">
            {name}
          </h3>

          <div
            className="flex shrink-0 items-center gap-1 text-[13px] font-normal leading-5 text-ink"
            aria-label={`Đánh giá ${formattedRating} trên 5 sao`}
          >
            <span aria-hidden="true" className="text-ink">
              ★
            </span>
            <span className="font-semibold">{formattedRating}</span>
          </div>
        </div>

        {/* Distance & Dates */}
        <p className="text-[13px] font-normal leading-4 tracking-normal text-muted">
          {distance}
        </p>
        <p className="text-[13px] font-normal leading-4 tracking-normal text-muted">
          {dates}
        </p>

        {/* Price & Reviews count */}
        <div className="flex justify-between items-center pt-0.5">
          <span className="text-[13px] font-bold leading-5 text-ink">
            {price} <span className="font-normal text-muted">/ đêm</span>
          </span>
          <span className="text-[12px] font-normal text-muted underline">
            {reviewCount} đánh giá
          </span>
        </div>

        {/* Action Button */}
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            if (onExplore) onExplore(e);
          }}
          disabled={disabled}
          aria-label={`Khám phá ${name}`}
          className={[
            "mt-3 h-9 w-full rounded-full px-4 text-[13px] font-medium leading-5 tracking-normal",
            "bg-black text-white transition-colors duration-150",
            "hover:bg-neutral-800 active:bg-neutral-900",
            "disabled:cursor-not-allowed disabled:bg-neutral-200 disabled:text-neutral-400",
          ].join(" ")}
        >
          Khám phá ngay
        </button>
      </div>
    </article>
  );
}

export default TravelDestinationCard;

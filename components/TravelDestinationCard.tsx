import type { ButtonHTMLAttributes } from "react";

export type TravelDestinationCardProps = {
  name: string;
  imageUrl: string;
  rating: number;
  reviewCount?: number;
  imageAlt?: string;
  onExplore?: ButtonHTMLAttributes<HTMLButtonElement>["onClick"];
  disabled?: boolean;
  className?: string;
};

const cardShadow =
  "hover:shadow-[rgba(0,0,0,0.02)_0_0_0_1px,rgba(0,0,0,0.04)_0_2px_6px_0,rgba(0,0,0,0.1)_0_4px_8px_0]";

export function TravelDestinationCard({
  name,
  imageUrl,
  rating,
  reviewCount,
  imageAlt,
  onExplore,
  disabled = false,
  className = "",
}: TravelDestinationCardProps) {
  const safeRating = Math.max(0, Math.min(5, rating));
  const formattedRating = safeRating.toFixed(1);

  return (
    <article
      className={[
        "group w-full max-w-sm rounded-[14px] bg-white text-[#222222]",
        "transition-shadow duration-200",
        cardShadow,
        className,
      ].join(" ")}
      style={{
        fontFamily:
          "'Airbnb Cereal VF', Circular, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      }}
    >
      <div className="relative aspect-square overflow-hidden rounded-[14px] bg-[#f7f7f7]">
        <img
          src={imageUrl}
          alt={imageAlt ?? name}
          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.025]"
          loading="lazy"
        />
      </div>

      <div className="space-y-3 px-1 pt-3">
        <div className="flex items-start justify-between gap-3">
          <h3 className="overflow-hidden text-[16px] font-semibold leading-5 tracking-normal [display:-webkit-box] [-webkit-box-orient:vertical] [-webkit-line-clamp:2]">
            {name}
          </h3>

          <div
            className="flex shrink-0 items-center gap-1 text-[14px] font-normal leading-5 text-[#222222]"
            aria-label={`Đánh giá ${formattedRating} trên 5 sao`}
          >
            <span aria-hidden="true" className="text-[13px] leading-none">
              ★
            </span>
            <span>{formattedRating}</span>
          </div>
        </div>

        {typeof reviewCount === "number" ? (
          <p className="text-[14px] font-normal leading-5 tracking-normal text-[#6a6a6a]">
            {reviewCount.toLocaleString("vi-VN")} lượt đánh giá
          </p>
        ) : null}

        <button
          type="button"
          onClick={onExplore}
          disabled={disabled}
          aria-label={`Khám phá ${name}`}
          className={[
            "h-12 w-full rounded-[8px] px-6 text-[16px] font-medium leading-5 tracking-normal",
            "bg-[#ff385c] text-white transition-colors duration-150",
            "hover:bg-[#e00b41] active:bg-[#e00b41]",
            "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#222222]",
            "disabled:cursor-not-allowed disabled:bg-[#ffd1da] disabled:text-white",
          ].join(" ")}
        >
          Khám phá ngay
        </button>
      </div>
    </article>
  );
}

export default TravelDestinationCard;

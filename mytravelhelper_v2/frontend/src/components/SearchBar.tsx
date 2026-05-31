import { useState, useRef, useEffect } from "react";
import { Search } from "lucide-react";

export function SearchBar() {
  const [activeSegment, setActiveSegment] = useState<"where" | "when" | "who" | null>(null);
  const [selectedRange, setSelectedRange] = useState<{ start: number | null; end: number | null }>({
    start: 12,
    end: 17,
  });
  const [whereInput, setWhereInput] = useState("");
  const [guestsCount, setGuestsCount] = useState(2);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close dropdowns on outside clicks
  useEffect(() => {
    function handleOutsideClick(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setActiveSegment(null);
      }
    }
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  const selectDay = (day: number) => {
    if (!selectedRange.start || (selectedRange.start && selectedRange.end)) {
      setSelectedRange({ start: day, end: null });
    } else if (selectedRange.start && !selectedRange.end) {
      if (day < selectedRange.start) {
        setSelectedRange({ start: day, end: selectedRange.start });
      } else {
        setSelectedRange({ ...selectedRange, end: day });
      }
    }
  };

  const isDaySelected = (day: number) => {
    return selectedRange.start === day || selectedRange.end === day;
  };

  const isDayInRange = (day: number) => {
    if (selectedRange.start && selectedRange.end) {
      return day > selectedRange.start && day < selectedRange.end;
    }
    return false;
  };

  return (
    <div ref={containerRef} className="relative w-full max-w-[850px] mx-auto my-6 px-4">
      {/* Outer Pill Container */}
      <div
        className={[
          "h-[66px] w-full rounded-full border border-hairline bg-canvas flex items-center shadow-sm select-none",
          activeSegment ? "bg-surface-soft shadow-md" : "hover:bg-[#f2f2f2]/60 hover:shadow-md",
          "transition-all duration-200 cursor-pointer relative",
        ].join(" ")}
      >
        {/* Segment 1: Where */}
        <div
          onClick={() => setActiveSegment("where")}
          className={[
            "flex-1 h-full rounded-full flex flex-col justify-center px-8 transition-colors duration-150",
            activeSegment === "where" ? "bg-canvas shadow-lg" : "hover:bg-canvas/30",
          ].join(" ")}
        >
          <span className="text-[12px] font-bold text-ink uppercase tracking-wider">Địa điểm</span>
          <input
            type="text"
            placeholder="Bạn muốn đi đâu?"
            value={whereInput}
            onChange={(e) => setWhereInput(e.target.value)}
            className="bg-transparent text-[14px] text-body placeholder-muted focus:outline-none w-full border-none p-0 mt-0.5"
          />
        </div>

        {/* Divider 1 */}
        <div className="h-8 w-[1px] bg-hairline shrink-0"></div>

        {/* Segment 2: When */}
        <div
          onClick={() => setActiveSegment("when")}
          className={[
            "flex-[1.2] h-full rounded-full flex flex-col justify-center px-8 transition-colors duration-150",
            activeSegment === "when" ? "bg-canvas shadow-lg" : "hover:bg-canvas/30",
          ].join(" ")}
        >
          <span className="text-[12px] font-bold text-ink uppercase tracking-wider">Thời gian</span>
          <span className="text-[14px] text-body font-medium mt-0.5">
            {selectedRange.start
              ? `${selectedRange.start} thg 6` + (selectedRange.end ? ` - ${selectedRange.end} thg 6` : "")
              : "Thêm ngày"}
          </span>
        </div>

        {/* Divider 2 */}
        <div className="h-8 w-[1px] bg-hairline shrink-0"></div>

        {/* Segment 3: Who */}
        <div
          onClick={() => setActiveSegment("who")}
          className={[
            "flex-1 h-full rounded-full flex flex-col justify-center pl-8 pr-20 transition-colors duration-150 relative",
            activeSegment === "who" ? "bg-canvas shadow-lg" : "hover:bg-canvas/30",
          ].join(" ")}
        >
          <span className="text-[12px] font-bold text-ink uppercase tracking-wider">Số khách</span>
          <span className="text-[14px] text-muted font-normal mt-0.5">
            {guestsCount > 0 ? `${guestsCount} người lớn` : "Thêm khách"}
          </span>

          {/* Search Orb */}
          <button
            type="button"
            className="absolute right-2 top-1/2 -translate-y-1/2 h-[48px] w-[48px] rounded-full bg-rausch text-canvas flex items-center justify-center transition-colors hover:bg-rausch-active active:scale-95 z-20 shadow-sm"
          >
            <Search className="h-[18px] w-[18px]" />
          </button>
        </div>
      </div>

      {/* DROPDOWN OVERLAYS */}
      {/* 1. Date Picker Dropdown */}
      {activeSegment === "when" && (
        <div className="absolute top-[76px] left-1/2 -translate-x-1/2 w-full max-w-[500px] bg-canvas rounded-xl border border-hairline shadow-card p-6 z-50 text-ink">
          <div className="flex items-center justify-between mb-4">
            <span className="font-semibold text-[16px]">Tháng 6 2026</span>
            <button
              onClick={() => setSelectedRange({ start: null, end: null })}
              className="text-[12px] font-semibold text-muted underline hover:text-ink cursor-pointer"
            >
              Xóa ngày
            </button>
          </div>

          {/* Calendar Grid */}
          <div className="grid grid-cols-7 gap-y-2 justify-items-center text-center">
            {/* Days of week */}
            {["CN", "T2", "T3", "T4", "T5", "T6", "T7"].map((d) => (
              <span key={d} className="text-[12px] font-bold text-muted w-10 py-1">
                {d}
              </span>
            ))}

            {/* Empty grid cells for day offset */}
            {Array.from({ length: 1 }).map((_, i) => (
              <div key={`empty-${i}`} className="w-10 h-10"></div>
            ))}

            {/* Days of month 1 to 30 */}
            {Array.from({ length: 30 }).map((_, i) => {
              const day = i + 1;
              const isSelected = isDaySelected(day);
              const inRange = isDayInRange(day);

              return (
                <div
                  key={`day-${day}`}
                  className={[
                    "w-10 h-10 flex items-center justify-center relative cursor-pointer text-[14px]",
                    inRange ? "bg-surface-soft w-full" : "",
                  ].join(" ")}
                  onClick={() => selectDay(day)}
                >
                  <button
                    className={[
                      "w-10 h-10 rounded-full flex items-center justify-center transition-colors font-medium z-10",
                      isSelected
                        ? "bg-ink text-canvas font-semibold"
                        : "text-ink hover:border hover:border-ink hover:bg-canvas",
                    ].join(" ")}
                  >
                    {day}
                  </button>

                  {/* Connective ranges background lozenge */}
                  {inRange && (
                    <div className="absolute inset-0 bg-surface-soft z-0"></div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 2. Where Search Overlay */}
      {activeSegment === "where" && (
        <div className="absolute top-[76px] left-[5%] w-[320px] bg-canvas rounded-xl border border-hairline shadow-card p-4 z-50 text-ink">
          <span className="text-[12px] font-bold text-muted uppercase tracking-wider block mb-3">Tìm kiếm gần đây</span>
          <div className="space-y-2">
            {["Phú Quốc", "Đà Nẵng", "Sapa", "Vũng Tàu"].map((loc) => (
              <div
                key={loc}
                onClick={() => {
                  setWhereInput(loc);
                  setActiveSegment("when");
                }}
                className="flex items-center gap-3 p-2 rounded-sm hover:bg-surface-soft transition-colors cursor-pointer"
              >
                <div className="h-8 w-8 bg-surface-strong rounded-sm flex items-center justify-center">
                  📍
                </div>
                <div>
                  <div className="text-[14px] font-semibold">{loc}</div>
                  <div className="text-[12px] text-muted">Việt Nam</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3. Who Selector Dropdown */}
      {activeSegment === "who" && (
        <div className="absolute top-[76px] right-[5%] w-[320px] bg-canvas rounded-xl border border-hairline shadow-card p-5 z-50 text-ink">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-[15px] font-semibold">Người lớn</div>
              <div className="text-[13px] text-muted">Từ 13 tuổi trở lên</div>
            </div>
            <div className="flex items-center gap-3.5">
              <button
                onClick={() => setGuestsCount(Math.max(0, guestsCount - 1))}
                className="w-8 h-8 rounded-full border border-border-strong flex items-center justify-center text-[20px] font-light hover:border-ink disabled:opacity-30"
                disabled={guestsCount === 0}
              >
                -
              </button>
              <span className="text-[16px] font-medium w-4 text-center">{guestsCount}</span>
              <button
                onClick={() => setGuestsCount(guestsCount + 1)}
                className="w-8 h-8 rounded-full border border-border-strong flex items-center justify-center text-[18px] font-light hover:border-ink"
              >
                +
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SearchBar;

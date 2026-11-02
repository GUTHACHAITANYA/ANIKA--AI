import React, { useState } from 'react';
import { ProductOffer } from '../../types/smartbuy';

interface ProductOfferCardProps {
  offer: ProductOffer;
  rank: number;
}

function formatINR(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

function timeAgo(isoStr: string): string {
  try {
    const diff = Date.now() - new Date(isoStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
  } catch {
    return 'recently';
  }
}

function StarRating({ rating }: { rating: number }) {
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.5;
  return (
    <span className="flex items-center gap-0.5">
      {Array.from({ length: 5 }, (_, i) => (
        <span
          key={i}
          className={
            i < full
              ? 'text-yellow-400'
              : i === full && half
              ? 'text-yellow-400 opacity-60'
              : 'text-slate-600'
          }
          style={{ fontSize: '11px' }}
        >
          ★
        </span>
      ))}
    </span>
  );
}

export const ProductOfferCard: React.FC<ProductOfferCardProps> = ({ offer, rank }) => {
  const [expanded, setExpanded] = useState(false);

  const discountColor =
    offer.discount_percentage >= 30
      ? 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30'
      : offer.discount_percentage >= 15
      ? 'text-orange-400 bg-orange-400/10 border-orange-400/30'
      : 'text-slate-400 bg-slate-400/10 border-slate-400/30';

  const cardBorder = offer.is_best_discount
    ? 'border-emerald-500/60 shadow-emerald-500/10 shadow-lg'
    : 'border-slate-700/50';

  return (
    <div
      className={`relative rounded-xl border ${cardBorder} bg-slate-800/60 backdrop-blur-sm p-4 transition-all duration-200 hover:border-indigo-500/40`}
    >
      {/* BEST DISCOUNT badge */}
      {offer.is_best_discount && (
        <div className="absolute -top-3 left-4 flex items-center gap-1.5 bg-emerald-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-md">
          <span>⚡</span> BEST DISCOUNT
        </div>
      )}

      {/* Demo warning */}
      {offer.is_demo && (
        <div className="mb-3 flex items-center gap-2 rounded-lg bg-amber-500/10 border border-amber-500/30 px-3 py-2">
          <span className="text-amber-400 text-xs">⚠️</span>
          <span className="text-amber-300 text-xs">
            Demo data — connect provider APIs for live verified prices
          </span>
        </div>
      )}

      <div className="flex gap-4">
        {/* Product Image */}
        <div className="flex-shrink-0 w-20 h-20 rounded-lg bg-slate-700/50 flex items-center justify-center overflow-hidden">
          {offer.image_url ? (
            <img
              src={offer.image_url}
              alt={offer.product_title}
              className="w-full h-full object-contain p-1"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
          ) : (
            <span className="text-3xl">{offer.platform_logo}</span>
          )}
        </div>

        {/* Main content */}
        <div className="flex-1 min-w-0">
          {/* Platform + rank */}
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <span className="text-lg">{offer.platform_logo}</span>
              <span className="text-sm font-semibold text-white">{offer.platform_name}</span>
              <span className="text-xs text-slate-500">#{rank}</span>
            </div>
            {/* Discount badge */}
            <span
              className={`text-sm font-bold px-2 py-0.5 rounded-full border ${discountColor}`}
            >
              {offer.discount_percentage > 0 ? `${offer.discount_percentage.toFixed(0)}% OFF` : 'No discount'}
            </span>
          </div>

          {/* Product title */}
          <p className="text-sm text-slate-200 font-medium leading-snug line-clamp-2 mb-2">
            {offer.product_title}
          </p>

          {/* Variant warning */}
          {offer.variant_warning && offer.variant_warning.length > 0 && (
            <div className="mb-2 text-xs text-amber-400 bg-amber-400/10 rounded px-2 py-1">
              ⚠️ Variant may differ: {offer.variant_warning.join(', ')}
            </div>
          )}

          {/* Pricing */}
          <div className="flex flex-wrap items-baseline gap-3 mb-2">
            <span className="text-xl font-extrabold text-white">
              {formatINR(offer.selling_price)}
            </span>
            {offer.original_price > offer.selling_price && (
              <span className="text-sm text-slate-500 line-through">
                {formatINR(offer.original_price)}
              </span>
            )}
          </div>

          {/* Savings breakdown */}
          <div className="flex flex-wrap gap-2 text-xs mb-2">
            {offer.coupon_discount > 0 && (
              <span className="text-emerald-400 bg-emerald-400/10 rounded px-2 py-0.5 border border-emerald-400/20">
                🎟 Coupon: -{formatINR(offer.coupon_discount)}
              </span>
            )}
            {offer.bank_discount > 0 && (
              <span className="text-blue-400 bg-blue-400/10 rounded px-2 py-0.5 border border-blue-400/20">
                🏦 Bank offer*: -{formatINR(offer.bank_discount)}
              </span>
            )}
            {offer.cashback > 0 && (
              <span className="text-purple-400 bg-purple-400/10 rounded px-2 py-0.5 border border-purple-400/20">
                💰 Cashback*: {formatINR(offer.cashback)}
              </span>
            )}
            {offer.delivery_fee > 0 ? (
              <span className="text-orange-400 bg-orange-400/10 rounded px-2 py-0.5 border border-orange-400/20">
                🚚 Delivery: +{formatINR(offer.delivery_fee)}
              </span>
            ) : (
              <span className="text-emerald-400 bg-emerald-400/10 rounded px-2 py-0.5 border border-emerald-400/20">
                🚚 Free Delivery
              </span>
            )}
          </div>

          {/* Final payable + rating */}
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-400">Final payable: </span>
              <span className="text-sm font-bold text-indigo-300">
                {formatINR(offer.final_payable_price)}
              </span>
              {(offer.bank_discount > 0 || offer.cashback > 0) && (
                <span className="text-xs text-slate-500 ml-1">
                  (excl. conditional offers*)
                </span>
              )}
            </div>
            <div className="flex items-center gap-1.5">
              <StarRating rating={offer.rating} />
              {offer.reviews_count > 0 && (
                <span className="text-xs text-slate-500">
                  ({offer.reviews_count.toLocaleString('en-IN')})
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-3 pt-3 border-t border-slate-700/50 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 text-xs text-slate-500">
          <span
            className={
              offer.availability === 'in_stock'
                ? 'text-emerald-400'
                : offer.availability === 'limited_stock'
                ? 'text-orange-400'
                : 'text-red-400'
            }
          >
            ●{' '}
            {offer.availability === 'in_stock'
              ? 'In Stock'
              : offer.availability === 'limited_stock'
              ? 'Limited Stock'
              : 'Out of Stock'}
          </span>
          <span>Updated {timeAgo(offer.last_checked)}</span>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            {expanded ? '▲ Less' : '▼ Offer details'}
          </button>
        </div>

        <a
          href={offer.product_url}
          target="_blank"
          rel="noopener noreferrer"
          className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-bold transition-all ${
            offer.availability !== 'out_of_stock'
              ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-500/20'
              : 'bg-slate-700 text-slate-400 cursor-not-allowed pointer-events-none'
          }`}
        >
          BUY NOW →
        </a>
      </div>

      {/* Expanded offer details */}
      {expanded && offer.offer_details && (
        <div className="mt-3 p-3 rounded-lg bg-slate-900/60 border border-slate-700/40 text-xs text-slate-300 leading-relaxed">
          {offer.offer_details}
          {(offer.bank_discount > 0 || offer.cashback > 0) && (
            <p className="mt-2 text-slate-500">
              * Bank offers and cashback are conditional and may require specific cards or
              wallet providers. They are not counted in the final payable price shown above.
            </p>
          )}
        </div>
      )}
    </div>
  );
};


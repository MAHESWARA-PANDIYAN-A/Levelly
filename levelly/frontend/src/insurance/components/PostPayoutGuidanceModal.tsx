import { useState } from 'react'
import { Shield, X, CheckCircle2 } from 'lucide-react'

interface PostPayoutGuidanceModalProps {
  isOpen: boolean
  onClose: () => void
  payoutAmount: number
  safetyBalance: number
  safetyTarget: number
  onConfirmTransfer: (amount: number) => Promise<void>
  isTransferring?: boolean
}

const formatINR = (amt: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amt)

export default function PostPayoutGuidanceModal({
  isOpen,
  onClose,
  payoutAmount,
  safetyBalance,
  safetyTarget,
  onConfirmTransfer,
  isTransferring = false,
}: PostPayoutGuidanceModalProps) {
  const [selectedAmount, setSelectedAmount] = useState<number>(Math.min(payoutAmount, 500))

  if (!isOpen) return null

  const shortfall = Math.max(0, safetyTarget - safetyBalance)
  const isBelowTarget = shortfall > 0

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fade-in">
      <div className="bg-white rounded-3xl max-w-sm w-full p-5 shadow-2xl border border-slate-100 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4 shadow-sm shadow-emerald-500/10">
          <Shield className="w-6 h-6" />
        </div>

        <h3 className="text-lg font-bold text-slate-900 mb-1">Post-Payout Guidance</h3>
        <p className="text-xs text-slate-500 mb-4 leading-relaxed">
          Payout of <span className="font-bold text-slate-800">{formatINR(payoutAmount)}</span> settled to your linked account.
        </p>

        {/* Safety Wallet Current Status */}
        <div className="p-3 bg-slate-50 rounded-2xl border border-slate-200/70 mb-4 space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-slate-500">Current Safety Balance</span>
            <span className="font-extrabold text-slate-800">{formatINR(safetyBalance)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Target Buffer</span>
            <span className="font-semibold text-slate-700">{formatINR(safetyTarget)}</span>
          </div>
          {isBelowTarget ? (
            <div className="pt-2 border-t border-slate-200 flex justify-between text-amber-800 font-medium">
              <span>Safety Buffer Shortfall:</span>
              <span className="font-bold">{formatINR(shortfall)}</span>
            </div>
          ) : (
            <div className="pt-2 border-t border-slate-200 flex items-center gap-1 text-emerald-700 font-bold">
              <CheckCircle2 className="w-3.5 h-3.5" /> Safety Target Achieved!
            </div>
          )}
        </div>

        {isBelowTarget && (
          <div className="mb-4">
            <p className="text-xs font-semibold text-slate-800 mb-1.5">
              Your Safety Wallet is still below your target.
            </p>
            <p className="text-[11px] text-slate-500 mb-3 leading-relaxed">
              Would you like to move part of your payout into your Safety Wallet to boost your resilience reserve?
            </p>

            {/* Quick amount pills */}
            <div className="flex items-center gap-2 mb-3">
              {[Math.min(250, payoutAmount), Math.min(500, payoutAmount), payoutAmount].map((amt) => (
                <button
                  key={amt}
                  type="button"
                  onClick={() => setSelectedAmount(amt)}
                  className={`flex-1 py-1.5 px-2 rounded-xl text-xs font-bold border transition ${
                    selectedAmount === amt
                      ? 'bg-emerald-600 text-white border-emerald-600 shadow-xs'
                      : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  {formatINR(amt)}
                </button>
              ))}
            </div>

            {/* Custom amount slider / input */}
            <div className="flex items-center justify-between text-xs bg-slate-100/80 px-3 py-2 rounded-xl">
              <span className="text-slate-500 font-medium">Amount to allocate:</span>
              <span className="font-black text-slate-900 text-sm">{formatINR(selectedAmount)}</span>
            </div>
          </div>
        )}

        <div className="space-y-2 mt-5">
          {isBelowTarget && (
            <button
              onClick={() => onConfirmTransfer(selectedAmount)}
              disabled={isTransferring}
              className="btn-primary w-full py-3 text-xs font-bold shadow-md"
            >
              {isTransferring ? 'Transferring...' : `Add ${formatINR(selectedAmount)} to Safety Wallet`}
            </button>
          )}

          <button
            onClick={onClose}
            className="w-full py-2.5 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition"
          >
            Keep Payout Available in Bank
          </button>
        </div>

        <p className="text-[10px] text-slate-400 text-center mt-3">
          Transfers are optional and never automated without explicit consent.
        </p>
      </div>
    </div>
  )
}

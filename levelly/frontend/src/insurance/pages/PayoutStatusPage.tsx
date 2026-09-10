import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft,
  CheckCircle2,
  Clock,
  Shield,
  Sparkles,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { insuranceApi } from '../api/insuranceApi'
import PostPayoutGuidanceModal from '../components/PostPayoutGuidanceModal'

const formatINR = (amt: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amt)

export default function PayoutStatusPage() {
  const { payoutId } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [isGuidanceModalOpen, setIsGuidanceModalOpen] = useState(false)

  const { data: payout, isLoading: payoutLoading } = useQuery({
    queryKey: ['insurance-payout', payoutId],
    queryFn: () => insuranceApi.getPayoutDetails(Number(payoutId)).then((r) => r.data),
  })

  const { data: status } = useQuery({
    queryKey: ['insurance-status'],
    queryFn: () => insuranceApi.getStatus().then((r) => r.data),
  })

  const completePayoutMutation = useMutation({
    mutationFn: () => insuranceApi.completePayoutDemo(Number(payoutId)),
    onSuccess: () => {
      toast.success('Insurance partner completed claim settlement!')
      queryClient.invalidateQueries({ queryKey: ['insurance-payout', payoutId] })
      queryClient.invalidateQueries({ queryKey: ['insurance-status'] })
    },
  })

  const moveToSafetyMutation = useMutation({
    mutationFn: (amount: number) => insuranceApi.moveToSafetyWallet(Number(payoutId), amount),
    onSuccess: (res: any) => {
      toast.success(res.data.message)
      setIsGuidanceModalOpen(false)
      queryClient.invalidateQueries({ queryKey: ['insurance-status'] })
      queryClient.invalidateQueries({ queryKey: ['wallets'] })
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Transfer failed')
    },
  })

  if (payoutLoading || !payout) {
    return (
      <div className="px-5 pt-8 animate-pulse space-y-4">
        <div className="h-6 bg-slate-200 rounded w-1/3" />
        <div className="h-44 bg-slate-200 rounded-2xl" />
      </div>
    )
  }

  const isCompleted = payout.status === 'COMPLETED'
  const safetyBalance = status?.safety_wallet_balance || 8200
  const safetyTarget = status?.safety_wallet_target || 10000

  return (
    <div className="px-5 pb-8 animate-fade-in space-y-4 pt-2">
      <button
        onClick={() => navigate('/incomeshield/policy')}
        className="flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-800 transition py-1"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Policy
      </button>

      {/* Main Status Hero Card */}
      {isCompleted ? (
        /* SCREEN 16: PAYOUT COMPLETED */
        <div className="card p-5 bg-gradient-to-br from-emerald-900 via-slate-900 to-slate-950 text-white rounded-3xl shadow-xl text-center space-y-2">
          <div className="w-14 h-14 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto border border-emerald-500/30 mb-1">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-400 block">
            Claim Settled
          </span>
          <h1 className="text-3xl font-black text-white">{payout.amount_display}</h1>
          <p className="text-xs text-slate-300">
            Transferred to your <strong className="text-emerald-300">{payout.destination_reference}</strong>
          </p>
          <div className="inline-block mt-1 px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-black tracking-wider">
            STATUS: COMPLETED
          </div>
        </div>
      ) : (
        /* SCREEN 15: PAYOUT PROCESSING */
        <div className="card p-5 bg-gradient-to-br from-blue-900 via-slate-900 to-slate-950 text-white rounded-3xl shadow-xl text-center space-y-2">
          <div className="w-14 h-14 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center mx-auto border border-blue-500/30 mb-1 animate-pulse">
            <Clock className="w-8 h-8" />
          </div>
          <span className="text-[10px] font-bold uppercase tracking-widest text-blue-400 block">
            Parametric Payout Processing
          </span>
          <h1 className="text-2xl font-black text-white">{payout.amount_display}</h1>
          <p className="text-xs text-slate-300">
            Underwriting partner is validating telemetry logs for instant UPI deposit.
          </p>
          <div className="inline-block mt-1 px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30 text-[10px] font-black tracking-wider">
            STATUS: PROCESSING
          </div>
        </div>
      )}

      {/* Payout Details Card */}
      <div className="card p-4 bg-white border border-slate-200 shadow-xs space-y-2.5 text-xs">
        <h3 className="font-bold text-slate-900 pb-2 border-b border-slate-100">Settlement Particulars</h3>
        <div className="flex justify-between">
          <span className="text-slate-500">Reason:</span>
          <span className="font-bold text-slate-800">{payout.reason}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-500">Partner Reference:</span>
          <span className="font-mono font-bold text-slate-700">{payout.payout_id_from_partner || 'Assigning...'}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-500">Date:</span>
          <span className="font-semibold text-slate-800">
            {new Date(payout.created_at).toLocaleDateString('en-IN', {
              day: 'numeric',
              month: 'short',
              year: 'numeric',
            })}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-500">Settlement Channel:</span>
          <span className="font-semibold text-slate-800">Direct UPI Settlement</span>
        </div>
      </div>

      {/* SCREEN 17: POST-PAYOUT FINANCIAL GUIDANCE */}
      {isCompleted && (
        <div className="card p-5 bg-gradient-to-b from-emerald-50/70 to-white border-2 border-emerald-300 rounded-3xl shadow-sm space-y-3">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-emerald-700" />
            <h3 className="text-sm font-bold text-slate-900">Post-Payout Financial Guidance</h3>
          </div>

          <p className="text-xs text-slate-600 leading-relaxed">
            Your Safety Wallet balance is currently <strong className="text-slate-900">{formatINR(safetyBalance)}</strong> against your target of <strong className="text-slate-900">{formatINR(safetyTarget)}</strong>.
          </p>

          {safetyTarget > safetyBalance && (
            <div className="p-3 bg-white rounded-2xl border border-emerald-200/80 space-y-2 text-xs">
              <div className="flex justify-between font-medium text-slate-700">
                <span>Safety Wallet Target Shortfall:</span>
                <span className="font-bold text-amber-700">{formatINR(safetyTarget - safetyBalance)}</span>
              </div>
              <p className="text-[11px] text-slate-500 leading-snug">
                Would you like to move part of your payout into your Safety Wallet to strengthen your buffer against future low-earning days?
              </p>
            </div>
          )}

          <div className="space-y-2 pt-1">
            <button
              onClick={() => setIsGuidanceModalOpen(true)}
              className="btn-primary w-full py-3 text-xs font-bold shadow-md flex items-center justify-center gap-1.5"
            >
              <Shield className="w-4 h-4" /> Add to Safety Wallet
            </button>
            <button
              onClick={() => navigate('/safety')}
              className="w-full py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition text-center"
            >
              Keep Payout Available & View Wallet
            </button>
          </div>
        </div>
      )}

      {/* Demo Simulation Action: Complete Payout if still processing */}
      {!isCompleted && (
        <div className="p-3 bg-slate-100 rounded-2xl border border-slate-200 text-center space-y-2">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
            Partner Settlement Simulator
          </span>
          <button
            onClick={() => completePayoutMutation.mutate()}
            disabled={completePayoutMutation.isPending}
            className="w-full py-2.5 px-3 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition shadow-sm flex items-center justify-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            {completePayoutMutation.isPending ? 'Settling...' : '⚡ Settle Payout Now (Partner Callback)'}
          </button>
        </div>
      )}

      {/* Post Payout Modal */}
      {payout.amount && (
        <PostPayoutGuidanceModal
          isOpen={isGuidanceModalOpen}
          onClose={() => setIsGuidanceModalOpen(false)}
          payoutAmount={payout.amount}
          safetyBalance={safetyBalance}
          safetyTarget={safetyTarget}
          onConfirmTransfer={async (amount) => {
            await moveToSafetyMutation.mutateAsync(amount)
          }}
          isTransferring={moveToSafetyMutation.isPending}
        />
      )}
    </div>
  )
}

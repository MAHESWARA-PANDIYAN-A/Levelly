import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, DollarSign } from 'lucide-react'
import { incomeAPI } from '../lib/api'
import toast from 'react-hot-toast'

const SOURCES = [
  { key: 'Swiggy', label: 'Swiggy', emoji: '🛵' },
  { key: 'Zomato', label: 'Zomato', emoji: '🍕' },
  { key: 'Uber', label: 'Uber', emoji: '🚗' },
  { key: 'Ola', label: 'Ola', emoji: '🚖' },
  { key: 'Blinkit', label: 'Blinkit', emoji: '⚡' },
  { key: 'Other', label: 'Other', emoji: '💼' },
]

export default function IncomePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [amount, setAmount] = useState('')
  const [source, setSource] = useState('Swiggy')
  const [success, setSuccess] = useState<any>(null)

  const addIncomeMutation = useMutation({
    mutationFn: () => incomeAPI.add({ amount: parseFloat(amount), source }),
    onSuccess: (res) => {
      setSuccess(res.data)
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['wallets'] })
      toast.success('Income added!')
    },
    onError: () => toast.error('Failed to add income'),
  })

  if (success) {
    return (
      <div className="px-5 pt-12 pb-8 text-center animate-fade-in">
        <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-5 animate-bounce-soft">
          <DollarSign className="w-10 h-10 text-emerald-600" />
        </div>
        <h2 className="text-2xl font-bold mb-2">Income Added!</h2>
        <p className="text-4xl font-bold text-emerald-600 mb-4">
          ₹{parseFloat(amount).toLocaleString('en-IN')}
        </p>
        <p className="text-gray-500 mb-6">Added to your Daily Wallet from {source}</p>
        <div className="card mb-4">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Daily Wallet Balance</span>
            <span className="font-bold">₹{success.daily_wallet_balance?.toLocaleString('en-IN')}</span>
          </div>
        </div>
        <button onClick={() => { setSuccess(null); setAmount('') }} className="btn-primary mb-2">
          Add More Income
        </button>
        <button onClick={() => navigate('/')} className="btn-ghost">Back to Home</button>
      </div>
    )
  }

  return (
    <div className="px-5 pt-12 pb-8 animate-fade-in">
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-gray-600 mb-5">
        <ArrowLeft className="w-4 h-4" /> Back
      </button>
      <h1 className="text-2xl font-bold mb-1">Add Income</h1>
      <p className="text-sm text-gray-500 mb-6">Record a payout or income received</p>

      <div className="card mb-4">
        <label className="text-sm font-medium text-gray-600 block mb-2">Amount Received (₹)</label>
        <div className="flex items-center gap-2">
          <span className="text-3xl font-bold text-gray-400">₹</span>
          <input
            id="income-amount"
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0"
            className="flex-1 text-4xl font-bold text-gray-900 focus:outline-none bg-transparent"
          />
        </div>
        <div className="flex gap-2 mt-3">
          {[1000, 2000, 5000, 10000].map((v) => (
            <button key={v} onClick={() => setAmount(String(v))}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                ${amount === String(v) ? 'bg-emerald-600 text-white' : 'bg-gray-100 text-gray-600'}`}>
              ₹{v >= 1000 ? `${v / 1000}k` : v}
            </button>
          ))}
        </div>
      </div>

      <div className="card mb-6">
        <p className="text-sm font-medium text-gray-600 mb-3">Source</p>
        <div className="grid grid-cols-3 gap-2">
          {SOURCES.map(({ key, label, emoji }) => (
            <button key={key} onClick={() => setSource(key)}
              className={`flex flex-col items-center gap-1 p-3 rounded-xl text-sm font-medium transition-all
                ${source === key ? 'bg-emerald-600 text-white' : 'bg-gray-50 text-gray-700 hover:bg-gray-100'}`}>
              <span className="text-xl">{emoji}</span>
              {label}
            </button>
          ))}
        </div>
      </div>

      <button
        id="btn-add-income"
        onClick={() => {
          if (!amount || parseFloat(amount) <= 0) { toast.error('Enter a valid amount'); return }
          addIncomeMutation.mutate()
        }}
        disabled={addIncomeMutation.isPending}
        className="btn-primary"
      >
        {addIncomeMutation.isPending ? 'Adding...' : `Add ₹${amount || '0'} to Daily Wallet`}
      </button>
    </div>
  )
}

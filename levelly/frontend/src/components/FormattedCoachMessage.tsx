import React from 'react'

interface FormattedCoachMessageProps {
  text: string
  isUser: boolean
}

export default function FormattedCoachMessage({ text, isUser }: FormattedCoachMessageProps) {
  if (isUser) {
    return <p className="text-sm leading-relaxed whitespace-pre-wrap">{text}</p>
  }

  // Pre-process text to separate smashed together headers, bullets, and numbered items
  let formatted = text || ''

  // 1. Break apart inline headings after sentence punctuation:
  // e.g. "pressure on expenses. **When will they reopen?**" or "signals). **What you can do now**"
  formatted = formatted.replace(/([.!?]|\))\s+(\*\*[A-Z0-9][^*]+\*\*)/g, '$1\n\n$2\n\n')

  // 2. Break apart headings immediately followed by a list item:
  // e.g. "**What you can do now** 1. **Boost"
  formatted = formatted.replace(/(\*\*[A-Z0-9][^*]+\*\*)\s+(?=\d+\.|\-|\*)/g, '$1\n\n')

  // 3. Break apart inline bullet points:
  // e.g. "trend). - **Or when"
  formatted = formatted.replace(/([.!?]|\))\s+([•\-*])\s+/g, '$1\n\n- ')

  // 4. Break apart inline numbered list items:
  // e.g. "possible. 2. **Stabilize" or "trend. 3. **Trim"
  formatted = formatted.replace(/([.!?]|\))\s+(\d+)\.\s+/g, '$1\n\n$2. ')

  // Split into paragraphs / blocks
  const blocks = formatted
    .split(/\n\n+/)
    .map((b) => b.trim())
    .filter(Boolean)

  return (
    <div className="space-y-3 text-sm leading-relaxed text-slate-800">
      {blocks.map((block, bIdx) => {
        // Check if block is a heading: e.g. "**Title?**" or "**Title**" or "### Title"
        const isHeader =
          (block.startsWith('**') && block.endsWith('**') && !block.slice(2, -2).includes('**')) ||
          block.startsWith('###') ||
          block.startsWith('##')

        if (isHeader) {
          const title = block.replace(/^#{2,3}\s*/, '').replace(/^\*\*|\*\*$/g, '')
          return (
            <div
              key={bIdx}
              className="font-bold text-slate-900 text-sm pt-2 pb-0.5 border-b border-slate-100 flex items-center gap-1.5"
            >
              <span className="w-1 h-3.5 bg-emerald-600 rounded-full" />
              <span>{title}</span>
            </div>
          )
        }

        // Check if block contains lines of bullets or numbered items
        const lines = block.split('\n').map((l) => l.trim()).filter(Boolean)
        const isAllBullets = lines.length > 0 && lines.every((l) => /^[-*•]\s+/.test(l))
        const isAllNumbered = lines.length > 0 && lines.every((l) => /^\d+\.\s+/.test(l))

        if (isAllBullets) {
          return (
            <ul key={bIdx} className="space-y-2 pl-0.5 my-1.5">
              {lines.map((line, lIdx) => {
                const cleanLine = line.replace(/^[-*•]\s+/, '')
                return (
                  <li key={lIdx} className="flex items-start gap-2 text-slate-800">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 mt-2 flex-shrink-0" />
                    <span className="flex-1">{renderInline(cleanLine)}</span>
                  </li>
                )
              })}
            </ul>
          )
        }

        if (isAllNumbered) {
          return (
            <ol key={bIdx} className="space-y-2.5 pl-0.5 my-2">
              {lines.map((line, lIdx) => {
                const match = line.match(/^(\d+)\.\s+(.*)$/)
                const num = match ? match[1] : `${lIdx + 1}`
                const cleanLine = match ? match[2] : line
                return (
                  <li key={lIdx} className="flex items-start gap-2.5 text-slate-800">
                    <span className="w-5 h-5 rounded-full bg-emerald-50 text-emerald-700 font-bold text-[11px] flex items-center justify-center flex-shrink-0 mt-0.5 border border-emerald-200/80 shadow-xs">
                      {num}
                    </span>
                    <span className="flex-1">{renderInline(cleanLine)}</span>
                  </li>
                )
              })}
            </ol>
          )
        }

        // Single bullet point starting line
        if (/^[-*•]\s+/.test(block)) {
          const cleanLine = block.replace(/^[-*•]\s+/, '')
          return (
            <div key={bIdx} className="flex items-start gap-2 pl-0.5 my-1 text-slate-800">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 mt-2 flex-shrink-0" />
              <span className="flex-1">{renderInline(cleanLine)}</span>
            </div>
          )
        }

        // Single numbered item starting line
        if (/^\d+\.\s+/.test(block)) {
          const match = block.match(/^(\d+)\.\s+(.*)$/)
          const num = match ? match[1] : '1'
          const cleanLine = match ? match[2] : block
          return (
            <div key={bIdx} className="flex items-start gap-2.5 pl-0.5 my-1.5 text-slate-800">
              <span className="w-5 h-5 rounded-full bg-emerald-50 text-emerald-700 font-bold text-[11px] flex items-center justify-center flex-shrink-0 mt-0.5 border border-emerald-200/80 shadow-xs">
                {num}
              </span>
              <span className="flex-1">{renderInline(cleanLine)}</span>
            </div>
          )
        }

        // Regular paragraph with inline formatting
        return (
          <p key={bIdx} className="leading-relaxed text-slate-800">
            {renderInline(block)}
          </p>
        )
      })}
    </div>
  )
}

function renderInline(text: string): React.ReactNode {
  // Split by bold (**bold**) and italic (*italic*)
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={i} className="font-bold text-slate-950">
          {part.slice(2, -2)}
        </strong>
      )
    }
    if (part.startsWith('*') && part.endsWith('*')) {
      return (
        <em key={i} className="italic text-slate-700">
          {part.slice(1, -1)}
        </em>
      )
    }
    return part
  })
}

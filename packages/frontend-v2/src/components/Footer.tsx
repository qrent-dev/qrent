'use client'

import { useEffect, useState } from 'react'

export default function Footer() {
  const [currentYear, setCurrentYear] = useState(2024)

  useEffect(() => {
    setCurrentYear(new Date().getFullYear())
  }, [])

  return (
    <footer className="border-t border-slate-200 py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-sm text-slate-500">
        © {currentYear} BlueEstate Rentals. All rights reserved.
      </div>
    </footer>
  )
}
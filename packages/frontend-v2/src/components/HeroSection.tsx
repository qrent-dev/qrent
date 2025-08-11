'use client'

import { HiSearch, HiAdjustments } from 'react-icons/hi'

export default function HeroSection() {
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implement search functionality
  }

  return (
    <section className="relative">
      <img
        src="https://images.unsplash.com/photo-1505691723518-36a5ac3b2c83?q=80&w=2000&auto=format&fit=crop"
        alt="Modern house landscape"
        className="h-[340px] sm:h-[420px] md:h-[520px] w-full object-cover"
      />

      {/* Search bar overlay */}
      <div className="absolute inset-0 flex items-center justify-center px-4">
        <form onSubmit={handleSearch} className="w-full max-w-3xl">
          <div className="rounded-2xl bg-white shadow-card ring-1 ring-slate-200 p-2 md:p-3">
            {/* Responsive: stack on small screens, inline on md+ */}
            <div className="flex flex-col gap-2 md:grid md:grid-cols-[1fr_auto_auto] md:items-center">
              <label htmlFor="search" className="sr-only">Search rentals</label>
              <div className="relative">
                <span className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
                  <HiSearch className="h-5 w-5" />
                </span>
                <input 
                  id="search" 
                  name="q" 
                  placeholder="Enter location, property type..." 
                  className="w-full rounded-xl border border-slate-200 pl-10 pr-4 py-3 text-slate-700 placeholder-slate-400 focus:border-brand focus:ring-brand focus:outline-none" 
                />
              </div>
              <button 
                type="button" 
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 font-medium text-slate-700 hover:border-brand/40 hover:text-brand transition"
              >
                <HiAdjustments className="h-5 w-5" />
                Filter
              </button>
              <button 
                type="submit" 
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-brand px-5 py-3 font-semibold text-white hover:bg-brand/90 transition"
              >
                <HiSearch className="h-5 w-5" />
                Search
              </button>
            </div>
          </div>
        </form>
      </div>
    </section>
  )
}
'use client'

import Image from 'next/image'
import { HiSearch, HiAdjustments } from 'react-icons/hi'

export default function HeroSection() {
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implement search functionality
  }

  return (
    <section className="relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="relative h-[340px] sm:h-[420px] md:h-[520px] w-full overflow-hidden rounded-2xl">
          <Image
            src="/banner.jpg"
            alt="Homepage banner"
            fill
            priority
            className="object-cover"
            sizes="(max-width: 1280px) 100vw, 1280px"
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
                    className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 font-medium text-slate-700 hover:border-blue-300 hover:text-blue-600 transition"
                  >
                    <HiAdjustments className="h-5 w-5" />
                    Filter
                  </button>
                  <button 
                    type="submit" 
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700 transition"
                  >
                    <HiSearch className="h-5 w-5" />
                    Search
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </section>
  )
}

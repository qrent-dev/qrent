'use client'

import { useState } from 'react'
import { HiHome, HiMenu, HiX } from 'react-icons/hi'

export default function Header() {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)

  const openDrawer = () => {
    setIsDrawerOpen(true)
    document.body.classList.add('overflow-hidden')
  }

  const closeDrawer = () => {
    setIsDrawerOpen(false)
    document.body.classList.remove('overflow-hidden')
  }

  return (
    <>
      <header className="sticky top-0 z-50 bg-white/90 backdrop-blur border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="h-16 flex items-center justify-between">
            {/* Left: logo + brand */}
            <a href="#" className="flex items-center gap-3">
              <span aria-hidden="true" className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-brand/10 text-brand">
                <HiHome className="h-5 w-5" />
              </span>
              <span className="text-lg font-semibold tracking-tight">BlueEstate Rentals</span>
            </a>

            {/* Center: desktop nav */}
            <nav className="hidden md:flex items-center gap-8" aria-label="Primary">
              <a href="#guide" className="text-slate-700 hover:text-brand transition-colors">Rental Guide</a>
              <a href="#docs" className="text-slate-700 hover:text-brand transition-colors">Document Preparation</a>
            </nav>

            {/* Right: actions */}
            <div className="hidden md:flex items-center gap-3">
              <a href="#login" className="px-3 py-2 text-sm font-medium text-slate-700 hover:text-brand transition-colors">Log in</a>
              <a href="#signup" className="px-3 py-2 text-sm font-medium text-white bg-brand hover:bg-brand/90 rounded-md transition-colors">Sign up</a>
              {/* User avatar placeholder */}
              <button className="ml-1 inline-flex h-9 w-9 items-center justify-center rounded-full ring-1 ring-slate-200 hover:ring-brand/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand">
                <span className="sr-only">User menu</span>
                <img alt="avatar" src="https://api.dicebear.com/7.x/initials/svg?seed=BR" className="h-8 w-8 rounded-full" />
              </button>
            </div>

            {/* Mobile hamburger */}
            <button 
              onClick={openDrawer}
              className="md:hidden inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 text-slate-700 hover:text-brand hover:border-brand/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand" 
              aria-label="Open menu"
            >
              <HiMenu className="h-5 w-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Mobile drawer and overlay */}
      {isDrawerOpen && (
        <>
          <div className="fixed inset-0 z-40 bg-slate-900/40" onClick={closeDrawer}></div>
          <aside className="fixed inset-y-0 left-0 z-50 w-72 bg-white shadow-xl">
            <div className="h-16 flex items-center justify-between px-4 border-b">
              <div className="flex items-center gap-2">
                <span aria-hidden className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-brand/10 text-brand">
                  <HiHome className="h-5 w-5" />
                </span>
                <span className="font-semibold">BlueEstate</span>
              </div>
              <button 
                onClick={closeDrawer}
                className="inline-flex h-9 w-9 items-center justify-center rounded-md hover:bg-slate-100 focus:outline-none" 
                aria-label="Close menu"
              >
                <HiX className="h-5 w-5" />
              </button>
            </div>
            <nav className="px-4 py-4 space-y-1" aria-label="Mobile">
              <a href="#guide" className="block rounded-md px-3 py-2 text-slate-700 hover:bg-slate-100 hover:text-brand">Rental Guide</a>
              <a href="#docs" className="block rounded-md px-3 py-2 text-slate-700 hover:bg-slate-100 hover:text-brand">Document Preparation</a>
              <div className="my-3 h-px bg-slate-200"></div>
              <a href="#login" className="block rounded-md px-3 py-2 text-slate-700 hover:bg-slate-100 hover:text-brand">Log in</a>
              <a href="#signup" className="block rounded-md px-3 py-2 text-white bg-brand hover:bg-brand/90">Sign up</a>
            </nav>
          </aside>
        </>
      )}
    </>
  )
}
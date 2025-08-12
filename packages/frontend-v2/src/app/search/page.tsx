import Header from '@/components/Header'
import Footer from '@/components/Footer'
import PropertyCard from '@/components/PropertyCard'
import { HiSearch } from 'react-icons/hi'
import Link from 'next/link'
import { Suspense } from 'react'
import { Metadata } from 'next'
import SearchBar from '@/components/SearchBar'
import FilterModal from '@/components/FilterModal'

export const metadata: Metadata = {
  title: 'Search — BlueEstate Rentals',
}

type SearchParams = {
  q?: string
  page?: string
}

// Simple mock dataset
const MOCK_PROPERTIES = Array.from({ length: 42 }).map((_, idx) => ({
  id: idx + 1,
  title: `Modern Apartment #${idx + 1}`,
  location: idx % 2 === 0 ? 'Sydney CBD' : 'Kensington',
  price: 1200 + (idx % 7) * 100,
  description: 'Near campus · Furnished · Great transport',
  imageUrl: `https://images.unsplash.com/photo-15${(idx % 90)
    .toString()
    .padStart(2, '0')}691938895-1758d7feb511?q=80&w=1600&auto=format&fit=crop`,
}))

function filterAndPaginate(list: typeof MOCK_PROPERTIES, q: string, page: number, pageSize = 12) {
  const filtered = q
    ? list.filter(item =>
        [item.title, item.location, item.description]
          .join(' ')
          .toLowerCase()
          .includes(q.toLowerCase())
      )
    : list

  const total = filtered.length
  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const currentPage = Math.min(Math.max(1, page), totalPages)
  const start = (currentPage - 1) * pageSize
  const pageItems = filtered.slice(start, start + pageSize)

  return { items: pageItems, total, totalPages, currentPage }
}

export default async function SearchPage({ searchParams }: { searchParams: Promise<SearchParams> }) {
  const params = await searchParams
  const q = typeof params.q === 'string' ? params.q : ''
  const page = Number(params.page ?? '1') || 1

  const { items, total, totalPages, currentPage } = filterAndPaginate(MOCK_PROPERTIES, q, page)

  return (
    <>
      <Header />
      <main>
        {/* Head bar already provided by Header. Below it, the search bar aligned to container width */}
        <section className="py-4">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <SearchBar initialQuery={q} />
          </div>
        </section>

        {/* Results area */}
        <section className="pb-12 md:pb-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
              {/* Left: stats/info */}
              <aside className="lg:col-span-3">
                <StatsPanel total={total} query={q} />
              </aside>

              {/* Right: pagination + results */}
              <div className="lg:col-span-9">
                <h2 id="results-heading" tabIndex={-1} className="sr-only">Search results</h2>
                <div className="flex items-center justify-between">
                  <Pagination current={currentPage} totalPages={totalPages} q={q} />
                </div>

                <Suspense fallback={<ResultsSkeleton />}> 
                  {items.length === 0 ? (
                    <EmptyState query={q} />
                  ) : (
                    <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                      {items.map(item => (
                        <PropertyCard
                          key={item.id}
                          title={item.title}
                          location={item.location}
                          price={item.price}
                          description={item.description}
                          imageUrl={item.imageUrl}
                        />
                      ))}
                    </div>
                  )}
                </Suspense>

                <div className="mt-6">
                  <Pagination current={currentPage} totalPages={totalPages} q={q} />
                </div>
              </div>
            </div>
          </div>
        </section>
        <FilterModal />
      </main>
      <Footer />
    </>
  )
}

function StatsPanel({ total, query }: { total: number; query: string }) {
  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="text-sm text-slate-500">Total results</div>
        <div className="mt-1 text-2xl font-semibold text-slate-900">{total}</div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="text-sm text-slate-500">Filters summary</div>
        <p className="mt-1 text-sm text-slate-700">
          {query ? (
            <>Search for “{query}”. More filters coming soon.</>
          ) : (
            <>No keywords. Try filtering by location or type.</>
          )}
        </p>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="text-sm font-medium text-slate-800">Tips</div>
        <ul className="mt-2 list-disc pl-5 text-sm text-slate-600 space-y-1">
          <li>Use city, suburb, or property type keywords</li>
          <li>Sort and more filters will be available soon</li>
        </ul>
      </div>
    </div>
  )
}

function Pagination({ current, totalPages, q }: { current: number; totalPages: number; q: string }) {
  const prevPage = Math.max(1, current - 1)
  const nextPage = Math.min(totalPages, current + 1)

  const makeHref = (pageNum: number) => {
    const params = new URLSearchParams()
    if (q) params.set('q', q)
    params.set('page', String(pageNum))
    return `/search?${params.toString()}`
  }

  return (
    <nav className="flex items-center gap-2" aria-label="Pagination">
      <Link
        href={makeHref(prevPage)}
        aria-disabled={current === 1}
        className={`px-3 py-1.5 rounded-md border text-sm ${
          current === 1
            ? 'cursor-not-allowed border-slate-200 text-slate-300'
            : 'border-slate-200 text-slate-700 hover:border-blue-300 hover:text-blue-600'
        }`}
      >
        Prev
      </Link>
      <span className="text-sm text-slate-600">
        Page <span className="font-medium text-slate-900">{current}</span> of {totalPages}
      </span>
      <Link
        href={makeHref(nextPage)}
        aria-disabled={current === totalPages}
        className={`px-3 py-1.5 rounded-md border text-sm ${
          current === totalPages
            ? 'cursor-not-allowed border-slate-200 text-slate-300'
            : 'border-slate-200 text-slate-700 hover:border-blue-300 hover:text-blue-600'
        }`}
      >
        Next
      </Link>
    </nav>
  )
}

function ResultsSkeleton() {
  return (
    <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="animate-pulse overflow-hidden rounded-2xl border border-slate-200 bg-white">
          <div className="aspect-[4/3] bg-slate-200" />
          <div className="p-4 space-y-2">
            <div className="h-4 bg-slate-200 rounded w-2/3" />
            <div className="h-3 bg-slate-200 rounded w-1/2" />
            <div className="h-4 bg-slate-200 rounded w-1/3 mt-3" />
            <div className="h-3 bg-slate-200 rounded w-full" />
            <div className="h-3 bg-slate-200 rounded w-5/6" />
          </div>
        </div>
      ))}
    </div>
  )
}

function EmptyState({ query }: { query: string }) {
  return (
    <div className="mt-10 rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-50 text-blue-600">
        <HiSearch className="h-6 w-6" />
      </div>
      <h3 className="mt-4 text-lg font-semibold text-slate-900">No results</h3>
      <p className="mt-2 text-sm text-slate-600">
        {query ? (
          <>We couldn’t find any results for “{query}”. Try different keywords.</>
        ) : (
          <>Try entering a location or property type in the search bar.</>
        )}
      </p>
      <div className="mt-6">
        <Link
          href="/"
          className="inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:border-blue-300 hover:text-blue-600"
        >
          Go to homepage
        </Link>
      </div>
    </div>
  )
}



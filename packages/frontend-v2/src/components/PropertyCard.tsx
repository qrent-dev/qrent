interface PropertyCardProps {
  title: string
  location: string
  price: number
  description: string
  imageUrl: string
}

export default function PropertyCard({ title, location, price, description, imageUrl }: PropertyCardProps) {
  return (
    <article className="group overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-card">
      <figure className="relative aspect-[4/3] overflow-hidden">
        {/* Keep <img> for remote demo images to avoid domain config. When moving to production, switch to next/image with loader or domain allowlist. */}
        <img 
          className="h-full w-full object-cover transition duration-300 group-hover:scale-105" 
          src={imageUrl} 
          alt={title}
          loading="lazy"
        />
        <figcaption className="sr-only">{title}</figcaption>
      </figure>
      <div className="p-4">
        <h3 className="text-base font-semibold text-slate-900">{title}</h3>
        <p className="mt-1 text-sm text-slate-500">{location}</p>
        <p className="mt-3 text-brand font-semibold text-lg">
          ${price.toLocaleString()}
          <span className="text-sm text-slate-500 font-normal">/month</span>
        </p>
        <p className="mt-2 text-sm text-slate-600">{description}</p>
      </div>
    </article>
  )
}



import Header from '@/components/Header'
import HeroSection from '@/components/HeroSection'
import UsefulGuide from '@/components/UsefulGuide'
import PropertyGrid from '@/components/PropertyGrid'
import Footer from '@/components/Footer'

export default function Home() {
  return (
    <>
      <Header />
      <main>
        <HeroSection />
        <UsefulGuide />
        <PropertyGrid />
      </main>
      <Footer />
    </>
  )
}
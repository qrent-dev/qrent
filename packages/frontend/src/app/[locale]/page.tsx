'use client';
import Search from '@/src/components/Search';
import HeroButton from '@/src/components/HeroButton';
import JustLanded from '@/src/components/JustLanded';
import DeviceWarning from '@/src/components/DeviceWarning';

export default function HomePage() {
  return (
    <main>
      <DeviceWarning />
      <Search />
      <HeroButton />
      <JustLanded />
    </main>
  );
}

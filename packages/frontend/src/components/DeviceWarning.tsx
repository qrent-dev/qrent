import { useEffect, useState } from 'react';
import { useTranslations } from 'use-intl';

function DeviceWarning() {
  const t = useTranslations('DeviceWarning');
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkIsMobile = () => {
      const userAgent = navigator.userAgent.toLowerCase();
      const isPhone = /iphone|ipod|android.*mobile|windows phone/.test(userAgent);
      setIsMobile(isPhone || window.innerWidth < 768);
    };

    checkIsMobile();
    window.addEventListener('resize', checkIsMobile); // handle screen rotation

    return () => window.removeEventListener('resize', checkIsMobile);
  }, []);

  if (!isMobile) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        padding: '12px',
        backgroundColor: '#ffcccc',
        color: '#333',
        textAlign: 'center',
        zIndex: 1000,
      }}
    >
      ⚠️ {t('warning')}
    </div>
  );
}

export default DeviceWarning;

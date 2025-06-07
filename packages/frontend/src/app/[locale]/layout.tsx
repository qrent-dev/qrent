import FooterHandler from '@/src/components/FooterHandler';
import NavBar from '@/src/components/NavBar';
import { routing } from '@/src/i18n/routing';
import { NextIntlClientProvider, hasLocale } from 'next-intl';
import { notFound } from 'next/navigation';
import Script from 'next/script';

// Layout component for locale-based routing
export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  // Ensure that the incoming `locale` is valid
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) {
    notFound();
  }

  return (
    <html lang={locale} className="bg-white">
      <head>
        <Script
          strategy="afterInteractive"
          src={`https://www.googletagmanager.com/gtag/js?id=G-LVXN1Q8W0X`}
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-LVXN1Q8W0X');
          `}
        </Script>
        <Script
          id="clarity-analytics"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              (function(c,l,a,r,i,t,y){
                  c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
                  t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
                  y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
              })(window, document, "clarity", "script", "r5zysdcmja");
            `,
          }}
        />
        {/* Dify Chatbot Configuration */}
        <Script id="dify-chatbot-config" strategy="afterInteractive">
          {`
            window.difyChatbotConfig = {
              token: 'Pk5JLyWtauKU4b1H',
              systemVariables: {
                // user_id: 'YOU CAN DEFINE USER ID HERE',
                // conversation_id: 'YOU CAN DEFINE CONVERSATION ID HERE, IT MUST BE A VALID UUID',
              },
            }
          `}
        </Script>
        <Script
          src="https://udify.app/embed.min.js"
          id="Pk5JLyWtauKU4b1H"
          strategy="afterInteractive"
        />
        {/* Dify Chatbot Custom Styles */}
        <style dangerouslySetInnerHTML={{
          __html: `
            #dify-chatbot-bubble-button {
              background-color: #1C64F2 !important;
            }
            #dify-chatbot-bubble-window {
              width: 24rem !important;
              height: 40rem !important;
            }
          `
        }}></style>
      </head>
      <body>
        <NextIntlClientProvider>
          <NavBar />
          {children}
          <FooterHandler />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}

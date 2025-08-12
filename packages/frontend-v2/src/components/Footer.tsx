import { SiXiaohongshu, SiGithub } from 'react-icons/si'
import { MdEmail } from 'react-icons/md'

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <nav aria-label="Footer navigation">
            <ul className="space-y-2 text-slate-700">
              <li>
                <a href="#about" className="hover:text-blue-600 transition-colors">About</a>
              </li>
              <li>
                <a href="#team" className="hover:text-blue-600 transition-colors">Meet our team</a>
              </li>
              <li>
                <a href="#contact" className="hover:text-blue-600 transition-colors">Get in touch</a>
              </li>
            </ul>
          </nav>

          <div className="flex items-start sm:items-center gap-4">
            <a
              href="https://www.xiaohongshu.com/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Xiaohongshu"
              className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 text-slate-700 hover:text-white hover:bg-red-500 hover:border-red-500 transition"
            >
              <SiXiaohongshu className="h-5 w-5" />
            </a>
            <a
              href="https://github.com/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="GitHub"
              className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 text-slate-700 hover:text-white hover:bg-slate-900 hover:border-slate-900 transition"
            >
              <SiGithub className="h-5 w-5" />
            </a>
            <a
              href="mailto:hello@qrent.com"
              aria-label="Email"
              className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 text-slate-700 hover:text-white hover:bg-blue-600 hover:border-blue-600 transition"
            >
              <MdEmail className="h-5 w-5" />
            </a>
          </div>

          <div className="lg:col-span-1 text-sm text-slate-500">
            <p>Copyright © 2025 - All right reserved by Qrent Industries Ltd</p>
            <p className="mt-2">网页备案号: 粤ICP备2025363367号-1</p>
          </div>
        </div>
      </div>
    </footer>
  )
}

'use client';
import React, { useState } from 'react';
import { Label } from '@/src/components/label';
import { Input } from '@/src/components/input';
import { cn } from '@/src/lib/utils';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { Alert } from '@heroui/react';
import { useRouter } from 'next/navigation';
import { useUserStore } from '../../../store/userInfoStore';

const Login = () => {
  const t = useTranslations('Login');
  const { setUser } = useUserStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState('');

  const [isSuccVisible, setisSuccVisible] = useState(false);
  const succTitle = t('succ-title');
  const succDes = '';

  const [isFailVisible, setisFailVisible] = useState(false);
  const failTitle = t('fail-title');
  const failDes = t('fail-des');

  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        throw new Error('Login failed');
      }

      const token = await res.json();
      setToken(token);

      console.log('Login successful');
      setUser({
        name: email.slice(0, 4),
        email: email,
        token: token,
      });

      setisSuccVisible(true);

      setTimeout(() => {
        router.push('/');
      }, 1000);
    } catch (err) {
      console.log(err);
      setisFailVisible(true);
    }
  };

  return (
    <div className="max-w-md w-full mx-auto rounded-none md:rounded-2xl p-4 md:p-8 shadow-input bg-white dark:bg-white font-serif font-bold">
      <h2 className="font-bold text-3xl text-blue-primary ">{t('welcome')}</h2>
      <p className="text-black text-sm max-w-sm mt-2 ">{t('login-to-continue')}</p>

      <form className="my-8" onSubmit={handleSubmit}>
        <LabelInputContainer className="mb-4">
          <Label htmlFor="email">{t('email-address')}</Label>
          <Input
            id="email"
            placeholder="projectmayhem@fc.com"
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
          />
        </LabelInputContainer>

        <LabelInputContainer className="mb-4">
          <Label htmlFor="password">{t('pwd')}</Label>
          <Input
            id="password"
            placeholder="••••••••"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
          />
        </LabelInputContainer>

        <button
          className="bg-morandi-blue text-white rounded-md h-10 w-full font-medium shadow-inner hover:brightness-110 transition"
          type="submit"
        >
          {t('login')} &rarr;
          <BottomGradient />
        </button>

        <div className="bg-gradient-to-r from-transparent via-neutral-300  to-transparent my-8 h-[1px] w-full" />
        <div className="flex justify-center items-center gap-2 py-1">
          <p className="text-gray-600">{t('dont-have-acc')}</p>
          <Link href="/signup" className="text-blue-primary font-semibold hover:underline">
            {t('sign-up')}
          </Link>
        </div>
      </form>

      <div className="flex flex-col gap-4">
        {isSuccVisible && (
          <Alert
            color="success"
            description={<>{succDes}</>}
            isVisible={isSuccVisible}
            title={succTitle}
            variant="faded"
            onClose={() => setisSuccVisible(false)}
          />
        )}
        {isFailVisible && (
          <Alert
            color="warning"
            description={<>{failDes}</>}
            isVisible={isFailVisible}
            title={failTitle}
            variant="faded"
            onClose={() => setisFailVisible(false)}
          />
        )}
      </div>
    </div>
  );
};

export default Login;

const BottomGradient = () => {
  return (
    <>
      <span className="group-hover/btn:opacity-100 block transition duration-500 opacity-0 absolute h-px w-full -bottom-px inset-x-0 bg-gradient-to-r from-transparent via-cyan-500 to-transparent" />
      <span className="group-hover/btn:opacity-100 blur-sm block transition duration-500 opacity-0 absolute h-px w-1/2 mx-auto -bottom-px inset-x-10 bg-gradient-to-r from-transparent via-indigo-500 to-transparent" />
    </>
  );
};

const LabelInputContainer = ({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) => {
  return <div className={cn('flex flex-col space-y-2 w-full bg-white', className)}>{children}</div>;
};

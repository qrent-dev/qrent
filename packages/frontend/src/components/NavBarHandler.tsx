'use client';
import React from 'react';
import NavBar from './NavBar';
import { usePathname } from 'next/navigation';
import NavBarForEfficiencyFilter from './NavBarForEfficiencyFilter';
import NavBarForJustLanded from './NavBarForJustLanded';

const NavBarHandler = () => {
  const pathname = usePathname();

  let navBar;
  if (pathname?.endsWith('/findAHome')) {
    navBar = <NavBarForEfficiencyFilter />;
  } else if (pathname?.endsWith('/justLanded')) {
    navBar = <NavBarForJustLanded />;
  } else {
    navBar = <NavBar />;
  }
  return <>{navBar}</>;
};

export default NavBarHandler;

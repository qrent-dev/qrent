import { PrismaClient } from '@prisma/client';
import * as fs from 'fs';
import * as path from 'path';

const prisma = new PrismaClient();

interface PropertyData {
  addressLine2: string;
  [key: string]: any;
}

function parseAddressLine2(addressLine2: string) {
  const parts = addressLine2.split('-');
  if (parts.length >= 3) {
    const nswIndex = parts.findIndex(part => part.toLowerCase() === 'nsw');
    if (nswIndex > 0 && nswIndex < parts.length - 1) {
      const name = parts.slice(0, nswIndex).join(' ').toLowerCase();
      const state = parts[nswIndex].toUpperCase();
      const postcode = parseInt(parts[nswIndex + 1]);
      
      return {
        name,
        state,
        postcode
      };
    }
  }
  return null;
}

async function seedSchools() {
  console.log('setting...');
  
  await (prisma as any).school.deleteMany();
  
  await prisma.$executeRaw`ALTER TABLE schools AUTO_INCREMENT = 1`;
  
  const schools = [
    { id: 1, name: 'UNSW' },
    { id: 2, name: 'USYD' }
  ];
  
  for (const school of schools) {
    await (prisma as any).school.create({
      data: school
    });
  }
  
  console.log('school complete');
}

async function seedRegions() {
  console.log('region...');
  
  await (prisma as any).region.deleteMany();
  
  await prisma.$executeRaw`ALTER TABLE regions AUTO_INCREMENT = 1`;
  
  const propertyDataPath = path.join(__dirname, '../../scraper/property_data_250623.json');
  const propertyData: PropertyData[] = JSON.parse(fs.readFileSync(propertyDataPath, 'utf8'));
  
  const uniqueRegions = new Map<string, { name: string; state: string; postcode: number }>();
  
  for (const property of propertyData) {
    const regionInfo = parseAddressLine2(property.addressLine2);
    if (regionInfo) {
      const key = `${regionInfo.name}-${regionInfo.state}-${regionInfo.postcode}`;
      if (!uniqueRegions.has(key)) {
        uniqueRegions.set(key, regionInfo);
      }
    }
  }
  
  console.log(`found ${uniqueRegions.size}`);
  
  const regionsArray = Array.from(uniqueRegions.values()).sort((a, b) => a.name.localeCompare(b.name));
  
  for (let i = 0; i < regionsArray.length; i++) {
    const region = regionsArray[i];
    await (prisma as any).region.create({
      data: {
        id: i + 1,
        name: region.name,
        state: region.state,
        postcode: region.postcode
      }
    });
    
    if ((i + 1) % 10 === 0) {
      console.log(`已插入 ${i + 1}/${regionsArray.length} 个区域`);
    }
  }
  
  console.log('finsh');
}

async function main() {
  try {
    console.log('starting databse..');
    
    await seedSchools();
    await seedRegions();
    
    console.log('finsih！');
  } catch (error) {
    console.error('error', error);
    throw error;
  } finally {
    await prisma.$disconnect();
  }
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  });

import { prisma } from '../prisma/client';

async function clearDb() {
  await prisma.user.deleteMany();
  await prisma.userPreference.deleteMany();
  await prisma.property.deleteMany();
}

export { clearDb };
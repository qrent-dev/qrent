import { prisma as p } from '@qrent/shared'; 

const FULL_SUBURB_OPTIONS = {
  unsw: [
    'alexandria',
    'arncliffe',
    'banksia',
    'beaconsfield',
    'botany',
    'brighton-le-sands',
    'bronte',
    'camperdown',
    'chifley',
    'chippendale',
    'clovelly',
    'coogee',
    'darlington',
    'eastgardens',
    'eastlakes',
    'enmore',
    'erskineville',
    'hillsdale',
    'kensington',
    'kingsford',
    'kyeemagh',
    'malabar',
    'maroubra',
    'marrickville',
    'mascot',
    'matraville',
    'newtown',
    'paddington',
    'pagewood',
    'randwick',
    'redfern',
    'rockdale',
    'rosebery',
    'stanmore',
    'sydenham',
    'tempe',
    'turrella',
    'waterloo',
    'waverley',
    'zetland',
    'bondi-junction',
    'centennial-park',
    'la-perouse',
    'little-bay',
    'moore-park',
    'phillip-bay',
    'queens-park',
    'south-coogee',
    'st-peters',
    'wolli-creek',
  ],
  usyd: [
    'abbotsford',
    'alexandria',
    'allawah',
    'annandale',
    'arncliffe',
    'banksia',
    'barangaroo',
    'beaconsfield',
    'bexley',
    'blakehurst',
    'botany',
    'brighton-le-sands',
    'burwood',
    'camperdown',
    'carlton',
    'chippendale',
    'chiswick',
    'concord',
    'croydon',
    'darlinghurst',
    'darlington',
    'earlwood',
    'eastlakes',
    'enfield',
    'enmore',
    'erskineville',
    'glebe',
    'haymarket',
    'hurstville',
    'kensington',
    'kingsgrove',
    'kyeemagh',
    'maroubra',
    'marrickville',
    'mascot',
    'mortlake',
    'narwee',
    'newtown',
    'paddington',
    'pagewood',
    'penshurst',
    'pyrmont',
    'redfern',
    'rockdale',
    'rosebery',
    'stanmore',
    'strathfield',
    'sydenham',
    'sydney',
    'tempe',
    'turrella',
    'ultimo',
    'wareemba',
    'waterloo',
    'woolloomooloo',
    'zetland',
    'bardwell-valley',
    'beverly-hills',
    'breakfast-point',
    'canada-bay',
    'carss-park',
    'centennial-park',
    'clemton-park',
    'connells-point',
    'dawes-point',
    'five-dock',
    'forest-lodge',
    'kyle-bay',
    'millers-point',
    'moore-park',
    'north-strathfield',
    'russell-lea',
    'south-coogee',
    'st-peters',
    'surry-hills',
    'the-rocks',
    'walsh-bay',
    'wolli-creek',
  ],
};

async function seed_school_region() {
  // ... you will write your Prisma Client queries here
  // p.properties.deleteMany({});
  await p.school.deleteMany({});
  // const allProperties = await p.properties.findMany({
  //   select: { id: true }
  // });
  
  // const regions = await p.regions.findMany({
  //   select: { id: true }
  // });

  await p.school.createMany({
    data: [
      {
        name: 'UNSW',
      },
      {
        name: 'USYD',
      }
    ]
  })

  FULL_SUBURB_OPTIONS.unsw.forEach(async suburb => {
    await p.school.update({
      where: {
        name: 'UNSW',
      },
      data: {
        regions: {
          connect: {
            name: suburb
          }
        }
      }
    })
  });

  FULL_SUBURB_OPTIONS.usyd.forEach(async suburb => {
    await p.school.update({
      where: {
        name: 'USYD',
      },
      data: {
        regions: {
          connect: {
            name: suburb
          }
        }
      }
    })
  });
}

async function seed_property_school() {
  await p.propertySchool.deleteMany({});
  const properties = await p.property.findMany({
    include: {
      region: true,
    }
  });

  const schools = await p.school.findMany();

  properties.forEach(async property => {
    for (const school of schools) {
      const schoolName = school.name.toLowerCase();
      const regionName = property.region.name.toLowerCase();
      
      // Check if the region is related to the school
      const isRelated = 
        (schoolName === 'unsw' && FULL_SUBURB_OPTIONS.unsw.includes(regionName)) ||
        (schoolName === 'usyd' && FULL_SUBURB_OPTIONS.usyd.includes(regionName));
      
      if (isRelated) {
        await p.propertySchool.create({
          data: {
            propertyId: property.id,
            schoolId: school.id,
            commuteTime: Math.floor(Math.random() * 180) + 10,
          }
        })
      }
    }
  });
}

async function main() {
  await seed_property_school();
}

main()
  .then(async () => {
    console.log('done');
    await p.$disconnect();
  })
  .catch(async e => {
    console.error(e);
    await p.$disconnect();
    process.exit(1);
  });

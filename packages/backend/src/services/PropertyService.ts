import { Prisma, prisma, User, UserPreference, Property } from '@qrent/shared';
import HttpError from '@/error/HttpError';

class PropertyService {
  /**
   * Subscribe a user to updates for a specific property
   * @param userId - ID of the user
   * @param propertyId - ID of the property to subscribe to
   * @returns Promise resolving to the subscription response
   */
  async subscribeToProperty(userId: number, propertyId: number): Promise<string> {
    try {
      const user = await prisma.user.findUnique({
        where: { id: userId },
        include: { properties: true },
      });

      if (!user) {
        throw new HttpError(400, 'User not found???');
      }
      const property = await prisma.property.findUnique({
        where: { id: propertyId },
      });

      if (!property) {
        throw new HttpError(404, 'Property not found');
      }

      const isSubscribed = user.properties.some(property => property.id === propertyId);
      if (isSubscribed) {
        throw new HttpError(409, 'Already subscribed to this property');
      }

      await prisma.user.update({
        where: { id: userId },
        data: {
          properties: {
            connect: { id: propertyId },
          },
        },
      });

      return `Successfully subscribed to property`;
    } catch (error) {
      if (error instanceof Prisma.PrismaClientKnownRequestError) {
        if (error.code === 'P2002') {
          throw new HttpError(400, 'Subscription already exists');
        }
      }
      throw error;
    }
  }

  /**
   * Get properties based on user preferences with pagination
   * @param preferences - User preferences with pagination parameters
   * @returns Promise resolving to the filtered properties
   */
  async getPropertiesByPreferences(
    preferences: UserPreference & {
      page: number;
      pageSize: number;
      publishedAt?: string;
      orderBy?: Prisma.PropertyOrderByWithRelationInput[];
    }
  ): Promise<{
    properties: Property[];
    propertyCount: number;
    totalProperties: number;
    averageWeeklyPrice: number | null;
    averageCommuteTime: number | null;
  }> {
    const page = preferences.page;
    const pageSize = preferences.pageSize;
    const skip = (page - 1) * pageSize;

    if (page == undefined) {
      throw new HttpError(400, 'Page is required');
    }

    if (pageSize == undefined) {
      throw new HttpError(400, 'Page size is required');
    }

    let orderBy: Prisma.PropertyOrderByWithRelationInput[] = [];

    if (preferences.orderBy) {
      // Check if every key is a valid db column
      for (const obj of preferences.orderBy) {
        for (const key in obj) {
          if (!(key in prisma.property.fields)) {
            throw new HttpError(400, `Invalid orderBy key: ${key}`);
          }

          if (obj[key as keyof typeof obj] !== 'asc' && obj[key as keyof typeof obj] !== 'desc') {
            throw new HttpError(400, `Invalid orderBy value: ${obj[key as keyof typeof obj]}`);
          }
        }
      }
      orderBy = preferences.orderBy;
    }

    const where: Prisma.PropertyWhereInput = {};

    // Price filter
    where.pricePerWeek = {};
    if (preferences.minPrice) {
      where.pricePerWeek.gte = preferences.minPrice;
    }
    if (preferences.maxPrice) {
      where.pricePerWeek.lte = preferences.maxPrice;
    }

    // Bedroom filter
    where.bedroomCount = {};
    if (preferences.minBedrooms) {
      where.bedroomCount.gte = preferences.minBedrooms;
    }
    if (preferences.maxBedrooms) {
      where.bedroomCount.lte = preferences.maxBedrooms;
    }

    // Bathroom filter
    where.bathroomCount = {};
    if (preferences.minBathrooms) {
      where.bathroomCount.gte = preferences.minBathrooms;
    }
    if (preferences.maxBathrooms) {
      where.bathroomCount.lte = preferences.maxBathrooms;
    }

    // Property type filter
    if (preferences.propertyType) {
      where.propertyType = preferences.propertyType;
    }

    // Rating filter
    where.averageScore = {};
    if (preferences.minRating) {
      where.averageScore.gte = preferences.minRating;
    }

    // Commute time filter
    where.commuteTime = {};
    if (preferences.minCommuteTime) {
      where.commuteTime.gte = preferences.minCommuteTime;
    }
    if (preferences.maxCommuteTime) {
      where.commuteTime.lte = preferences.maxCommuteTime;
    }

    // Regions filter
    if (preferences.regions && preferences.regions.length > 0) {
      const regions = preferences.regions.split(' ');
      where.OR = regions.map(region => ({
        addressLine2: {
          startsWith: region,
        },
      }));
    }

    // Published date filter
    if (preferences.publishedAt) {
      where.publishedAt = { gte: new Date(preferences.publishedAt) };
    }

    // Get properties that match the filter
    const properties = await prisma.property.findMany({
      where,
      take: pageSize,
      skip,
      orderBy,
    });

    // Total number of properties that match the filter
    const propertyCount = await prisma.property.count({
      where,
    });

    // Total number of properties in the database
    const totalProperties = await prisma.property.count();

    // Average weekly price of properties that match the filter
    const averageWeeklyPrice = await prisma.property.aggregate({
      where,
      _avg: { pricePerWeek: true },
    });

    // Average commute time of properties that match the filter
    const averageCommuteTime = await prisma.property.aggregate({
      where,
      _avg: { commuteTime: true },
    });

    return {
      properties,
      propertyCount,
      totalProperties,
      averageWeeklyPrice: averageWeeklyPrice._avg.pricePerWeek,
      averageCommuteTime: averageCommuteTime._avg.commuteTime,
    };
  }

  async getRegionSummary(regions: string) {
    const where: Prisma.PropertyWhereInput = {};

    const regionList = regions.split(' ');
    where.OR = regionList.map(region => ({
      addressLine2: {
        startsWith: region,
      },
    }));

    const summaries = await prisma.property.groupBy({
      by: ['addressLine2'],
      where,
      _count: true,
      _avg: { pricePerWeek: true, commuteTime: true, averageScore: true },
      orderBy: {
        _count: {
          id: 'desc',
        },
      },
      take: 5,
    });

    const totalProperties = summaries.reduce((acc, summary) => acc + summary._count, 0);

    return {
      summaries: summaries.map(summary => ({
        region: summary.addressLine2,
        propertyCount: summary._count,
        averageWeeklyPrice: summary._avg.pricePerWeek,
        averageCommuteTime: summary._avg.commuteTime,
        averageScore: summary._avg.averageScore,
      })),
      totalProperties,
    };
  }
}

export const propertyService = new PropertyService();

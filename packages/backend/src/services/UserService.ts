import { prisma } from '@qrent/shared';

class UserService {
  async getProfile(userId: number) {
    const user = await prisma.user.findUnique({
      where: { id: userId },
    });

    return user;
  }
}

export const userService = new UserService();

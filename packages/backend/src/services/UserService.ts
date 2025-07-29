import { prisma } from '@qrent/shared';
import { EMAIL_PREFERENCE } from '@qrent/shared/enum';

class UserService {
  async getProfile(userId: number) {
    const user = await prisma.user.findUnique({
      include: {
        emailPreferences: true,
      },
      where: { id: userId },
    });

    return user;
  }
}

export const userService = new UserService();

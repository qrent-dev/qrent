import { Prisma, prisma, User } from '@qrent/shared';
import HttpError from '@/error/HttpError';
import { generateToken } from '@/utils/helper';

class AuthService {
  async register(userData: User): Promise<string> {
    if (await prisma.user.findUnique({ where: { email: userData.email } })) {
      throw new HttpError(400, 'Email already exists');
    }

    const user = await prisma.user.create({
      data: userData,
    });

    // Generate JWT token
    const token = generateToken(user.id);

    await prisma.userSession.create({
      data: {
        userId: user.id,
        token,
        expiresAt: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000),
      },
    });

    return token;
  }

  async login(userData: Pick<User, 'email' | 'password'>): Promise<string> {
    const user = await prisma.user.findUnique({
      where: { email: userData.email },
    });

    if (!user) {
      throw new HttpError(400, 'Email not found');
    }
    if (user.password !== userData.password) {
      throw new HttpError(400, 'Invalid password');
    }

    // Generate JWT token
    const token = generateToken(user.id);

    await prisma.userSession.create({
      data: {
        userId: user.id,
        token,
        expiresAt: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000),
      },
    });

    return token;
  }

  async changePassword(userId: number, oldPassword: string, newPassword: string) {
    const user = await prisma.user.findUnique({
      where: { id: userId },
    });

    if (!user) {
      throw new HttpError(400, 'User not found');
    }

    if (user.password !== oldPassword) {
      throw new HttpError(400, 'Invalid old password');
    }

    if (newPassword === oldPassword) {
      throw new HttpError(400, 'New password cannot be the same as the old password');
    }

    await prisma.user.update({
      where: { id: userId },
      data: { password: newPassword },
    });
  }
}
export const authService = new AuthService();

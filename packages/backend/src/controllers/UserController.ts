import { propertyService } from '@/services/PropertyService';
import { userService } from '@/services/UserService';
import { Request, Response, NextFunction } from 'express';

class UserController {
  async fetchPreference(req: Request, res: Response, next: NextFunction) {
    const userId = req.user!.userId;
    const preferences = await propertyService.fetchPreference(userId);
    res.json(preferences);
  }

  async getProfile(req: Request, res: Response, next: NextFunction) {
    const userId = req.user!.userId;
    const profile = await userService.getProfile(userId);
    res.json(profile);
  }
}

export const userController = new UserController();

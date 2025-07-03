import { propertyService } from '@/services/PropertyService';
import { Request, Response, NextFunction } from 'express';

class UserController {
  async fetchPreference(req: Request, res: Response, next: NextFunction) {
    const userId = req.user!.userId;
    const preferences = await propertyService.fetchPreference(userId);
    res.json(preferences);
  }
}

export const userController = new UserController();

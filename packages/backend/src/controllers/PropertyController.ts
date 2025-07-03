import { Request, Response, NextFunction } from 'express';
import { propertyService } from '@/services/PropertyService';
import { Preference } from '@qrent/shared';

export class PropertyController {
  async handleSubscribeProperty(req: Request, res: Response, next: NextFunction) {
    const propertyId = parseInt(req.params.propertyId);
    const userId = req.user!.userId;
    const result = await propertyService.subscribeToProperty(userId, propertyId);

    res.json(result);
  }

  async handleUnsubscribeProperty(req: Request, res: Response, next: NextFunction) {
    const propertyId = parseInt(req.params.propertyId);
    const userId = req.user!.userId;
    const result = await propertyService.unsubscribeFromProperty(userId, propertyId);

    res.json(result);
  }

  async fetchSubscriptions(req: Request, res: Response, next: NextFunction) {
    const userId = req.user!.userId;
    const result = await propertyService.fetchSubscriptions(userId);

    res.json(result);
  }

  async fetchProperty(req: Request, res: Response) {
    const preferences: Preference & { page: number; pageSize: number } = req.body;
    const properties = await propertyService.getPropertiesByPreferences(
      preferences,
      req.user?.userId
    );
    res.json(properties);
  }
}

export const propertyController = new PropertyController();

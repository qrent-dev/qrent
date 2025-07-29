import { catchError } from '@/utils/helper';
import { Router } from 'express';
import { propertyController } from '@/controllers/PropertyController';
import { userController } from '@/controllers/UserController';

const router = Router();

router.get('/subscriptions', catchError(propertyController.fetchSubscriptions));
router.get('/preference', catchError(userController.fetchPreference));
router.get('/profile', catchError(userController.getProfile));

export default router;

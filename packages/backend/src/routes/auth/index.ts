import { authController } from '@/controllers/AuthController';
import { catchError } from '@/utils/helper';
import { Router } from 'express';

const router = Router();

router.post('/register', catchError(authController.register));
router.post('/login', catchError(authController.login));
router.put('/change-password', catchError(authController.changePassword));
router.post('/email/send-verification', catchError(authController.sendVerificationEmail));
router.post('/email/verify', catchError(authController.verifyEmail));

export default router;

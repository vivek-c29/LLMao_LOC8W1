const express = require('express');
const router = express.Router();
const authController = require('../controllers/auth.controller');
const { requireAuth } = require('../middleware/auth.middleware');

router.post('/register-user', authController.registerUser);
router.post('/register-worker', authController.registerWorker);
router.post('/login', authController.login);
router.get('/me', requireAuth, authController.getMe);

module.exports = router;

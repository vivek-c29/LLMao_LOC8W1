const express = require('express');
const router = express.Router();
const adminController = require('../controllers/admin.controller');
const { requireAuth, requireAdmin } = require('../middleware/auth.middleware');

router.get('/users', requireAuth, requireAdmin, adminController.getUsers);
router.get('/workers', requireAuth, requireAdmin, adminController.getWorkers);
router.get('/jobs', requireAuth, requireAdmin, adminController.getJobs);

module.exports = router;

const express = require('express');
const router = express.Router();
const workerController = require('../controllers/worker.controller');
const { requireAuth, requireWorker } = require('../middleware/auth.middleware');

router.get('/', workerController.getWorkers);
router.get('/:id', workerController.getWorkerById);
router.patch('/availability', requireAuth, requireWorker, workerController.updateAvailability);

module.exports = router;

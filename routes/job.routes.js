const express = require('express');
const router = express.Router();
const jobController = require('../controllers/job.controller');
const { requireAuth, requireUser, requireWorker } = require('../middleware/auth.middleware');

router.post('/', requireAuth, requireUser, jobController.createJob);
router.get('/user', requireAuth, requireUser, jobController.getJobsForUser);
router.get('/worker', requireAuth, requireWorker, jobController.getJobsForWorker);
router.get('/worker/my-jobs', requireAuth, requireWorker, jobController.getWorkerMyJobs);
router.post('/:id/quotation', requireAuth, requireWorker, jobController.addQuotation);
router.post('/:id/accept', requireAuth, requireUser, jobController.acceptJob);
router.post('/:id/complete', requireAuth, jobController.completeJob);

module.exports = router;

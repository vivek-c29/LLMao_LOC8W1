const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function createJob(req, res) {
  try {
    const { description, address, latitude, longitude } = req.body;

    if (!description || !address) {
      return res.status(400).json({ error: 'Description and address are required' });
    }

    const lat = latitude ? parseFloat(latitude) : 0;
    const lng = longitude ? parseFloat(longitude) : 0;

    const job = await prisma.job.create({
      data: {
        userId: req.user.id,
        description,
        address,
        latitude: lat,
        longitude: lng,
      },
      include: {
        user: {
          select: {
            id: true,
            name: true,
            phone: true,
            address: true,
            city: true,
          },
        },
      },
    });

    res.status(201).json(job);
  } catch (error) {
    console.error('Create job error:', error);
    res.status(500).json({ error: 'Failed to create job' });
  }
}

async function getJobsForUser(req, res) {
  try {
    const jobs = await prisma.job.findMany({
      where: { userId: req.user.id },
      include: {
        worker: {
          select: {
            id: true,
            name: true,
            phone: true,
          },
        },
        quotations: {
          include: {
            worker: {
              select: {
                id: true,
                name: true,
                phone: true,
                workerProfile: {
                  select: {
                    primarySkill: true,
                    rating: true,
                    experience: true,
                  },
                },
              },
            },
          },
        },
      },
      orderBy: { createdAt: 'desc' },
    });

    res.json(jobs);
  } catch (error) {
    console.error('Get user jobs error:', error);
    res.status(500).json({ error: 'Failed to fetch jobs' });
  }
}

async function getJobsForWorker(req, res) {
  try {
    const { status } = req.query;

    const workerProfile = await prisma.workerProfile.findUnique({
      where: { userId: req.user.id },
    });

    if (!workerProfile) {
      return res.status(404).json({ error: 'Worker profile not found' });
    }

    const where = {
      workerId: null,
      status: 'PENDING',
      ...(status && { status }),
    };

    const jobs = await prisma.job.findMany({
      where,
      include: {
        user: {
          select: {
            id: true,
            name: true,
            phone: true,
            address: true,
            city: true,
          },
        },
        quotations: true,
      },
      orderBy: { createdAt: 'desc' },
    });

    res.json(jobs);
  } catch (error) {
    console.error('Get worker jobs error:', error);
    res.status(500).json({ error: 'Failed to fetch jobs' });
  }
}

async function getWorkerMyJobs(req, res) {
  try {
    const jobs = await prisma.job.findMany({
      where: { workerId: req.user.id },
      include: {
        user: {
          select: {
            id: true,
            name: true,
            phone: true,
            address: true,
            city: true,
          },
        },
      },
      orderBy: { createdAt: 'desc' },
    });

    res.json(jobs);
  } catch (error) {
    console.error('Get worker my jobs error:', error);
    res.status(500).json({ error: 'Failed to fetch jobs' });
  }
}

async function addQuotation(req, res) {
  try {
    const { id } = req.params;
    const { price } = req.body;

    if (!price || isNaN(parseFloat(price))) {
      return res.status(400).json({ error: 'Valid price is required' });
    }

    const job = await prisma.job.findUnique({
      where: { id },
    });

    if (!job) {
      return res.status(404).json({ error: 'Job not found' });
    }

    if (job.status !== 'PENDING') {
      return res.status(400).json({ error: 'Job is no longer accepting quotations' });
    }

    const existingQuotation = await prisma.quotation.findUnique({
      where: {
        jobId_workerId: {
          jobId: id,
          workerId: req.user.id,
        },
      },
    });

    if (existingQuotation) {
      return res.status(400).json({ error: 'You have already submitted a quotation for this job' });
    }

    const quotation = await prisma.quotation.create({
      data: {
        jobId: id,
        workerId: req.user.id,
        price: parseFloat(price),
      },
      select: {
        id: true,
        jobId: true,
        workerId: true,
        price: true,
        status: true,
        createdAt: true,
        job: true,
        worker: {
          select: {
            id: true,
            name: true,
            phone: true,
            workerProfile: {
              select: {
                primarySkill: true,
                rating: true,
              },
            },
          },
        },
      },
    });

    res.status(201).json(quotation);
  } catch (error) {
    console.error('Add quotation error:', error);
    res.status(500).json({ error: error.message || 'Failed to add quotation' });
  }
}

async function acceptJob(req, res) {
  try {
    const { id } = req.params;
    const { workerId, quotationId } = req.body;

    const job = await prisma.job.findUnique({
      where: { id },
      include: { quotations: true },
    });

    if (!job) {
      return res.status(404).json({ error: 'Job not found' });
    }

    if (job.userId !== req.user.id) {
      return res.status(403).json({ error: 'Only the job owner can accept quotations' });
    }

    if (job.status !== 'PENDING') {
      return res.status(400).json({ error: 'Job is no longer pending' });
    }

    const quotation = await prisma.quotation.findFirst({
      where: {
        jobId: id,
        workerId: workerId || undefined,
        id: quotationId || undefined,
      },
    });

    if (!quotation) {
      return res.status(404).json({ error: 'Quotation not found' });
    }

    const [updatedJob] = await prisma.$transaction([
      prisma.job.update({
        where: { id },
        data: {
          workerId: quotation.workerId,
          status: 'ACCEPTED',
          price: quotation.price,
        },
      }),
      prisma.quotation.update({
        where: { id: quotation.id },
        data: { status: 'ACCEPTED' },
      }),
      prisma.quotation.updateMany({
        where: {
          jobId: id,
          id: { not: quotation.id },
        },
        data: { status: 'REJECTED' },
      }),
    ]);

    res.json(updatedJob);
  } catch (error) {
    console.error('Accept job error:', error);
    res.status(500).json({ error: 'Failed to accept job' });
  }
}

async function completeJob(req, res) {
  try {
    const { id } = req.params;

    const job = await prisma.job.findUnique({
      where: { id },
    });

    if (!job) {
      return res.status(404).json({ error: 'Job not found' });
    }

    if (job.userId !== req.user.id && job.workerId !== req.user.id) {
      return res.status(403).json({ error: 'Only job owner or assigned worker can complete' });
    }

    if (job.status !== 'ACCEPTED') {
      return res.status(400).json({ error: 'Only accepted jobs can be completed' });
    }

    const updatedJob = await prisma.$transaction(async (tx) => {
      const jobUpdate = await tx.job.update({
        where: { id },
        data: { status: 'COMPLETED' },
      });

      if (job.workerId) {
        await tx.workerProfile.update({
          where: { userId: job.workerId },
          data: {
            totalJobs: { increment: 1 },
          },
        });
      }

      return jobUpdate;
    });

    res.json(updatedJob);
  } catch (error) {
    console.error('Complete job error:', error);
    res.status(500).json({ error: 'Failed to complete job' });
  }
}

module.exports = {
  createJob,
  getJobsForUser,
  getJobsForWorker,
  getWorkerMyJobs,
  addQuotation,
  acceptJob,
  completeJob,
};

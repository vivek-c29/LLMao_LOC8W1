const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function getUsers(req, res) {
  try {
    const users = await prisma.user.findMany({
      where: { role: 'USER' },
      select: {
        id: true,
        name: true,
        phone: true,
        email: true,
        address: true,
        city: true,
        state: true,
        pincode: true,
        createdAt: true,
      },
      orderBy: { createdAt: 'desc' },
    });

    res.json(users);
  } catch (error) {
    console.error('Get users error:', error);
    res.status(500).json({ error: 'Failed to fetch users' });
  }
}

async function getWorkers(req, res) {
  try {
    const workers = await prisma.user.findMany({
      where: { role: 'WORKER' },
      select: {
        id: true,
        name: true,
        phone: true,
        email: true,
        address: true,
        city: true,
        state: true,
        pincode: true,
        createdAt: true,
        workerProfile: true,
      },
      orderBy: { createdAt: 'desc' },
    });

    res.json(workers);
  } catch (error) {
    console.error('Get workers error:', error);
    res.status(500).json({ error: 'Failed to fetch workers' });
  }
}

async function getJobs(req, res) {
  try {
    const jobs = await prisma.job.findMany({
      include: {
        user: {
          select: {
            id: true,
            name: true,
            phone: true,
          },
        },
        worker: {
          select: {
            id: true,
            name: true,
            phone: true,
          },
        },
      },
      orderBy: { createdAt: 'desc' },
    });

    res.json(jobs);
  } catch (error) {
    console.error('Get jobs error:', error);
    res.status(500).json({ error: 'Failed to fetch jobs' });
  }
}

module.exports = {
  getUsers,
  getWorkers,
  getJobs,
};

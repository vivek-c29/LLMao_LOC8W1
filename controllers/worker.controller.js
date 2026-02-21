const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function getWorkers(req, res) {
  try {
    const { skill, available, city } = req.query;

    const where = {
      role: 'WORKER',
      ...(city && { city: { contains: city } }),
      workerProfile: {
        ...(skill && { primarySkill: { contains: skill } }),
        ...(available !== undefined && { available: available === 'true' }),
      },
    };

    const workers = await prisma.user.findMany({
      where,
      include: {
        workerProfile: true,
      },
      select: {
        id: true,
        name: true,
        phone: true,
        email: true,
        city: true,
        state: true,
        workerProfile: true,
      },
    });

    res.json(workers);
  } catch (error) {
    console.error('Get workers error:', error);
    res.status(500).json({ error: 'Failed to fetch workers' });
  }
}

async function getWorkerById(req, res) {
  try {
    const { id } = req.params;

    const worker = await prisma.user.findFirst({
      where: {
        id,
        role: 'WORKER',
      },
      include: {
        workerProfile: true,
      },
      select: {
        id: true,
        name: true,
        phone: true,
        email: true,
        address: true,
        city: true,
        state: true,
        pincode: true,
        workerProfile: true,
        createdAt: true,
      },
    });

    if (!worker) {
      return res.status(404).json({ error: 'Worker not found' });
    }

    res.json(worker);
  } catch (error) {
    console.error('Get worker error:', error);
    res.status(500).json({ error: 'Failed to fetch worker' });
  }
}

async function updateAvailability(req, res) {
  try {
    const { available } = req.body;

    const workerProfile = await prisma.workerProfile.findUnique({
      where: { userId: req.user.id },
    });

    if (!workerProfile) {
      return res.status(404).json({ error: 'Worker profile not found' });
    }

    const updated = await prisma.workerProfile.update({
      where: { userId: req.user.id },
      data: { available: available ?? true },
    });

    res.json(updated);
  } catch (error) {
    console.error('Update availability error:', error);
    res.status(500).json({ error: 'Failed to update availability' });
  }
}

module.exports = {
  getWorkers,
  getWorkerById,
  updateAvailability,
};

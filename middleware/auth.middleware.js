const { verifyToken } = require('../utils/jwt');
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function requireAuth(req, res, next) {
  const authHeader = req.headers.authorization;
  const token = authHeader?.startsWith('Bearer ') ? authHeader.slice(7) : null;

  if (!token) {
    return res.status(401).json({ error: 'Authentication required' });
  }

  const decoded = verifyToken(token);
  if (!decoded) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }

  const user = await prisma.user.findUnique({
    where: { id: decoded.userId },
    include: { workerProfile: true },
  });

  if (!user) {
    return res.status(401).json({ error: 'User not found' });
  }

  req.user = user;
  next();
}

function requireUser(req, res, next) {
  if (req.user.role !== 'USER') {
    return res.status(403).json({ error: 'Access denied. User role required.' });
  }
  next();
}

function requireWorker(req, res, next) {
  if (req.user.role !== 'WORKER') {
    return res.status(403).json({ error: 'Access denied. Worker role required.' });
  }
  next();
}

function requireAdmin(req, res, next) {
  if (req.user.role !== 'ADMIN') {
    return res.status(403).json({ error: 'Access denied. Admin role required.' });
  }
  next();
}

module.exports = {
  requireAuth,
  requireUser,
  requireWorker,
  requireAdmin,
};

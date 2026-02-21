const { PrismaClient } = require('@prisma/client');
const { hashPassword, comparePassword } = require('../utils/hash');
const { generateToken } = require('../utils/jwt');

const prisma = new PrismaClient();

async function registerUser(req, res) {
  try {
    const { name, phone, email, password, address, city, state, pincode } = req.body;

    if (!name || !phone || !password) {
      return res.status(400).json({ error: 'Name, phone, and password are required' });
    }

    const existingUser = await prisma.user.findFirst({
      where: {
        OR: [{ phone }, ...(email ? [{ email }] : [])],
      },
    });

    if (existingUser) {
      return res.status(400).json({ error: 'Phone or email already registered' });
    }

    const hashedPassword = await hashPassword(password);

    const user = await prisma.user.create({
      data: {
        name,
        phone,
        email: email || null,
        password: hashedPassword,
        role: 'USER',
        address: address || null,
        city: city || null,
        state: state || null,
        pincode: pincode || null,
      },
      select: {
        id: true,
        name: true,
        phone: true,
        email: true,
        role: true,
        address: true,
        city: true,
        state: true,
        pincode: true,
        createdAt: true,
      },
    });

    const token = generateToken({ userId: user.id, role: user.role });

    res.status(201).json({ user, token });
  } catch (error) {
    console.error('Register user error:', error);
    const message = error.message || 'Registration failed';
    res.status(500).json({ error: message });
  }
}

async function registerWorker(req, res) {
  try {
    const {
      name,
      phone,
      email,
      password,
      address,
      city,
      state,
      pincode,
      primarySkill,
      skills,
      experience,
      description,
      serviceRadius,
    } = req.body;

    if (!name || !phone || !password || !primarySkill) {
      return res.status(400).json({ error: 'Name, phone, password, and primary skill are required' });
    }

    const existingUser = await prisma.user.findFirst({
      where: {
        OR: [{ phone }, ...(email ? [{ email }] : [])],
      },
    });

    if (existingUser) {
      return res.status(400).json({ error: 'Phone or email already registered' });
    }

    const hashedPassword = await hashPassword(password);

    const user = await prisma.user.create({
      data: {
        name,
        phone,
        email: email || null,
        password: hashedPassword,
        role: 'WORKER',
        address: address || null,
        city: city || null,
        state: state || null,
        pincode: pincode || null,
        workerProfile: {
          create: {
            primarySkill,
            skills: JSON.stringify(Array.isArray(skills) ? skills : skills ? [skills] : []),
            experience: parseInt(experience) || 0,
            description: description || null,
            serviceRadius: parseInt(serviceRadius) || 10,
          },
        },
      },
      select: {
        id: true,
        name: true,
        phone: true,
        email: true,
        role: true,
        address: true,
        city: true,
        state: true,
        pincode: true,
        createdAt: true,
        workerProfile: {
          select: {
            id: true,
            primarySkill: true,
            skills: true,
            experience: true,
            description: true,
            serviceRadius: true,
            available: true,
          },
        },
      },
    });

    const token = generateToken({ userId: user.id, role: user.role });

    res.status(201).json({ user, token });
  } catch (error) {
    console.error('Register worker error:', error);
    const message = error.message || 'Registration failed';
    res.status(500).json({ error: message });
  }
}

async function login(req, res) {
  try {
    const { phone, password } = req.body;

    if (!phone || !password) {
      return res.status(400).json({ error: 'Phone and password are required' });
    }

    const user = await prisma.user.findUnique({
      where: { phone },
      include: { workerProfile: true },
    });

    if (!user) {
      return res.status(401).json({ error: 'Invalid phone or password' });
    }

    const validPassword = await comparePassword(password, user.password);
    if (!validPassword) {
      return res.status(401).json({ error: 'Invalid phone or password' });
    }

    const token = generateToken({ userId: user.id, role: user.role });

    const { password: _, ...userWithoutPassword } = user;

    res.json({ user: userWithoutPassword, token });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Login failed' });
  }
}

async function getMe(req, res) {
  try {
    const { password: _, ...userWithoutPassword } = req.user;

    res.json(userWithoutPassword);
  } catch (error) {
    console.error('Get me error:', error);
    res.status(500).json({ error: 'Failed to get user' });
  }
}

module.exports = {
  registerUser,
  registerWorker,
  login,
  getMe,
};

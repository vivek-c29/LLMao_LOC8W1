require('dotenv').config();
const express = require('express');
const cors = require('cors');

const authRoutes = require('./routes/auth.routes');
const workerRoutes = require('./routes/worker.routes');
const jobRoutes = require('./routes/job.routes');
const adminRoutes = require('./routes/admin.routes');

const app = express();
const PORT = parseInt(process.env.PORT, 10) || 8000;

const allowedOrigins = [
  'http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002',
  'http://127.0.0.1:3000', 'http://127.0.0.1:3001', 'http://127.0.0.1:3002',
];
app.use(cors({
  origin: (origin, cb) => cb(null, !origin || allowedOrigins.includes(origin)),
  credentials: true,
}));
app.use(express.json());

app.use('/auth', authRoutes);
app.use('/workers', workerRoutes);
app.use('/jobs', jobRoutes);
app.use('/admin', adminRoutes);

app.get('/', (req, res) => {
  res.json({
    message: 'Job Platform API',
    docs: 'API runs on this port. Use the frontend at http://localhost:3000',
    endpoints: { auth: '/auth', jobs: '/jobs', workers: '/workers', admin: '/admin', health: '/health' },
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

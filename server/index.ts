import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import dotenv from 'dotenv';
import { apiRouter } from './routes/api.js';

dotenv.config();

const app = express();
const PORT = process.env.NODE_PORT || 5001;

// Security & Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Routes
app.use('/node-api', apiRouter);

app.get('/', (req, res) => {
  res.json({
    message: 'ANIKA-AI Node/Express Gateway Service is active.',
    version: '1.0.0',
    endpoints: ['/node-api/status', '/node-api/health']
  });
});

app.listen(PORT, () => {
  console.log(`[ANIKA-AI] Node/Express companion server listening on http://localhost:${PORT}`);
});

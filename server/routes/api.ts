import { Router, Request, Response } from 'express';
import { getDatabaseStatus } from '../db.js';

export const apiRouter = Router();

apiRouter.get('/status', (req: Request, res: Response) => {
  const dbStatus = getDatabaseStatus();
  res.json({
    platform: 'ANIKA-AI Companion Server',
    status: 'online',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    database: dbStatus
  });
});

apiRouter.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    uptime: process.uptime(),
    nodeVersion: process.version
  });
});

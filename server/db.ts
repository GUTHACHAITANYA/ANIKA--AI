import path from 'path';
import fs from 'fs';

export interface DatabaseStatus {
  connected: boolean;
  type: string;
  path: string;
  sizeBytes?: number;
}

export const getDatabaseStatus = (): DatabaseStatus => {
  const dbPath = path.resolve(process.cwd(), 'instance', 'anika.db');
  const exists = fs.existsSync(dbPath);
  let sizeBytes = 0;
  if (exists) {
    const stats = fs.statSync(dbPath);
    sizeBytes = stats.size;
  }

  return {
    connected: exists,
    type: 'SQLite3',
    path: dbPath,
    sizeBytes
  };
};

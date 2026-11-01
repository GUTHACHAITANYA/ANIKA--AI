export interface ServiceMetrics {
  serverStart: string;
  platform: string;
}

export const getServiceMetrics = (): ServiceMetrics => {
  return {
    serverStart: new Date().toISOString(),
    platform: 'ANIKA-AI'
  };
};

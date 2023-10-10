/**
 * Configuration for Playwright using default from @jupyterlab/galata
 */
const baseConfig = require('@jupyterlab/galata/lib/playwright-config');

module.exports = {
  ...baseConfig,
  webServer: {
    command: 'jlpm start',
    url: 'http://localhost:8888/lab',
    timeout: 30000,
    reuseExistingServer: !process.env.CI
  },
  retries: process.env.CI ? 2 : 0,
  timeout: 120000,
  use: {
    viewport: { width: 1600, height: 1200 },
    screen: { width: 1600, height: 1200 },
    navigationTimeout: 10000,
    actionTimeout: 10000,
    trace: 'retain-on-failure',
    video: 'retain-on-failure'
  }
};

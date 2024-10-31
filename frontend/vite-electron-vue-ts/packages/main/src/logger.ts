import log from 'electron-log/main';
import util from 'node:util';

export function createLogger() {
  log.initialize();
  log.transports.console.format = ({ data, level, message }) => {
    const text = util.format(...data);
    const logId = message.logId;
    var keyValuePairs: string[] = [];
    if (message.variables) {
      const vars = message.variables;
      const keys = Object.keys(vars);
      keyValuePairs = keys.map(key => `[${key}:${vars[key]}]`);
    }
    return [
      message.date.toISOString(),
      `[${level}]${logId ? logId : ''}`,
      keyValuePairs ? keyValuePairs.join(' ') : '',
      text
    ];
  }
  return log;
};
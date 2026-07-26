
export function createLogger(namespace) {
    return {
        info(message) {
        console.log(`[${namespace}] ${message}`);
        },

        warn(message) {
        console.warn(`[${namespace}] ${message}`);
        },

        error(message) {
        console.error(`[${namespace}] ${message}`);
        },
    }
}
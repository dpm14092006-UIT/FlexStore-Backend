import axios from 'axios';

class PackingService {
    constructor(baseURL = 'http://localhost:8000') {
        this.client = axios.create({
            baseURL,
            headers: {
                'Content-Type': 'application/json',
            },
        });
    }

    /**
     * Send optimization request to Backend
     * @param {Array|Object} bins - List of bins or single bin { width, height, depth }
     * @param {Array} items - List of items { id, name, width, height, depth, color }
     * @returns {Promise<Object>} - { packed_bins, unpacked_items, efficiency }
     */
    async optimize(bins, items) {
        try {
            // Ensure items have all required fields (backend expects 'x', 'y', 'z' to be numbers even if 0)
            const sanitizedItems = items.map(item => ({
                ...item,
                x: item.x || 0,
                y: item.y || 0,
                z: item.z || 0
            }));

            // Handle bins input (single object or array)
            const binsList = Array.isArray(bins) ? bins : [bins];

            const sanitizedBins = binsList.map(bin => ({
                width: Number(bin.width),
                height: Number(bin.height),
                depth: Number(bin.depth)
            }));

            const response = await this.client.post('/optimize', {
                bins: sanitizedBins,
                items: sanitizedItems
            });
            return response.data;
        } catch (error) {
            console.error('PackingService Error:', error);
            throw error;
        }
    }

    async healthCheck() {
        try {
            const response = await this.client.get('/');
            return response.data;
        } catch (error) {
            console.error('Backend Health Check Failed:', error);
            return { status: 'error', message: 'Backend unreachable' };
        }
    }
}

// Singleton instance
export const packingService = new PackingService();

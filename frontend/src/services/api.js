import axios from 'axios';

class FlexStoreClient {
  constructor(baseURL = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Send optimization request
   * @param {Object} bin - { width, height, depth }
   * @param {Array} items - List of items
   * @returns {Promise<Object>} - Response data
   */
  async optimize(bin, items) {
    try {
      const response = await this.client.post('/optimize', {
        bin,
        items
      });
      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }
}

export const apiClient = new FlexStoreClient();
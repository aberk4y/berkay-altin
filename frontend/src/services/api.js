import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const api = {
  // Get prices
  getPrices: async (type = 'all') => {
    try {
      const response = await axios.get(`${API}/prices`, {
        params: { type }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching prices:', error);
      throw error;
    }
  },

  // Portfolio operations
  getPortfolio: async () => {
    try {
      const response = await axios.get(`${API}/portfolio`);
      return response.data;
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      throw error;
    }
  },

  createPortfolioItem: async (item) => {
    try {
      const response = await axios.post(`${API}/portfolio`, item);
      return response.data;
    } catch (error) {
      console.error('Error creating portfolio item:', error);
      throw error;
    }
  },

  updatePortfolioItem: async (id, item) => {
    try {
      const response = await axios.put(`${API}/portfolio/${id}`, item);
      return response.data;
    } catch (error) {
      console.error('Error updating portfolio item:', error);
      throw error;
    }
  },

  deletePortfolioItem: async (id) => {
    try {
      const response = await axios.delete(`${API}/portfolio/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting portfolio item:', error);
      throw error;
    }
  }
};
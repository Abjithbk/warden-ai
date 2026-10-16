import axios from 'axios'

// Base URL points to the FastAPI backend v1 prefix
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000,
})

// Optional interceptor for logging or global error handling
api.interceptors.response.use(
    (response) => response.data,
    (error) => {
        const message = error.response?.data?.detail || error.message || 'Network Error'
        return Promise.reject(new Error(message))
    }
)

// dashboard api endpoints
export const getOverviewStats = () => api.get('/overview/stats')
export const getRecentActions = (limit = 10) => api.get(`/overview/recent-actions?limit=${limit}`)

//incidents api endpoints
export const getIncidents = (params = {}) => api.get('/incidents', { params })
export const getIncidentById = (id) => api.get(`/incidents/${id}`)
export const approveIncident = (id, payload) => api.post(`/incidents/${id}/approve`, payload)
export const rejectIncident = (id, payload) => api.post(`/incidents/${id}/reject`, payload)

//audit log endpoints
export const getAuditLogs = (params = {}) => api.get('/audit', { params })

export default api

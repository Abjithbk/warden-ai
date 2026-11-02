import axios from 'axios'

// Base URL points to the FastAPI backend v1 prefix
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'

export class ApiError extends Error {
    constructor(message, status) {
        super(message)
        this.name = 'ApiError'
        this.status = status
    }
}

function extractMessage(error) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) return detail.map((d) => d.msg).join(', ')
    return error.message || 'Network Error'
}



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
    (error) =>
        Promise.reject(
            axios.isCancel(error)
                ? error : new ApiError(extractMessage(error), error.response?.status ?? null),
        ),
)

// dashboard api endpoints
export const getOverviewStats = (signal) => api.get('/overview/stats', { signal })
export const getRecentActions = (limit = 10, signal) => api.get('/overview/recent-actions', { params: { limit }, signal })

//incidents api endpoints
export const getIncidents = (params = {}, signal) => api.get('/incidents', { params, signal })
export const getIncidentById = (id, signal) => api.get(`/incidents/${id}`, { signal })
export const approveIncident = (id, payload) => api.post(`/incidents/${id}/approve`, payload)
export const rejectIncident = (id, payload) => api.post(`/incidents/${id}/reject`, payload)
//slack endpoints
export const getSlackStatus = (signal) => api.get('/slack/status', { signal })
export const sendSlackTest = () => api.post('/slack/test')
export const notifySlack = (incidentId, force = false) =>
    api.post(`/slack/notify/${incidentId}`, null, { params: { force } })
//audit log endpoints
export const getAuditLogs = (params = {}, signal) => api.get('/audit', { params, signal })

export const auditExportUrl = (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return `${API_BASE_URL}/audit/export${qs ? '?' + qs : ''}`
}

export default api
